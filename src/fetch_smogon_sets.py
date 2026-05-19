from pathlib import Path

import pandas as pd
import requests


FORMATS = {
    # Generation 9
    "gen9ubers": {"generation": 9, "tier": "Ubers"},
    "gen9ou": {"generation": 9, "tier": "OU"},
    "gen9uu": {"generation": 9, "tier": "UU"},
    "gen9ru": {"generation": 9, "tier": "RU"},
    "gen9nu": {"generation": 9, "tier": "NU"},

    # Generation 8
    "gen8ubers": {"generation": 8, "tier": "Ubers"},
    "gen8ou": {"generation": 8, "tier": "OU"},
    "gen8uu": {"generation": 8, "tier": "UU"},
    "gen8ru": {"generation": 8, "tier": "RU"},
    "gen8nu": {"generation": 8, "tier": "NU"},

    # Generation 7
    "gen7ubers": {"generation": 7, "tier": "Ubers"},
    "gen7ou": {"generation": 7, "tier": "OU"},
    "gen7uu": {"generation": 7, "tier": "UU"},
    "gen7ru": {"generation": 7, "tier": "RU"},
    "gen7nu": {"generation": 7, "tier": "NU"},

    # Generation 6
    "gen6ubers": {"generation": 6, "tier": "Ubers"},
    "gen6ou": {"generation": 6, "tier": "OU"},
    "gen6uu": {"generation": 6, "tier": "UU"},
    "gen6ru": {"generation": 6, "tier": "RU"},
    "gen6nu": {"generation": 6, "tier": "NU"},

    # Generation 5
    "gen5ubers": {"generation": 5, "tier": "Ubers"},
    "gen5ou": {"generation": 5, "tier": "OU"},
    "gen5uu": {"generation": 5, "tier": "UU"},
    "gen5ru": {"generation": 5, "tier": "RU"},
    "gen5nu": {"generation": 5, "tier": "NU"},

    # Generation 4
    "gen4ubers": {"generation": 4, "tier": "Ubers"},
    "gen4ou": {"generation": 4, "tier": "OU"},
    "gen4uu": {"generation": 4, "tier": "UU"},
    "gen4nu": {"generation": 4, "tier": "NU"},

    # Generation 3
    "gen3ubers": {"generation": 3, "tier": "Ubers"},
    "gen3ou": {"generation": 3, "tier": "OU"},
    "gen3uu": {"generation": 3, "tier": "UU"},

    # Generation 2
    "gen2ubers": {"generation": 2, "tier": "Ubers"},
    "gen2ou": {"generation": 2, "tier": "OU"},
    "gen2uu": {"generation": 2, "tier": "UU"},

    # Generation 1
    "gen1ubers": {"generation": 1, "tier": "Ubers"},
    "gen1ou": {"generation": 1, "tier": "OU"},
}

BASE_URL = "https://data.pkmn.cc/sets/{format_id}.json"


def flatten_list(value):
    if value is None:
        return []

    if not isinstance(value, list):
        return [value]

    flattened = []

    for item in value:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)

    return flattened


def normalize_to_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return flatten_list(value)

    return [value]


def pick_first(value, default=""):
    values = normalize_to_list(value)

    if len(values) == 0:
        return default

    return str(values[0])


def get_stat_value(stat_block, stat_key, default_value):
    if not isinstance(stat_block, dict):
        return default_value

    return stat_block.get(stat_key, default_value)


def contains_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def infer_roles_from_set(
    set_name,
    moves,
    item,
    ability,
    nature,
    evs
):
    roles = set()

    set_name_lower = str(set_name).lower()
    move_names = [str(move).lower() for move in moves]
    item_lower = str(item).lower()
    ability_lower = str(ability).lower()
    nature_lower = str(nature).lower()

    ev_hp = get_stat_value(evs, "hp", 0)
    ev_atk = get_stat_value(evs, "atk", 0)
    ev_def = get_stat_value(evs, "def", 0)
    ev_spa = get_stat_value(evs, "spa", 0)
    ev_spd = get_stat_value(evs, "spd", 0)
    ev_spe = get_stat_value(evs, "spe", 0)

    hazard_moves = [
        "stealth rock",
        "spikes",
        "toxic spikes",
        "sticky web"
    ]

    removal_moves = [
        "rapid spin",
        "defog",
        "court change"
    ]

    pivot_moves = [
        "u-turn",
        "volt switch",
        "flip turn",
        "parting shot",
        "chilly reception",
        "baton pass",
        "teleport"
    ]

    setup_moves = [
        "swords dance",
        "nasty plot",
        "dragon dance",
        "calm mind",
        "bulk up",
        "curse",
        "quiver dance",
        "shell smash",
        "agility",
        "rock polish",
        "shift gear",
        "coil",
        "iron defense"
    ]

    recovery_moves = [
        "recover",
        "roost",
        "slack off",
        "soft-boiled",
        "moonlight",
        "synthesis",
        "wish",
        "rest",
        "milk drink",
        "shore up",
        "morning sun"
    ]

    status_moves = [
        "toxic",
        "will-o-wisp",
        "thunder wave",
        "glare",
        "spore",
        "sleep powder",
        "stun spore",
        "yawn",
        "hypnosis"
    ]

    cleric_moves = [
        "heal bell",
        "aromatherapy",
        "wish",
        "healing wish"
    ]

    screen_moves = [
        "reflect",
        "light screen",
        "aurora veil"
    ]

    phazing_moves = [
        "roar",
        "whirlwind",
        "dragon tail",
        "circle throw",
        "haze"
    ]

    trapping_moves = [
        "pursuit",
        "mean look",
        "block",
        "spider web",
        "magma storm",
        "fire spin",
        "whirlpool"
    ]

    priority_moves = [
        "extreme speed",
        "sucker punch",
        "bullet punch",
        "mach punch",
        "ice shard",
        "aqua jet",
        "shadow sneak",
        "quick attack",
        "vacuum wave"
    ]

    # Basic move-based roles
    if any(move in move_names for move in hazard_moves):
        roles.add("hazard_setter")
        roles.add("lead")

    if any(move in move_names for move in removal_moves):
        roles.add("hazard_remover")

    if any(move in move_names for move in pivot_moves):
        roles.add("pivot")

    if any(move in move_names for move in setup_moves):
        roles.add("setup_sweeper")

    if any(move in move_names for move in recovery_moves):
        roles.add("defensive_pivot")

    if any(move in move_names for move in status_moves):
        roles.add("status_spreader")

    if any(move in move_names for move in cleric_moves):
        roles.add("cleric")
        roles.add("support")

    if any(move in move_names for move in screen_moves):
        roles.add("screen_setter")
        roles.add("support")
        roles.add("lead")

    if any(move in move_names for move in phazing_moves):
        roles.add("phazer")
        roles.add("support")

    if any(move in move_names for move in trapping_moves):
        roles.add("trapper")

    if any(move in move_names for move in priority_moves):
        roles.add("priority_user")
        roles.add("revenge_killer")

    # Item-based roles
    if "choice scarf" in item_lower:
        roles.add("speed_control")
        roles.add("revenge_killer")
        roles.add("choice_user")

    if "choice specs" in item_lower:
        roles.add("special_wallbreaker")
        roles.add("wallbreaker")
        roles.add("choice_user")
        roles.add("special_attacker")

    if "choice band" in item_lower:
        roles.add("physical_wallbreaker")
        roles.add("wallbreaker")
        roles.add("choice_user")
        roles.add("physical_attacker")

    if "life orb" in item_lower:
        roles.add("wallbreaker")

    if "focus sash" in item_lower:
        roles.add("lead")

    if "assault vest" in item_lower:
        roles.add("special_tank")

    # Weather roles
    if ability_lower == "drizzle":
        roles.add("weather_setter")
        roles.add("rain_setter")

    if ability_lower == "drought":
        roles.add("weather_setter")
        roles.add("sun_setter")

    if ability_lower == "sand stream":
        roles.add("weather_setter")
        roles.add("sand_setter")

    if ability_lower == "snow warning":
        roles.add("weather_setter")
        roles.add("snow_setter")

    if ability_lower in ["swift swim", "chlorophyll", "sand rush", "slush rush"]:
        roles.add("weather_abuser")
        roles.add("speed_control")

    # Ability-based roles
    if ability_lower in ["magnet pull", "arena trap", "shadow tag"]:
        roles.add("trapper")

    if ability_lower in ["regenerator", "natural cure", "magic guard"]:
        roles.add("defensive_pivot")

    # EV and nature based attacking roles
    if ev_atk >= 200 and ev_spa < 100:
        roles.add("physical_attacker")

    if ev_spa >= 200 and ev_atk < 100:
        roles.add("special_attacker")

    if ev_atk >= 120 and ev_spa >= 120:
        roles.add("mixed_attacker")
        roles.add("wallbreaker")

    if ev_spe >= 200 and (ev_atk >= 180 or ev_spa >= 180):
        roles.add("speed_control")

    # EV and nature based defensive roles
    physically_defensive_natures = ["bold", "impish", "relaxed"]
    specially_defensive_natures = ["calm", "careful", "sassy"]

    if ev_hp >= 200 and ev_def >= 180:
        roles.add("physical_wall")

    if ev_hp >= 200 and ev_spd >= 180:
        roles.add("special_wall")

    if nature_lower in physically_defensive_natures and ev_hp >= 200:
        roles.add("physical_wall")

    if nature_lower in specially_defensive_natures and ev_hp >= 200:
        roles.add("special_wall")

    if ev_hp >= 200 and (ev_def >= 120 or ev_spd >= 120):
        roles.add("bulky_pivot")

    # Set-name based roles
    if contains_any(set_name_lower, ["physically defensive", "physical wall"]):
        roles.add("physical_wall")
        roles.add("defensive_pivot")

    if contains_any(set_name_lower, ["specially defensive", "special wall", "spdef"]):
        roles.add("special_wall")
        roles.add("defensive_pivot")

    if contains_any(set_name_lower, ["defensive", "utility", "support"]):
        roles.add("defensive_pivot")
        roles.add("support")

    if contains_any(set_name_lower, ["wallbreaker", "breaker", "choice band", "choice specs"]):
        roles.add("wallbreaker")

    if contains_any(set_name_lower, ["sweeper", "dragon dance", "swords dance", "nasty plot", "calm mind"]):
        roles.add("setup_sweeper")

    if contains_any(set_name_lower, ["lead", "suicide lead"]):
        roles.add("lead")

    if contains_any(set_name_lower, ["rain", "rain dance"]):
        roles.add("rain_setter")

    if contains_any(set_name_lower, ["sun", "sun setter"]):
        roles.add("sun_setter")

    if contains_any(set_name_lower, ["sand"]):
        roles.add("sand_setter")

    if contains_any(set_name_lower, ["trick room"]):
        roles.add("trick_room_setter")
        roles.add("support")

    if contains_any(set_name_lower, ["stallbreaker"]):
        roles.add("stallbreaker")

    # Taunt often indicates anti-lead or stallbreaker support
    if "taunt" in move_names:
        roles.add("stallbreaker")
        roles.add("support")

    if not roles:
        roles.add("general_attacker")

    return sorted(roles)


def fetch_format_sets(format_id):
    url = BASE_URL.format(format_id=format_id)
    response = requests.get(url, timeout=30)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


def convert_format_to_dataframe(raw_data, format_id, generation, tier_label):
    rows = []

    for pokemon_name, sets in raw_data.items():
        for set_name, set_data in sets.items():
            moves = normalize_to_list(set_data.get("moves"))

            item = pick_first(set_data.get("item"))
            ability = pick_first(set_data.get("ability"))
            nature = pick_first(set_data.get("nature"))
            tera_type = pick_first(set_data.get("teraType"))

            evs = set_data.get("evs", {})
            ivs = set_data.get("ivs", {})

            moves = [str(move) for move in moves]
            moves = moves[:4]

            while len(moves) < 4:
                moves.append("")

            inferred_roles = infer_roles_from_set(
                set_name=set_name,
                moves=moves,
                item=item,
                ability=ability,
                nature=nature,
                evs=evs
            )

            rows.append({
                "generation": generation,
                "pokemon": pokemon_name,
                "set_name": set_name,
                "format": format_id,
                "tier": tier_label,
                "roles": ";".join(inferred_roles),
                "item": item,
                "ability": ability,
                "nature": nature,
                "tera_type": tera_type,

                "ev_hp": get_stat_value(evs, "hp", 0),
                "ev_atk": get_stat_value(evs, "atk", 0),
                "ev_def": get_stat_value(evs, "def", 0),
                "ev_spa": get_stat_value(evs, "spa", 0),
                "ev_spd": get_stat_value(evs, "spd", 0),
                "ev_spe": get_stat_value(evs, "spe", 0),

                "iv_hp": get_stat_value(ivs, "hp", 31),
                "iv_atk": get_stat_value(ivs, "atk", 31),
                "iv_def": get_stat_value(ivs, "def", 31),
                "iv_spa": get_stat_value(ivs, "spa", 31),
                "iv_spd": get_stat_value(ivs, "spd", 31),
                "iv_spe": get_stat_value(ivs, "spe", 31),

                "move_1": moves[0],
                "move_2": moves[1],
                "move_3": moves[2],
                "move_4": moves[3],
            })

    return pd.DataFrame(rows)


def main():
    Path("data").mkdir(exist_ok=True)

    all_sets = []
    failed_formats = []

    for format_id, metadata in FORMATS.items():
        generation = metadata["generation"]
        tier_label = metadata["tier"]

        print(f"Fetching {format_id}...")

        try:
            raw_data = fetch_format_sets(format_id)

            if raw_data is None:
                print(f"  Skipped {format_id}: not available")
                failed_formats.append(format_id)
                continue

            format_df = convert_format_to_dataframe(
                raw_data,
                format_id=format_id,
                generation=generation,
                tier_label=tier_label
            )

            all_sets.append(format_df)
            print(f"  Added {len(format_df)} sets for Gen {generation} {tier_label}")

        except requests.RequestException as error:
            print(f"  Failed to fetch {format_id}: {error}")
            failed_formats.append(format_id)

    if not all_sets:
        raise RuntimeError("No Smogon sets were downloaded.")

    sets_df = pd.concat(all_sets, ignore_index=True)

    output_path = "data/pokemon_sets.csv"
    sets_df.to_csv(output_path, index=False)

    print("\nDownload complete.")
    print(f"Downloaded and converted {len(sets_df)} Smogon sets.")
    print(f"Saved to: {output_path}")
    print(f"Generations: {sorted([int(gen) for gen in sets_df['generation'].unique()])}")
    print(f"Formats: {sets_df['format'].nunique()}")

    if failed_formats:
        print("\nUnavailable or failed formats:")
        for format_id in failed_formats:
            print(f"- {format_id}")

    print("\nPreview:")
    print(sets_df.head())


if __name__ == "__main__":
    main()