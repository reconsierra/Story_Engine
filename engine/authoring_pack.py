
from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple


@dataclass
class AuthoringPack:
    brief_md: str
    outline_md: str
    scaffold_md: str
    prompt_md: str


def _pick(resolved: Dict[str, str], key: str, default: str) -> str:
    return resolved.get(key, default)


def _chapter_count_from_turns(turning_points: str) -> int:
    # Simple deterministic mapping
    mapping = {
        "minimal": 12,
        "standard": 18,
        "high_frequency": 24,
    }
    return mapping.get(turning_points, 18)


def _act_split(chapters: int, act_weighting: str) -> Tuple[int, int, int]:
    # Deterministic split for 3 acts
    if act_weighting == "front_loaded":
        a1 = max(5, round(chapters * 0.30))
        a2 = max(6, round(chapters * 0.45))
    elif act_weighting == "back_loaded":
        a1 = max(4, round(chapters * 0.25))
        a2 = max(6, round(chapters * 0.40))
    else:  # mid_heavy
        a1 = max(4, round(chapters * 0.25))
        a2 = max(8, round(chapters * 0.50))

    a3 = max(4, chapters - a1 - a2)
    # normalise in case rounding pushed too far
    while a1 + a2 + a3 != chapters:
        if a1 + a2 + a3 > chapters:
            a2 = max(6, a2 - 1)
        else:
            a3 += 1
    return a1, a2, a3


def build_story_brief_md(resolved: Dict[str, str]) -> str:
    genre = _pick(resolved, "identity.genre", "adventure")
    protagonist = _pick(resolved, "identity.main_character", "traveling_loner")
    secondary = _pick(resolved, "identity.secondary_character", "genius_problem_solver")
    relationship = _pick(resolved, "identity.relationship_main_secondary", "friendly")
    ant_rel = _pick(resolved, "antagonist.relationship_to_protagonist", "old_colleague")
    ant_motive = _pick(resolved, "antagonist.motivation", "financial_bribery")
    story_type = _pick(resolved, "story_engine.story_type", "defeat_antagonist")

    contact = _pick(resolved, "story_engine.contact_types", "threats")
    complications = _pick(resolved, "story_engine.complications", "weather")

    pace_act = _pick(resolved, "pacing_structure.act_weighting", "mid_heavy")
    turns = _pick(resolved, "pacing_structure.turning_points", "standard")
    time_pressure = _pick(resolved, "pressure_and_flow.time_pressure", "soft_deadline")
    recovery = _pick(resolved, "pressure_and_flow.recovery_time", "brief")
    internal_external = _pick(resolved, "information_control.internal_external_ratio", "50_50")

    sentence = _pick(resolved, "tone_and_language.sentence_style", "mixed")
    dialogue = _pick(resolved, "tone_and_language.dialogue_ratio", "balanced")
    moral = _pick(resolved, "tone_and_language.moral_ambiguity", "clear_morality")

    setting = _pick(resolved, "pacing_structure.setting_confinement", "limited_locations")
    travel = _pick(resolved, "pressure_and_flow.travel_compression", "skipped")
    reveals = _pick(resolved, "information_control.reveal_granularity", "incremental_reveals")

    md = []
    md.append("# Story Brief\n\n")
    md.append(f"**Genre:** {genre}\n\n")
    md.append("## Core setup (engine-derived)\n")
    md.append(f"- **Protagonist archetype:** `{protagonist}`\n")
    md.append(f"- **Secondary archetype:** `{secondary}`\n")
    md.append(f"- **Relationship dynamic:** `{relationship}`\n")
    md.append(f"- **Antagonist relationship:** `{ant_rel}`\n")
    md.append(f"- **Antagonist motivation:** `{ant_motive}`\n")
    md.append(f"- **Story type:** `{story_type}`\n\n")

    md.append("## Conflict & pressure\n")
    md.append(f"- **Primary contact type:** `{contact}`\n")
    md.append(f"- **Complication bias:** `{complications}`\n")
    md.append(f"- **Time pressure:** `{time_pressure}`\n")
    md.append(f"- **Recovery time:** `{recovery}`\n\n")

    md.append("## Storytelling choices\n")
    md.append(f"- **Act weighting:** `{pace_act}`\n")
    md.append(f"- **Turning points:** `{turns}`\n")
    md.append(f"- **Reveal style:** `{reveals}`\n")
    md.append(f"- **Internal vs external:** `{internal_external}`\n\n")

    md.append("## Tone guide\n")
    md.append(f"- **Sentence style:** `{sentence}`\n")
    md.append(f"- **Dialogue ratio:** `{dialogue}`\n")
    md.append(f"- **Moral ambiguity:** `{moral}`\n\n")

    md.append("## Setting & movement\n")
    md.append(f"- **Setting confinement:** `{setting}`\n")
    md.append(f"- **Travel/transition handling:** `{travel}`\n\n")

    md.append("## Logline (draft)\n")
    md.append(
        "A highly competent protagonist confronts an old colleague’s corruption-driven scheme "
        "as pressure builds through threats and harsh conditions, forcing morally grey choices.\n"
    )
    md.append("\n---\n")
    md.append("## Use this brief to generate\n")
    md.append("- A chapter outline (goals, obstacles, reveals)\n")
    md.append("- Scene cards (goal / conflict / outcome / hook)\n")
    md.append("- A manuscript scaffold (chapter headings + prompts)\n")

    return "".join(md)


def build_outline_md(resolved: Dict[str, str]) -> str:
    turning_points = _pick(resolved, "pacing_structure.turning_points", "standard")
    act_weighting = _pick(resolved, "pacing_structure.act_weighting", "mid_heavy")

    chapters = _chapter_count_from_turns(turning_points)
    a1, a2, a3 = _act_split(chapters, act_weighting)

    # Deterministic beat labels
    outline = []
    outline.append("# Outline (chapter-by-chapter)\n\n")
    outline.append(f"**Chapters:** {chapters} (derived from turning points = `{turning_points}`)\n\n")
    outline.append("Each chapter should include: **Goal → Conflict → Outcome → Hook**.\n\n")

    def add_chapter(n: int, label: str):
        outline.append(f"## Chapter {n}: {label}\n")
        outline.append("- Goal:\n")
        outline.append("- Conflict:\n")
        outline.append("- Outcome:\n")
        outline.append("- Hook:\n\n")

    # Act 1
    outline.append("## ACT 1 — Setup & commitment\n\n")
    for i in range(1, a1 + 1):
        label = "Disruption / commitment" if i <= 2 else "Early pressure / first reversals"
        add_chapter(i, label)

    # Act 2
    outline.append("## ACT 2 — Pressure, discovery, reversals\n\n")
    for i in range(a1 + 1, a1 + a2 + 1):
        mid = a1 + (a2 // 2)
        if i == mid:
            label = "Midpoint shift (reframe the threat)"
        elif i == a1 + a2:
            label = "Lowest point (loss of leverage)"
        else:
            label = "Escalation / reveal / complication"
        add_chapter(i, label)

    # Act 3
    outline.append("## ACT 3 — Resolution & fallout\n\n")
    for i in range(a1 + a2 + 1, chapters + 1):
        label = "Final approach / confrontation" if i < chapters else "Soft landing / consequences"
        add_chapter(i, label)

    return "".join(outline)


def build_manuscript_scaffold_md(resolved: Dict[str, str]) -> str:
    turning_points = _pick(resolved, "pacing_structure.turning_points", "standard")
    chapters = _chapter_count_from_turns(turning_points)

    prose_rules = [
        f"- Sentence style: {_pick(resolved, 'tone_and_language.sentence_style', 'mixed')}",
        f"- Dialogue ratio: {_pick(resolved, 'tone_and_language.dialogue_ratio', 'balanced')}",
        f"- Internal vs external: {_pick(resolved, 'information_control.internal_external_ratio', '50_50')}",
        f"- Moral ambiguity: {_pick(resolved, 'tone_and_language.moral_ambiguity', 'clear_morality')}",
        f"- Reveal style: {_pick(resolved, 'information_control.reveal_granularity', 'incremental_reveals')}",
        f"- Time pressure: {_pick(resolved, 'pressure_and_flow.time_pressure', 'soft_deadline')}",
        f"- Recovery time: {_pick(resolved, 'pressure_and_flow.recovery_time', 'brief')}",
    ]

    md = []
    md.append("# Manuscript Scaffold\n\n")
    md.append("*(This is a write-ready skeleton. Replace the prompts with prose.)*\n\n")
    md.append("## Prose & continuity rules\n")
    md.extend([f"{r}\n" for r in prose_rules])
    md.append("\n---\n\n")

    md.append("# Title\n\n(Working title here)\n\n---\n\n")

    for n in range(1, chapters + 1):
        md.append(f"## Chapter {n}\n\n")
        md.append("**Scene goal:** \n\n")
        md.append("**Conflict/obstacle:** \n\n")
        md.append("**Outcome (what changes?):** \n\n")
        md.append("**Hook (why turn the page?):** \n\n")
        md.append("### Draft prose\n\n")
        md.append("*(Write the chapter here. Keep it consistent with the rules above.)*\n\n")
        md.append("---\n\n")

    return "".join(md)


def build_authoring_prompt_md(brief_md: str, outline_md: str, resolved: Dict[str, str]) -> str:
    # Generic prompt you can paste into an AI authoring tool.
    # Keeps instructions clear and repeatable.
    word_target = 60000  # default; you can change later
    md = []
    md.append("# Authoring Prompt (copy/paste)\n\n")
    md.append("## Role\n")
    md.append("You are a fiction author writing a complete first draft from the provided Story Brief and Outline.\n\n")
    md.append("## Output format\n")
    md.append("- Output a complete manuscript in Markdown.\n")
    md.append("- Use `## Chapter N` headings for chapters.\n")
    md.append("- No commentary, no analysis — manuscript only.\n\n")
    md.append("## Draft constraints\n")
    md.append(f"- Target length: approx {word_target} words.\n")
    md.append(f"- POV count: {resolved.get('viewpoint.pov_count', 'single')}.\n")
    md.append(f"- Turning points: {resolved.get('pacing_structure.turning_points', 'standard')}.\n")
    md.append(f"- Reveal style: {resolved.get('information_control.reveal_granularity', 'incremental_reveals')}.\n")
    md.append(f"- Moral ambiguity: {resolved.get('tone_and_language.moral_ambiguity', 'clear_morality')}.\n\n")
    md.append("## Story Brief\n")
    md.append(brief_md)
    md.append("\n\n## Outline\n")
    md.append(outline_md)
    md.append("\n\n## Writing instructions\n")
    md.append("- Follow the outline chapter-by-chapter.\n")
    md.append("- Every chapter must end with a hook.\n")
    md.append("- Keep continuity tight (names, motivations, cause/effect).\n")
    md.append("- Avoid filler travel; cut to scenes with consequences.\n")

    return "".join(md)


def build_authoring_pack(resolved: Dict[str, str], preset: str = "engine_default") -> AuthoringPack:
    brief_md = build_story_brief_md(resolved)
    outline_md = build_outline_md(resolved)
    scaffold_md = build_manuscript_scaffold_md(resolved)
    prompt_md = build_authoring_prompt_md(brief_md, outline_md, resolved)

    return AuthoringPack(
        brief_md=brief_md,
        outline_md=outline_md,
        scaffold_md=scaffold_md,
        prompt_md=prompt_md,
    )


def pack_to_zip_bytes(pack: AuthoringPack, resolved: Dict[str, str]) -> bytes:
    now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    genre = resolved.get("identity.genre", "genre")
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{now}_story_brief_{genre}.md", pack.brief_md)
        z.writestr(f"{now}_outline_{genre}.md", pack.outline_md)
        z.writestr(f"{now}_manuscript_scaffold_{genre}.md", pack.scaffold_md)
        z.writestr(f"{now}_authoring_prompt_{genre}.md", pack.prompt_md)
        z.writestr(f"{now}_resolved_config_{genre}.json", json.dumps(resolved, indent=2))

    return buf.getvalue()
