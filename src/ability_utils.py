import re
import requests


POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"


FORM_NAME_MAP = {
    # Urshifu forms
    "Urshifu-Rapid": "urshifu-rapid-strike",
    "Urshifu-Rapid-Strike": "urshifu-rapid-strike",
    "Urshifu-Single": "urshifu-single-strike",
    "Urshifu-Single-Strike": "urshifu-single-strike",
    "Urshifu": "urshifu-single-strike",

    # Paradox Pokémon
    "Great Tusk": "great-tusk",
    "Scream Tail": "scream-tail",
    "Brute Bonnet": "brute-bonnet",
    "Flutter Mane": "flutter-mane",
    "Slither Wing": "slither-wing",
    "Sandy Shocks": "sandy-shocks",
    "Roaring Moon": "roaring-moon",
    "Walking Wake": "walking-wake",
    "Gouging Fire": "gouging-fire",
    "Raging Bolt": "raging-bolt",
    "Iron Treads": "iron-treads",
    "Iron Bundle": "iron-bundle",
    "Iron Hands": "iron-hands",
    "Iron Jugulis": "iron-jugulis",
    "Iron Moth": "iron-moth",
    "Iron Thorns": "iron-thorns",
    "Iron Valiant": "iron-valiant",
    "Iron Leaves": "iron-leaves",
    "Iron Boulder": "iron-boulder",
    "Iron Crown": "iron-crown",

    # Treasures of Ruin
    "Wo-Chien": "wo-chien",
    "Chien-Pao": "chien-pao",
    "Ting-Lu": "ting-lu",
    "Chi-Yu": "chi-yu",

    # Calyrex forms
    "Calyrex-Ice": "calyrex-ice",
    "Calyrex-Shadow": "calyrex-shadow",

    # Forces of Nature
    "Tornadus-Therian": "tornadus-therian",
    "Thundurus-Therian": "thundurus-therian",
    "Landorus-Therian": "landorus-therian",
    "Enamorus-Therian": "enamorus-therian",
    "Tornadus-Incarnate": "tornadus-incarnate",
    "Thundurus-Incarnate": "thundurus-incarnate",
    "Landorus-Incarnate": "landorus-incarnate",
    "Enamorus-Incarnate": "enamorus-incarnate",

    # Special forms
    "Zacian-Crowned": "zacian-crowned",
    "Zamazenta-Crowned": "zamazenta-crowned",
    "Giratina-Origin": "giratina-origin",
    "Kyurem-Black": "kyurem-black",
    "Kyurem-White": "kyurem-white",
    "Necrozma-Dusk-Mane": "necrozma-dusk",
    "Necrozma-Dawn-Wings": "necrozma-dawn",
    "Necrozma-Ultra": "necrozma-ultra",
    "Hoopa-Unbound": "hoopa-unbound",

    # Ogerpon forms
    "Ogerpon-Wellspring": "ogerpon-wellspring-mask",
    "Ogerpon-Hearthflame": "ogerpon-hearthflame-mask",
    "Ogerpon-Cornerstone": "ogerpon-cornerstone-mask",

    # Regional forms
    "Weezing-Galar": "weezing-galar",
    "Muk-Alola": "muk-alola",
    "Sandslash-Alola": "sandslash-alola",
    "Ninetales-Alola": "ninetales-alola",
    "Persian-Alola": "persian-alola",
    "Dugtrio-Alola": "dugtrio-alola",
    "Marowak-Alola": "marowak-alola",
    "Slowbro-Galar": "slowbro-galar",
    "Slowking-Galar": "slowking-galar",
    "Zapdos-Galar": "zapdos-galar",
    "Moltres-Galar": "moltres-galar",
    "Articuno-Galar": "articuno-galar",

    # Common alternate forms
    "Rotom-Heat": "rotom-heat",
    "Rotom-Wash": "rotom-wash",
    "Rotom-Frost": "rotom-frost",
    "Rotom-Fan": "rotom-fan",
    "Rotom-Mow": "rotom-mow",
    "Basculegion-F": "basculegion-female",
    "Indeedee-F": "indeedee-female",
    "Meowstic-F": "meowstic-female",
    "Oinkologne-F": "oinkologne-female",
    "Toxtricity-Low-Key": "toxtricity-low-key",
    "Darmanitan-Galar": "darmanitan-galar-standard",
    "Darmanitan-Galar-Zen": "darmanitan-galar-zen",
    "Darmanitan-Zen": "darmanitan-zen",
    "Aegislash-Blade": "aegislash-blade",
    "Aegislash-Shield": "aegislash-shield",
    "Greninja-Ash": "greninja-ash",
    "Lycanroc-Dusk": "lycanroc-dusk",
    "Lycanroc-Midnight": "lycanroc-midnight",
    "Lycanroc-Midday": "lycanroc-midday",
    "Palafin-Hero": "palafin-hero",
}


DEFAULT_COMPETITIVE_ABILITIES = {
    # Very obvious single-standard competitive ability cases
    "Ditto": "Imposter",
    "Gholdengo": "Good as Gold",
    "Garganacl": "Purifying Salt",
    "Flutter Mane": "Protosynthesis",
    "Great Tusk": "Protosynthesis",
    "Scream Tail": "Protosynthesis",
    "Brute Bonnet": "Protosynthesis",
    "Slither Wing": "Protosynthesis",
    "Sandy Shocks": "Protosynthesis",
    "Roaring Moon": "Protosynthesis",
    "Walking Wake": "Protosynthesis",
    "Gouging Fire": "Protosynthesis",
    "Raging Bolt": "Protosynthesis",
    "Iron Treads": "Quark Drive",
    "Iron Bundle": "Quark Drive",
    "Iron Hands": "Quark Drive",
    "Iron Jugulis": "Quark Drive",
    "Iron Moth": "Quark Drive",
    "Iron Thorns": "Quark Drive",
    "Iron Valiant": "Quark Drive",
    "Iron Leaves": "Quark Drive",
    "Iron Boulder": "Quark Drive",
    "Iron Crown": "Quark Drive",
    "Chien-Pao": "Sword of Ruin",
    "Chi-Yu": "Beads of Ruin",
    "Ting-Lu": "Vessel of Ruin",
    "Wo-Chien": "Tablets of Ruin",
    "Zacian": "Intrepid Sword",
    "Zacian-Crowned": "Intrepid Sword",
    "Zamazenta": "Dauntless Shield",
    "Zamazenta-Crowned": "Dauntless Shield",
    "Miraidon": "Hadron Engine",
    "Koraidon": "Orichalcum Pulse",
    "Kingambit": "Supreme Overlord",
    "Gliscor": "Poison Heal",
    "Breloom": "Technician",
    "Toxapex": "Regenerator",
    "Alomomola": "Regenerator",
    "Slowbro": "Regenerator",
    "Slowking": "Regenerator",
    "Slowking-Galar": "Regenerator",
    "Amoonguss": "Regenerator",
    "Landorus-Therian": "Intimidate",
    "Tornadus-Therian": "Regenerator",
    "Thundurus-Therian": "Volt Absorb",
    "Enamorus-Therian": "Overcoat",
    "Heatran": "Flash Fire",
    "Volcarona": "Flame Body",
    "Dragonite": "Multiscale",
    "Corviknight": "Pressure",
    "Dondozo": "Unaware",
    "Clodsire": "Water Absorb",
    "Skeledirge": "Unaware",
    "Clefable": "Magic Guard",
    "Pelipper": "Drizzle",
    "Torkoal": "Drought",
    "Tyranitar": "Sand Stream",
    "Hippowdon": "Sand Stream",
    "Ninetales-Alola": "Snow Warning",
    "Abomasnow": "Snow Warning",
    "Excadrill": "Sand Rush",
    "Hatterene": "Magic Bounce",
    "Espeon": "Magic Bounce",
    "Xatu": "Magic Bounce",
    "Sableye": "Prankster",
    "Whimsicott": "Prankster",
    "Klefki": "Prankster",
    "Grimmsnarl": "Prankster",
    "Meowscarada": "Protean",
    "Greninja": "Protean",
    "Cinderace": "Libero",
    "Serperior": "Contrary",
    "Malamar": "Contrary",
    "Shuckle": "Sturdy",
    "Shedinja": "Wonder Guard",
    "Azumarill": "Huge Power",
    "Medicham": "Pure Power",
    "Mawile-Mega": "Huge Power",
    "Mimikyu": "Disguise",
    "Kommo-o": "Bulletproof",
    "Porygon2": "Trace",
    "Chansey": "Natural Cure",
    "Blissey": "Natural Cure",
    "Skarmory": "Sturdy",
    "Ferrothorn": "Iron Barbs",
    "Kartana": "Beast Boost",
    "Blacephalon": "Beast Boost",
    "Nihilego": "Beast Boost",
    "Celesteela": "Beast Boost",
    "Buzzwole": "Beast Boost",
    "Pheromosa": "Beast Boost",
    "Naganadel": "Beast Boost",
    "Xurkitree": "Beast Boost",
    "Stakataka": "Beast Boost",
}


def normalize_pokemon_name_for_pokeapi(name):
    if name in FORM_NAME_MAP:
        return FORM_NAME_MAP[name]

    normalized = str(name).strip().lower()
    normalized = normalized.replace("♀", "-f")
    normalized = normalized.replace("♂", "-m")
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("'", "")
    normalized = normalized.replace(":", "")
    normalized = normalized.replace(" ", "-")

    normalized = re.sub(r"[^a-z0-9-]", "", normalized)

    return normalized


def format_ability_name(ability_name):
    return str(ability_name).replace("-", " ").title()


def get_moves_from_row(row):
    moves = []

    for move_col in ["move_1", "move_2", "move_3", "move_4"]:
        move = row.get(move_col, "")

        if move and str(move).strip():
            moves.append(str(move).strip())

    return moves


def get_set_text(row):
    pieces = [
        str(row.get("set_name", "")),
        str(row.get("item", "")),
        str(row.get("roles", "")),
    ]

    pieces.extend(get_moves_from_row(row))

    return " ".join(pieces).lower()


def infer_competitive_ability_from_row(row):
    pokemon_name = row.get("name", row.get("pokemon", ""))

    if not pokemon_name:
        return None

    set_text = get_set_text(row)

    # Set-specific rules first.
    if pokemon_name == "Grimmsnarl":
        if any(term in set_text for term in ["reflect", "light screen", "dual screens", "taunt", "thunder wave", "parting shot"]):
            return "Prankster"

    if pokemon_name in ["Lilligant-Hisui", "Lilligant-H", "Hisuian Lilligant"]:
        if any(term in set_text for term in ["sun", "sunny day", "weather", "chlorophyll"]):
            return "Chlorophyll"
        return "Hustle"

    if pokemon_name == "Garganacl":
        return "Purifying Salt"

    if pokemon_name == "Ditto":
        return "Imposter"

    if pokemon_name == "Gholdengo":
        return "Good as Gold"

    if pokemon_name == "Gliscor":
        if any(term in set_text for term in ["toxic orb", "poison heal"]):
            return "Poison Heal"

    if pokemon_name == "Breloom":
        if any(term in set_text for term in ["bullet seed", "mach punch", "technician"]):
            return "Technician"

    if pokemon_name == "Clefable":
        if any(term in set_text for term in ["calm mind", "life orb", "stealth rock", "utility"]):
            return "Magic Guard"

    if pokemon_name == "Dragonite":
        return "Multiscale"

    if pokemon_name == "Kingambit":
        return "Supreme Overlord"

    if pokemon_name == "Toxapex":
        return "Regenerator"

    if pokemon_name == "Alomomola":
        return "Regenerator"

    # General curated defaults.
    if pokemon_name in DEFAULT_COMPETITIVE_ABILITIES:
        return DEFAULT_COMPETITIVE_ABILITIES[pokemon_name]

    return None


def get_single_regular_ability_from_pokeapi(pokemon_name):
    pokeapi_name = normalize_pokemon_name_for_pokeapi(pokemon_name)
    url = f"{POKEAPI_BASE_URL}/{pokeapi_name}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        regular_abilities = [
            ability_entry["ability"]["name"]
            for ability_entry in data.get("abilities", [])
            if not ability_entry.get("is_hidden", False)
        ]

        regular_abilities = sorted(set(regular_abilities))

        if len(regular_abilities) == 1:
            return format_ability_name(regular_abilities[0])

        return None

    except Exception:
        return None


if __name__ == "__main__":
    test_rows = [
        {
            "name": "Grimmsnarl",
            "set_name": "Dual Screens",
            "item": "Light Clay",
            "move_1": "Reflect",
            "move_2": "Light Screen",
            "move_3": "Taunt",
            "move_4": "Play Rough",
        },
        {
            "name": "Garganacl",
            "set_name": "Defensive",
            "item": "Leftovers",
            "move_1": "Salt Cure",
        },
        {
            "name": "Lilligant-Hisui",
            "set_name": "Victory Dance",
            "move_1": "Victory Dance",
        },
        {
            "name": "Ditto",
            "set_name": "Choice Scarf",
            "move_1": "Transform",
        },
    ]

    for row in test_rows:
        print(row["name"], "->", infer_competitive_ability_from_row(row))