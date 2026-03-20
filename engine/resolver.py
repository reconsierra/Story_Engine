
"""Story Engine Resolver

Deterministic resolution order:
  1) Engine baseline defaults
  2) Genre defaults
  3) Story-type modifiers (optional)
  4) Preset overrides
  5) User overrides
  6) Dependency corrections (guardrails)

The resolver returns:
  - resolved: dict[path -> value]
  - warnings: list[str]

Notes:
  - No randomness is applied.
  - If a value is invalid (not in allowed list), it is replaced with the baseline value and a warning is recorded.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _flatten_schema(schema: dict) -> Dict[str, List[str]]:
    allowed_map: Dict[str, List[str]] = {}

    def walk(node: Any, prefix: str = ""):
        if isinstance(node, dict):
            # variable leaf
            if 'allowed' in node and 'value' in node and isinstance(node['allowed'], list):
                allowed_map[prefix] = node['allowed']
                return
            for k, v in node.items():
                if k == 'meta':
                    continue
                new_prefix = f"{prefix}.{k}" if prefix else k
                walk(v, new_prefix)

    walk(schema)
    return allowed_map


def resolve(
    config: dict,
    repo_root: str | Path,
    schema_path: str = 'schemas/book_schema.json',
    engine_defaults_path: str = 'engine/engine_defaults.json',
    dependency_rules_path: str = 'engine/dependency_rules.json',
    story_type_modifiers_path: str = 'engine/story_type_modifiers.json',
) -> Tuple[Dict[str, str], List[str]]:
    """Resolve a config into a complete set of variables."""

    repo_root = Path(repo_root)
    schema = _load_json(repo_root / schema_path)
    allowed_map = _flatten_schema(schema)

    defaults = _load_json(repo_root / engine_defaults_path)
    deps = _load_json(repo_root / dependency_rules_path)
    story_mods = {}
    st_mod_path = repo_root / story_type_modifiers_path
    if st_mod_path.exists():
        story_mods = _load_json(st_mod_path)

    warnings: List[str] = []

    genre = config.get('genre')
    preset_name = config.get('preset', 'engine_default')
    user_overrides = config.get('overrides', {}) or {}

    # 1) baseline
    resolved: Dict[str, str] = dict(defaults.get('baseline', {}))

    # 2) genre defaults
    if genre:
        resolved.update(defaults.get(f'genre:{genre}', {}))
    else:
        warnings.append('No genre provided; using baseline defaults only.')

    # 3) story type modifiers (based on currently resolved or user override)
    story_type = user_overrides.get('story_engine.story_type') or resolved.get('story_engine.story_type')
    if story_type:
        resolved.update(story_mods.get(f'story_type:{story_type}', {}))

    # 4) preset overrides
    preset_path = repo_root / 'presets' / f'{preset_name}.json'
    if preset_path.exists():
        preset = _load_json(preset_path)
        resolved.update(preset.get('overrides', {}) or {})
    else:
        warnings.append(f"Preset '{preset_name}' not found; using engine defaults only.")

    # 5) user overrides
    resolved.update(user_overrides)

    # 6) dependency corrections
    for rule in deps:
        cond = rule.get('if', {})
        if cond and all(resolved.get(k) == v for k, v in cond.items()):
            resolved.update(rule.get('then', {}))

    # Validation against allowed values
    for path, allowed in allowed_map.items():
        if path not in resolved:
            # Fill missing from baseline if possible
            base_val = defaults.get('baseline', {}).get(path)
            if base_val is not None:
                resolved[path] = base_val
            else:
                # As a last resort, pick first allowed deterministically
                resolved[path] = allowed[0]
                warnings.append(f"Missing '{path}'; set to first allowed '{allowed[0]}'.")

        val = resolved.get(path)
        if val not in allowed:
            fallback = defaults.get('baseline', {}).get(path, allowed[0])
            warnings.append(f"Invalid value for '{path}': '{val}'. Replaced with '{fallback}'.")
            resolved[path] = fallback

    return resolved, warnings


def save_preset_from_diff(
    resolved: Dict[str, str],
    genre: str,
    repo_root: str | Path,
    preset_id: str,
    label: str,
    description: str = '',
) -> dict:
    """Create a new preset JSON using only the values that differ from baseline + genre defaults."""
    repo_root = Path(repo_root)
    defaults = _load_json(repo_root / 'engine/engine_defaults.json')

    baseline = dict(defaults.get('baseline', {}))
    baseline.update(defaults.get(f'genre:{genre}', {}))

    overrides = {k: v for k, v in resolved.items() if baseline.get(k) != v}

    return {
        'preset_id': preset_id,
        'label': label,
        'description': description,
        'overrides': overrides
    }
