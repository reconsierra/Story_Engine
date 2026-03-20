
    import json
    from pathlib import Path

    import streamlit as st

    from engine.resolver import resolve, save_preset_from_diff


    REPO_ROOT = Path(__file__).parent
    AUTO = "Auto (engine default)"


    def load_json(rel_path: str):
        return json.loads((REPO_ROOT / rel_path).read_text(encoding='utf-8'))


    def flatten_schema(schema: dict):
        """Return list of (group, path, allowed) for UI."""
        rows = []

        def walk(node, prefix="", group=""):
            if isinstance(node, dict):
                if 'allowed' in node and 'value' in node:
                    rows.append((group, prefix, node['allowed']))
                    return
                for k, v in node.items():
                    if k == 'meta':
                        continue
                    new_prefix = f"{prefix}.{k}" if prefix else k
                    new_group = group or prefix.split('.')[0] if prefix else k
                    walk(v, new_prefix, new_group)

        walk(schema)
        # Sort by group then path
        rows.sort(key=lambda r: (r[0], r[1]))
        return rows


    st.set_page_config(page_title="Story Engine", layout="wide")
    st.title("Story Engine – presets + overrides")
    st.caption("Defaults are deterministic and genre-aware. Nothing is random unless you add it later.")

    schema = load_json('schemas/book_schema.json')
    engine_defaults = load_json('engine/engine_defaults.json')

    # Top controls
    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        genre = st.selectbox("Genre", schema['identity']['genre']['allowed'], index=0)

    with c2:
        preset_files = sorted([p.stem for p in (REPO_ROOT / 'presets').glob('*.json')])
        preset = st.selectbox("Preset pack", preset_files, index=preset_files.index('engine_default') if 'engine_default' in preset_files else 0)

    with c3:
        st.markdown("**How it resolves**: User override → preset → engine defaults → dependency guardrails")

    st.divider()

    # Build override UI from schema
    schema_rows = flatten_schema(schema)

    st.subheader("Overrides (optional)")
    st.write("Leave any variable on **Auto** unless you want to force it. You can override one variable or many.")

    overrides = {}

    # Sidebar groups for better scanning
    st.sidebar.header("Overrides")
    st.sidebar.caption("Tip: Start by changing one variable only.")

    groups = {}
    for group, path, allowed in schema_rows:
        groups.setdefault(group, []).append((path, allowed))

    for group in groups:
        with st.sidebar.expander(group, expanded=(group in ['identity', 'pacing_structure'])):
            for path, allowed in groups[group]:
                # don't render genre here (already top control)
                if path == 'identity.genre':
                    continue
                label = path.replace('_', ' ').replace('.', ' → ')
                choice = st.selectbox(label, [AUTO] + allowed, key=path)
                if choice != AUTO:
                    overrides[path] = choice

    # Resolve
    config = {"genre": genre, "preset": preset, "overrides": overrides}

    resolved, warnings = resolve(config=config, repo_root=REPO_ROOT)

    st.subheader("Resolved values")
    if warnings:
        st.warning("
".join(warnings))

    st.code(json.dumps(resolved, indent=2), language='json')

    # Downloads
    st.download_button(
        "Download resolved JSON",
        data=json.dumps(resolved, indent=2).encode('utf-8'),
        file_name=f"resolved_{genre}_{preset}.json",
        mime="application/json"
    )

    st.divider()
    st.subheader("Create a new preset from this combination")
    st.write("This saves only differences from baseline + genre defaults.")

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
        description=new_desc
    )

    st.code(json.dumps(new_preset_json, indent=2), language='json')

    st.download_button(
        "Download preset JSON",
        data=json.dumps(new_preset_json, indent=2).encode('utf-8'),
        file_name=f"{new_preset_id}.json",
        mime="application/json"
    )

    st.caption("To use your new preset: put the downloaded JSON into the /presets folder in your repo and push to GitHub.")
