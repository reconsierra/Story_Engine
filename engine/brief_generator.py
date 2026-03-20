
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple, List


@dataclass
class BriefOutput:
    markdown: str
    data: dict


def _pick(resolved: Dict[str, str], key: str, default: str) -> str:
    return resolved.get(key, default)


def _map_genre(genre: str) -> Tuple[str, List[str], List[str]]:
    """Return (genre_name, promises, avoid)."""
    genre = (genre or "").lower()

    if genre == "military":
        return (
            "Military / Espionage Thriller",
            [
                "High stakes, credible tactics and pressure",
                "Clear mission objectives with escalating complications",
                "A competent lead forced into hard choices",
            ],
            [
                "Overly technical exposition without payoff",
                "Unmotivated villains",
                "Coincidence-based solutions",
            ],
        )

    if genre == "mystery":
        return (
            "Mystery",
            [
                "Fair-play clues (readers can solve it too)",
                "Rising suspicion, twists, and a satisfying reveal",
                "A central question that drives every chapter",
            ],
            [
                "Withholding the key clue unfairly",
                "Random culprit reveal with no foreshadowing",
                "Too many unrelated subplots",
            ],
        )

    if genre == "adventure":
        return (
            "Adventure",
            [
                "Momentum, discovery, and a clear objective",
                "Escalating obstacles and set pieces",
                "A rewarding payoff and sense of journey",
            ],
            [
                "Aimless wandering",
                "Low stakes for too long",
                "Too many slow info-dumps",
            ],
        )

    if genre == "drama":
        return (
            "Drama",
            [
                "Emotionally driven choices and consequences",
                "Relationships under stress",
                "A cathartic resolution (even if bittersweet)",
            ],
            [
                "Melodrama without grounding",
                "Characters acting against motivation",
                "Events that happen ‘to’ characters without agency",
            ],
        )

    return (
        "General Fiction",
        ["Clear stakes", "Compelling characters", "Rising tension"],
        ["Meandering middle", "Flat antagonist", "Unearned ending"],
    )


def _tone_pack(resolved: Dict[str, str]) -> str:
    sentence_style = _pick(resolved, "tone_and_language.sentence_style", "mixed")
    dialogue_ratio = _pick(resolved, "tone_and_language.dialogue_ratio", "balanced")
    moral = _pick(resolved, "tone_and_language.moral_ambiguity", "clear_morality")

    sentence_map = {
        "short_punchy": "Short, punchy sentences; brisk paragraphs; minimal waffle.",
        "mixed": "Mixed sentence lengths; clarity first; occasional rhythm for emphasis.",
        "long_lyrical": "Longer, more lyrical lines; atmosphere and reflection; careful pacing.",
    }

    dialogue_map = {
        "dialogue_heavy": "Dialogue-forward scenes; subtext; quick back-and-forth.",
        "balanced": "Balanced dialogue and description; keep scenes purposeful.",
        "descriptive_heavy": "More internal thought and description; slower, deliberate beats.",
    }

    moral_map = {
        "clear_morality": "Clear right/wrong; decisions are decisive; consequences still matter.",
        "grey_choices": "Grey choices; competing goods; moral tension drives character action.",
        "no_good_options": "No clean exits; every option costs something; consequences are unavoidable.",
    }

    return " ".join([sentence_map.get(sentence_style, ""), dialogue_map.get(dialogue_ratio, ""), moral_map.get(moral, "")]).strip()


def _pacing_pack(resolved: Dict[str, str]) -> str:
    act = _pick(resolved, "pacing_structure.act_weighting", "mid_heavy")
    turns = _pick(resolved, "pacing_structure.turning_points", "standard")
    time_pressure = _pick(resolved, "pressure_and_flow.time_pressure", "soft_deadline")
    recovery = _pick(resolved, "pressure_and_flow.recovery_time", "brief")
    reveal = _pick(resolved, "information_control.reveal_granularity", "incremental_reveals")

    act_map = {
        "front_loaded": "Hook early; commit fast; keep the middle moving with discoveries.",
        "mid_heavy": "A steadily tightening middle; midpoint shift; late acceleration.",
        "back_loaded": "Strong build-up; escalating pressure; relentless final act.",
    }

    turns_map = {
        "minimal": "Fewer, heavier turns; longer scenes; deeper emotional beats.",
        "standard": "Regular turns; each chapter changes the situation meaningfully.",
        "high_frequency": "Frequent reversals; short arcs; constant momentum.",
    }

    pressure_map = {
        "none": "No strict clock; pace comes from character choices and consequences.",
        "soft_deadline": "A looming deadline; occasional reminders; flexible tension.",
        "hard_deadline": "A hard deadline; urgency drives scene choices and cuts downtime.",
        "countdown": "A visible countdown; every chapter should tighten the vice.",
    }

    recovery_map = {
        "none": "No breathing room; cut quickly to the next threat or decision.",
        "brief": "Short decompression beats; then back into conflict.",
        "extended": "Longer recovery/reflection beats; use them to deepen stakes and relationships.",
    }

    reveal_map = {
        "big_reveals": "Fewer, weightier reveals; build pressure between them.",
        "incremental_reveals": "Regular reveals; each one changes the reader’s theory.",
    }

    return " ".join(
        [
            act_map.get(act, ""),
            turns_map.get(turns, ""),
            pressure_map.get(time_pressure, ""),
            recovery_map.get(recovery, ""),
            reveal_map.get(reveal, ""),
        ]
    ).strip()


def _build_logline(resolved: Dict[str, str], genre_label: str) -> str:
    story_type = _pick(resolved, "story_engine.story_type", "defeat_antagonist")
    antagonist_motive = _pick(resolved, "antagonist.motivation", "financial_bribery")
    time_pressure = _pick(resolved, "pressure_and_flow.time_pressure", "soft_deadline")

    story_map = {
        "mission_based": "must complete a mission",
        "adventure_reward": "chases a prize that changes everything",
        "defeat_antagonist": "must stop a dangerous adversary",
        "neighbourhood_dispute": "is dragged into a conflict that spirals",
        "protecting_family": "must protect their family from escalating danger",
        "protecting_client": "must protect a client under threat",
        "revenge": "is drawn into a revenge spiral",
        "theft_of_item": "must steal or recover a critical item",
        "hostile_takeover_plot": "uncovers a hostile takeover with real-world consequences",
    }

    motive_map = {
        "high_level_terrorism": "a high-level terror plot",
        "local_troublemaker": "a local troublemaker with bigger reach than expected",
        "wannabe_kingpin": "a wannabe kingpin building an empire",
        "revenge": "revenge as a driving motive",
        "financial_bribery": "money, leverage and corruption",
        "targeting_high_tech_item": "a high-tech asset everyone wants",
    }

    clock_map = {
        "none": "with no clear deadline",
        "soft_deadline": "before time runs out",
        "hard_deadline": "before a hard deadline hits",
        "countdown": "against a ticking countdown",
    }

    return (
        f"In this {genre_label}, the protagonist {story_map.get(story_type, 'faces a crisis')} "
        f"driven by {motive_map.get(antagonist_motive, 'a dangerous motive')}, "
        f"{clock_map.get(time_pressure, 'under mounting pressure')}."
    )


def generate_story_brief(
    resolved: Dict[str, str],
    genre: str,
    preset: str,
) -> BriefOutput:
    """Generate a structured story brief (Markdown + data) from a resolved config dict."""
    genre_label, promises, avoid = _map_genre(genre)

    protagonist = _pick(resolved, "identity.main_character", "traveling_loner")
    sidekick = _pick(resolved, "identity.secondary_character", "genius_problem_solver")
    relationship = _pick(resolved, "identity.relationship_main_secondary", "friendly")

    antagonist_relation = _pick(resolved, "antagonist.relationship_to_protagonist", "old_colleague")
    contact = _pick(resolved, "story_engine.contact_types", "threats")
    complications = _pick(resolved, "story_engine.complications", "weather")

    pov = _pick(resolved, "viewpoint.pov_count", "single")
    threads = _pick(resolved, "viewpoint.parallel_plot_threads", "single_thread")
    internal_external = _pick(resolved, "information_control.internal_external_ratio", "50_50")

    setting_scope = _pick(resolved, "pacing_structure.setting_confinement", "limited_locations")
    travel = _pick(resolved, "pressure_and_flow.travel_compression", "skipped")
    stakes = _pick(resolved, "pressure_and_flow.stakes_escalation", "linear")

    logline = _build_logline(resolved, genre_label)
    tone = _tone_pack(resolved)
    pacing = _pacing_pack(resolved)

    # Deterministic, reusable title prompts (not a final title)
    title_prompts = [
        f"{genre_label}: <Noun> of <Noun>",
        f"{genre_label}: <Place> Under <Threat>",
        f"{genre_label}: The <Object> Protocol",
        f"{genre_label}: <Surname>’s <Secret>",
    ]

    data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "genre": genre,
        "genre_label": genre_label,
        "preset": preset,
        "logline": logline,
        "resolved": resolved,
    }

    md = []
    md.append(f"# Story Brief\n")
    md.append(f"**Genre:** {genre_label}\n")
    md.append(f"**Preset pack:** `{preset}`\n")
    md.append(f"**Logline:** {logline}\n")
    md.append("\n---\n")

    md.append("## Genre promise (what readers should get)\n")
    for p in promises:
        md.append(f"- {p}\n")

    md.append("\n## What to avoid\n")
    for a in avoid:
        md.append(f"- {a}\n")

    md.append("\n---\n")
    md.append("## Core cast (engine-derived)\n")
    md.append(f"- **Protagonist archetype:** `{protagonist}`\n")
    md.append(f"- **Secondary archetype:** `{sidekick}`\n")
    md.append(f"- **Relationship dynamic:** `{relationship}`\n")
    md.append(f"- **Antagonist link to protagonist:** `{antagonist_relation}`\n")

    md.append("\n## Conflict profile\n")
    md.append(f"- **Primary pressure/contact:** `{contact}`\n")
    md.append(f"- **Complication bias:** `{complications}`\n")
    md.append(f"- **Stakes escalation:** `{stakes}`\n")

    md.append("\n## Setting & movement\n")
    md.append(f"- **Setting confinement:** `{setting_scope}`\n")
    md.append(f"- **Travel / transitions:** `{travel}`\n")
    md.append("*(You can add specific location variables later; this version focuses on narrative behaviour.)*\n")

    md.append("\n---\n")
    md.append("## Narrative choices (engine-derived)\n")
    md.append(f"- **POV count:** `{pov}`\n")
    md.append(f"- **Parallel threads:** `{threads}`\n")
    md.append(f"- **Internal vs external:** `{internal_external}`\n")

    md.append("\n## Pace & rhythm notes\n")
    md.append(pacing + "\n")

    md.append("\n## Tone & prose notes\n")
    md.append(tone + "\n")

    md.append("\n---\n")
    md.append("## Plot skeleton (fill-in template)\n")
    md.append("Use this as a chapter/scene blueprint. Each bullet should become 1–3 scenes.\n\n")
    md.append("### Act 1 — Setup & commitment\n")
    md.append("- Hook: open with immediate disruption tied to the core threat.\n")
    md.append("- Inciting incident: protagonist is forced to act.\n")
    md.append("- Commitment: the protagonist commits to the objective.\n\n")

    md.append("### Act 2 — Pressure, reversals, and discovery\n")
    md.append("- Rising obstacles: escalate through contact type and complications.\n")
    md.append("- Midpoint shift: reveal that changes the plan or redefines the threat.\n")
    md.append("- Lowest point: protagonist loses leverage; stakes spike.\n\n")

    md.append("### Act 3 — Resolution\n")
    md.append("- Final approach: gather the last piece of leverage.\n")
    md.append("- Confrontation: decisive action under peak pressure.\n")
    md.append("- Reveal / resolution: explain the antagonist’s motive and consequences.\n")

    md.append("\n---\n")
    md.append("## Title ideas (prompts)\n")
    for t in title_prompts:
        md.append(f"- {t}\n")

    md.append("\n---\n")
    md.append("## Next build steps (optional)\n")
    md.append("- Convert this brief into a chapter-by-chapter outline.\n")
    md.append("- Generate scene cards (goal / conflict / outcome / hook) per chapter.\n")
    md.append("- Produce a Markdown manuscript scaffold for your book factory.\n")

    return BriefOutput(markdown="".join(md), data=data)
