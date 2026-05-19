from pathlib import Path
import time

import pandas as pd
import requests


POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"


POKEMON_NAME_ALIASES = {
    "Landorus-Therian": "landorus-therian",
    "Tornadus-Therian": "tornadus-therian",
    "Thundurus-Therian": "thundurus-therian",
    "Enamorus-Therian": "enamorus-therian",

    "Slowking-Galar": "slowking-galar",
    "Slowbro-Galar": "slowbro-galar",
    "Weezing-Galar": "weezing-galar",
    "Zapdos-Galar": "zapdos-galar",
    "Moltres-Galar": "moltres-galar",
    "Articuno-Galar": "articuno-galar",

    "Tauros-Paldea-Aqua": "tauros-paldea-aqua-breed",
    "Tauros-Paldea-Blaze": "tauros-paldea-blaze-breed",
    "Tauros-Paldea-Combat": "tauros-paldea-combat-breed",

    "Ogerpon-Wellspring": "ogerpon-wellspring-mask",
    "Ogerpon-Hearthflame": "ogerpon-hearthflame-mask",
    "Ogerpon-Cornerstone": "ogerpon-cornerstone-mask",

    "Indeedee-F": "indeedee-female",
    "Basculegion-F": "basculegion-female",
    "Basculegion-M": "basculegion-male",

    "Urshifu-Rapid-Strike": "urshifu-rapid-strike",
    "Urshifu-Single-Strike": "urshifu-single-strike",

    "Toxtricity-Low-Key": "toxtricity-low-key",
    "Maushold-Four": "maushold-family-of-four",
    "Maushold-Three": "maushold-family-of-three",

    "Dudunsparce-Three-Segment": "dudunsparce-three-segment",
    "Dudunsparce-Two-Segment": "dudunsparce-two-segment",

    "Zacian-Crowned": "zacian-crowned",
    "Zamazenta-Crowned": "zamazenta-crowned",
    "Giratina-Origin": "giratina-origin",
    "Dialga-Origin": "dialga-origin",
    "Palkia-Origin": "palkia-origin",

    "Kyurem-Black": "kyurem-black",
    "Kyurem-White": "kyurem-white",

    "Necrozma-Dusk-Mane": "necrozma-dusk",
    "Necrozma-Dawn-Wings": "necrozma-dawn",

    "Hoopa-Unbound": "hoopa-unbound",
}


def smogon_name_to_pokeapi_name(name):
    if name in POKEMON_NAME_ALIASES:
        return POKEMON_NAME_ALIASES[name]

    return (
        name.lower()
        .replace(" ", "-")
        .replace(".", "")
        .replace("'", "")
        .replace(":", "")
    )


def fetch_pokemon_from_pokeapi(name):
    api_name = smogon_name_to_pokeapi_name(name)
    url = f"{POKEAPI_BASE_URL}/{api_name}"

    response = requests.get(url, timeout=30)

    if response.status_code != 200:
        return None

    return response.json()


def extract_pokemon_data(name, api_data):
    types = [slot["type"]["name"].title() for slot in api_data["types"]]

    type_1 = types[0] if len(types) > 0 else "-"
    type_2 = types[1] if len(types) > 1 else "-"

    stat_map = {
        item["stat"]["name"]: item["base_stat"]
        for item in api_data["stats"]
    }

    return {
        "name": name,
        "type_1": type_1,
        "type_2": type_2,
        "hp": stat_map.get("hp", 0),
        "attack": stat_map.get("attack", 0),
        "defense": stat_map.get("defense", 0),
        "special_attack": stat_map.get("special-attack", 0),
        "special_defense": stat_map.get("special-defense", 0),
        "speed": stat_map.get("speed", 0),
    }


def combine_roles(roles_series):
    all_roles = set()

    for roles_value in roles_series.dropna():
        for role in str(roles_value).split(";"):
            role = role.strip()

            if role:
                all_roles.add(role)

    return ";".join(sorted(all_roles))


def build_pokemon_data(
    sets_path="data/pokemon_sets.csv",
    output_path="data/pokemon_data.csv"
):
    sets_df = pd.read_csv(sets_path)

    grouped = (
        sets_df
        .groupby(["generation", "pokemon", "tier"], as_index=False)
        .agg({
            "roles": combine_roles
        })
    )

    rows = []
    failed_names = []

    unique_names = sorted(grouped["pokemon"].unique())

    print(f"Building Pokémon base dataset for {len(unique_names)} unique Pokémon...")

    pokemon_cache = {}

    for index, name in enumerate(unique_names, start=1):
        print(f"[{index}/{len(unique_names)}] Fetching {name}...")

        api_data = fetch_pokemon_from_pokeapi(name)

        if api_data is None:
            failed_names.append(name)
            continue

        pokemon_cache[name] = extract_pokemon_data(name, api_data)

        time.sleep(0.03)

    for _, row in grouped.iterrows():
        name = row["pokemon"]

        if name not in pokemon_cache:
            continue

        base_data = pokemon_cache[name].copy()

        base_data.update({
            "generation": int(row["generation"]),
            "tier": row["tier"],
            "roles": row["roles"]
        })

        rows.append(base_data)

    pokemon_df = pd.DataFrame(rows)

    column_order = [
        "generation",
        "name",
        "tier",
        "type_1",
        "type_2",
        "roles",
        "hp",
        "attack",
        "defense",
        "special_attack",
        "special_defense",
        "speed"
    ]

    pokemon_df = pokemon_df[column_order]
    pokemon_df = pokemon_df.sort_values(
        by=["generation", "tier", "name"],
        ascending=[False, True, True]
    )

    Path("data").mkdir(exist_ok=True)
    pokemon_df.to_csv(output_path, index=False)

    print("\nBuild complete.")
    print(f"Saved {len(pokemon_df)} rows to: {output_path}")
    print(f"Available generations: {sorted(pokemon_df['generation'].unique())}")
    print(f"Available tiers: {sorted(pokemon_df['tier'].unique())}")

    if failed_names:
        print("\nCould not fetch these Pokémon from PokeAPI:")
        for name in failed_names:
            print(f"- {name}")

    print("\nPreview:")
    print(pokemon_df.head())


if __name__ == "__main__":
    build_pokemon_data()