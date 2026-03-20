
import json
from pathlib import Path

import streamlit as st

from engine.brief_generator import generate_story_brief

from engine.authoring_pack import build_authoring_pack, pack_to_zip_bytes

from engine.resolver import resolve, save_preset_from_diff

REPO_ROOT = Path(__file__).parent
AUTO = "Auto (engine default)"


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text(encoding="utf-8"))


def flatten_schema(schema: dict):
    """
    Return list of (group, path, allowed) for UI generation.
    Leaf nodes are detected by presence of keys: 'allowed' and 'value'.
    """
    rows = []

    def walk(node, prefix="", group=""):
        if isinstance(node, dict):
            # Leaf node: variable definition
            if "allowed" in node and "value" in node and isinstance(node["allowed"], list):
                rows.append((group, prefix, node["allowed"]))
                return

            for k, v in node.items():
                if k == "meta":
                    continue
                new_prefix = f"{prefix}.{k}" if prefix else k
                new_group = group or (prefix.split(".")[0] if prefix else k)
                walk(v, new_prefix, new_group)

    walk(schema)
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


# ---------- UI ----------
st.set_page_config(page_title="Story Engine", layout="wide")
st.title("Story Engine – presets + overrides")
st.caption("Defaults are deterministic and genre-aware. Nothing is random unless you add it later.")

schema = load_json("schemas/book_schema.json")

# Top controls
c1, c2, c3 = st.columns([1, 1, 2])

with c1:
    genre = st.selectbox("Genre", schema["identity"]["genre"]["allowed"], index=0)

with c2:
    preset_files = sorted([p.stem for p in (REPO_ROOT / "presets").glob("*.json")])
    default_index = preset_files.index("engine_default") if "engine_default" in preset_files else 0
    preset = st.selectbox("Preset pack", preset_files, index=default_index)

with c3:
    st.markdown("**How it resolves:** User override → preset → engine defaults → dependency guardrails")

st.divider()

# Build override UI from schema
schema_rows = flatten_schema(schema)

st.subheader("Overrides (optional)")
st.write("Leave any variable on **Auto** unless you want to force it. You can override one variable or many.")

# Group variables for sidebar display
groups = {}
for group_name, path, allowed in schema_rows:
    groups.setdefault(group_name, []).append((path, allowed))

overrides = {}

st.sidebar.header("Overrides")
st.sidebar.caption("Tip: Start by changing one variable only.")

# Render dropdowns per group
for group_name in sorted(groups.keys()):
    expanded_by_default = group_name in ["identity", "pacing_structure"]
    with st.sidebar.expander(group_name, expanded=expanded_by_default):
        for path, allowed in groups[group_name]:
            # Genre already selected in the main UI
            if path == "identity.genre":
                continue

            label = path.replace("_", " ").replace(".", " → ")
            choice = st.selectbox(label, [AUTO] + allowed, key=path)

            if choice != AUTO:
                overrides[path] = choice

# Resolve using engine rules
config = {"genre": genre, "preset": preset, "overrides": overrides}
resolved, warnings = resolve(config=config, repo_root=REPO_ROOT)

st.subheader("Resolved values")

if warnings:
    st.warning("\n".join(warnings))

st.code(json.dumps(resolved, indent=2), language="json")

st.download_button(
    "Download resolved JSON",
    data=json.dumps(resolved, indent=2).encode("utf-8"),
    file_name=f"resolved_{genre}_{preset}.json",
    mime="application/json",
)

st.divider()
st.subheader("Authoring pack (brief → outline → manuscript scaffold)")

pack = build_authoring_pack(resolved=resolved, preset=preset)

st.markdown("### Story brief preview")
st.markdown(pack.brief_md)

with st.expander("Outline preview", expanded=False):
    st.markdown(pack.outline_md)

with st.expander("Manuscript scaffold preview", expanded=False):
    st.markdown(pack.scaffold_md)

with st.expander("Authoring prompt (copy/paste into your authoring tool)", expanded=False):
    st.markdown(pack.prompt_md)

zip_bytes = pack_to_zip_bytes(pack, resolved)

st.download_button(
    "Download authoring pack (ZIP)",
    data=zip_bytes,
    file_name=f"authoring_pack_{genre}_{preset}.zip",
    mime="application/zip",
)


st.divider()
st.subheader("Story brief (generated from resolved config)")

brief = generate_story_brief(resolved=resolved, genre=genre, preset=preset)

st.markdown(brief.markdown)

st.download_button(
    "Download story brief (Markdown)",
    data=brief.markdown.encode("utf-8"),
    file_name=f"story_brief_{genre}_{preset}.md",
    mime="text/markdown",
)

st.download_button(
    "Download story brief (JSON)",
    data=json.dumps(brief.data, indent=2).encode("utf-8"),
    file_name=f"story_brief_{genre}_{preset}.json",
    mime="application/json",
)


st.divider()

# Create new preset from current resolved configuration
st.subheader("Create a new preset from this combination")
st.write("This saves only differences from baseline + genre defaults (so presets stay small and reusable).")

p1, p2 = st.columns([1, 2])

with p1:
    new_preset_id = st.text_input("Preset id (file name)", value="my_preset")
    new_label = st.text_input("Label", value="My Preset")

with p2:
    new_desc = st.text_area("Description", value="", height=80)

new_preset_json = save_preset_from_diff(
    resolved=resolved,
    genre=genre,
    repo_root=REPO_ROOT,
    preset_id=new_preset_id,
    label=new_label,
    description=new_desc,
)

st.code(json.dumps(new_preset_json, indent=2), language="json")

st.download_button(
    "Download preset JSON",
    data=json.dumps(new_preset_json, indent=2).encode("utf-8"),
    file_name=f"{new_preset_id}.json",
    mime="application/json",
)

st.caption("To use your new preset: save the downloaded JSON into the /presets folder, commit, and push to GitHub.")
