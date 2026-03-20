# Story Engine (Streamlit) – Personal Use

A **deterministic, preset‑driven story engine** you can run as a Streamlit web app.

- **Not random by default**: decisions are intentional and rule‑driven.
- Choose a **genre** + **preset pack**, optionally override any variable.
- Download a fully **resolved config JSON**.
- Create and download a **new preset JSON** from any good combination.

## What’s in this repo

- `schemas/book_schema.json` – all variables and allowed values.
- `engine/engine_defaults.json` – baseline + genre defaults.
- `engine/story_type_modifiers.json` – optional extra rules by story type.
- `engine/dependency_rules.json` – guardrails that prevent incoherent combinations.
- `engine/resolver.py` – resolves everything deterministically.
- `presets/*.json` – preset packs (partial overlays).
- `streamlit_app.py` – Streamlit UI (dropdowns for every variable).

## Resolution rules (deterministic)

Order of precedence:

1. Engine baseline defaults
2. Genre defaults
3. Story-type modifiers (optional)
4. Preset overrides
5. User overrides
6. Dependency corrections

## Preset packs

- **engine_default**: pure engine defaults
- **relentless**: high pressure, constant escalation
- **fast_focused**: tight pacing without exhaustion
- **balanced**: broad, even rhythm
- **slow_burn**: atmosphere, moral tension, slower escalation
- **immersive_world**: scope, layered threads, rich environments
- **one_sitting**: short sessions, frequent hooks

Presets are **partial overlays**: anything not specified falls back to engine defaults.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud (recommended)

1. Push this repo to GitHub.
2. In Streamlit Community Cloud, create a new app from your GitHub repo.
3. Set **Main file path** to `streamlit_app.py`.

## Add your own preset

1. In the app, use **Create a new preset** and download the JSON.
2. Put it in `presets/<your_preset>.json`.
3. Push to GitHub – it will appear in the preset dropdown.

## Notes

- Keep any secrets out of Git (`.streamlit/secrets.toml` is gitignored).
- This is a *configuration engine* only. You can later connect it to a brief generator and manuscript factory.
