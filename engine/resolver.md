
Resolution order (deterministic):
1) Engine baseline defaults (engine/engine_defaults.json -> baseline)
2) Genre defaults (engine/engine_defaults.json -> genre:<genre>)
3) Story-type modifiers (engine/story_type_modifiers.json) (optional)
4) Preset overrides (presets/<preset>.json)
5) User overrides (from UI / examples config)
6) Dependency corrections (engine/dependency_rules.json)

No randomness is used.

Tip: When building the UI, include an "Auto (engine default)" option for each variable and only write an override when the user chooses a non-auto value.
