import random
import pandas as pd

from src.data_loader import load_pokemon_data, filter_by_generation_and_tier
from src.set_loader import load_pokemon_sets


TEAM_TEMPLATES = {
    "Pure Random": [],

    "Balanced": [
        "hazard_setter",
        "hazard_remover",
        "physical_wall",
        "special_wall",
        "wallbreaker",
        "speed_control"
    ],

    "Hyper Offense": [
        "lead",
        "setup_sweeper",
        "setup_sweeper",
        "wallbreaker",
        "speed_control",
        "cleaner"
    ],

    "Bulky Offense": [
        "hazard_setter",
        "pivot",
        "defensive_pivot",
        "wallbreaker",
        "physical_attacker",
        "speed_control"
    ],

    "Ubers Balance": [
        "hazard_setter",
        "hazard_remover",
        "wallbreaker",
        "speed_control",
        "setup_sweeper",
        "revenge_killer"
    ],

    "Ubers Offense": [
        "lead",
        "hazard_setter",
        "wallbreaker",
        "setup_sweeper",
        "speed_control",
        "revenge_killer"
    ]
}


ALWAYS_SHINY_POKEMON = [
    "Koffing",
    "Weezing",
    "Weezing-Galar"
]


def has_role(roles, target_role):
    return target_role in roles


def generate_random_team(df, team_size=6, random_state=None):
    if random_state is not None:
        random.seed(random_state)

    if len(df) < team_size:
        raise ValueError("Not enough Pokémon available to generate a team.")

    team_df = df.sample(n=team_size, random_state=random_state).reset_index(drop=True)
    team_df["chosen_role"] = "random"

    return team_df


def choose_set_for_pokemon(pokemon_sets, chosen_role, used_items, enforce_item_clause):
    if chosen_role not in ["random", "filler"]:
        matching_sets = pokemon_sets[
            pokemon_sets["roles"].apply(lambda roles: chosen_role in roles)
        ]
    else:
        matching_sets = pokemon_sets

    if len(matching_sets) == 0:
        matching_sets = pokemon_sets

    if enforce_item_clause:
        unique_item_sets = matching_sets[
            ~matching_sets["item"].isin(used_items)
        ]

        if len(unique_item_sets) > 0:
            matching_sets = unique_item_sets

    selected_set = matching_sets.sample(
        n=1,
        random_state=random.randint(1, 999999)
    ).iloc[0]

    return selected_set


def determine_shiny_status(pokemon_name, shiny_chance=1 / 6):
    if pokemon_name in ALWAYS_SHINY_POKEMON:
        return True

    return random.random() < shiny_chance


def attach_best_available_set(
    team_df,
    sets_df,
    enforce_item_clause=False,
    shiny_chance=1 / 6
):
    enriched_rows = []
    used_items = set()

    for _, pokemon_row in team_df.iterrows():
        pokemon_name = pokemon_row["name"]
        generation = int(pokemon_row["generation"])
        tier = pokemon_row["tier"]
        chosen_role = pokemon_row.get("chosen_role", "random")
        is_shiny = determine_shiny_status(pokemon_name, shiny_chance)

        pokemon_sets = sets_df[
            (sets_df["pokemon"] == pokemon_name) &
            (sets_df["generation"] == generation) &
            (sets_df["tier"] == tier)
        ].copy()

        if len(pokemon_sets) == 0:
            enriched_row = pokemon_row.to_dict()
            enriched_row.update({
                "set_name": "No generation-specific Smogon set found",
                "item": "",
                "ability": "",
                "nature": "",
                "tera_type": "",

                "ev_hp": 0,
                "ev_atk": 0,
                "ev_def": 0,
                "ev_spa": 0,
                "ev_spd": 0,
                "ev_spe": 0,

                "iv_hp": 31,
                "iv_atk": 31,
                "iv_def": 31,
                "iv_spa": 31,
                "iv_spd": 31,
                "iv_spe": 31,

                "move_1": "",
                "move_2": "",
                "move_3": "",
                "move_4": "",
                "shiny": is_shiny,
                "item_clause_warning": False
            })

            enriched_rows.append(enriched_row)
            continue

        selected_set = choose_set_for_pokemon(
            pokemon_sets=pokemon_sets,
            chosen_role=chosen_role,
            used_items=used_items,
            enforce_item_clause=enforce_item_clause
        )

        item = selected_set["item"]
        item_clause_warning = False

        if enforce_item_clause and item in used_items and item != "":
            item_clause_warning = True

        if item:
            used_items.add(item)

        enriched_row = pokemon_row.to_dict()

        enriched_row.update({
            "set_name": selected_set["set_name"],
            "format": selected_set["format"],
            "item": item,
            "ability": selected_set["ability"],
            "nature": selected_set["nature"],
            "tera_type": selected_set["tera_type"] if selected_set["tera_type"] else "",

            "ev_hp": selected_set["ev_hp"],
            "ev_atk": selected_set["ev_atk"],
            "ev_def": selected_set["ev_def"],
            "ev_spa": selected_set["ev_spa"],
            "ev_spd": selected_set["ev_spd"],
            "ev_spe": selected_set["ev_spe"],

            "iv_hp": selected_set["iv_hp"],
            "iv_atk": selected_set["iv_atk"],
            "iv_def": selected_set["iv_def"],
            "iv_spa": selected_set["iv_spa"],
            "iv_spd": selected_set["iv_spd"],
            "iv_spe": selected_set["iv_spe"],

            "move_1": selected_set["move_1"],
            "move_2": selected_set["move_2"],
            "move_3": selected_set["move_3"],
            "move_4": selected_set["move_4"],
            "shiny": is_shiny,
            "item_clause_warning": item_clause_warning
        })

        enriched_rows.append(enriched_row)

    return pd.DataFrame(enriched_rows)


def generate_role_based_team(
    df,
    template_name="Balanced",
    random_state=None,
    use_smogon_sets=True,
    enforce_item_clause=False,
    shiny_chance=1 / 6
):
    if random_state is not None:
        random.seed(random_state)

    if template_name == "Pure Random":
        team_df = generate_random_team(df, random_state=random_state)

        if use_smogon_sets:
            sets_df = load_pokemon_sets()
            team_df = attach_best_available_set(
                team_df,
                sets_df,
                enforce_item_clause=enforce_item_clause,
                shiny_chance=shiny_chance
            )

        return team_df

    required_roles = TEAM_TEMPLATES[template_name]

    selected_rows = []
    selected_names = set()

    for role in required_roles:
        candidates = df[
            df["roles"].apply(lambda roles: has_role(roles, role))
        ]

        candidates = candidates[
            ~candidates["name"].isin(selected_names)
        ]

        if len(candidates) == 0:
            continue

        selected = candidates.sample(
            n=1,
            random_state=random.randint(1, 999999)
        ).iloc[0]

        selected = selected.copy()
        selected["chosen_role"] = role

        selected_rows.append(selected)
        selected_names.add(selected["name"])

    team_df = pd.DataFrame(selected_rows)

    if len(team_df) < 6:
        remaining_pool = df[
            ~df["name"].isin(selected_names)
        ]

        needed = 6 - len(team_df)

        if len(remaining_pool) >= needed:
            filler = remaining_pool.sample(
                n=needed,
                random_state=random.randint(1, 999999)
            ).copy()

            filler["chosen_role"] = "filler"

            team_df = pd.concat([team_df, filler], ignore_index=True)

    team_df = team_df.reset_index(drop=True)

    if use_smogon_sets:
        sets_df = load_pokemon_sets()
        team_df = attach_best_available_set(
            team_df,
            sets_df,
            enforce_item_clause=enforce_item_clause,
            shiny_chance=shiny_chance
        )

    return team_df


def get_team_roles(team_df):
    role_counts = {}

    for roles in team_df["roles"]:
        for role in roles:
            role_counts[role] = role_counts.get(role, 0) + 1

    return role_counts


def get_missing_roles(team_df, template_name):
    if template_name == "Pure Random":
        return []

    required_roles = TEAM_TEMPLATES[template_name]
    team_roles = get_team_roles(team_df)

    missing_roles = [
        role for role in required_roles
        if role not in team_roles
    ]

    return missing_roles


def get_duplicate_items(team_df):
    if "item" not in team_df.columns:
        return {}

    item_counts = (
        team_df["item"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )

    duplicates = item_counts[item_counts > 1]

    return duplicates.to_dict()


if __name__ == "__main__":
    df = load_pokemon_data()
    test_df = filter_by_generation_and_tier(df, generation=3, tier="OU")

    team = generate_role_based_team(
        test_df,
        template_name="Pure Random",
        random_state=42,
        enforce_item_clause=False,
        shiny_chance=1 / 6
    )

    print("Generated Team:")
    print(team[[
        "generation",
        "name",
        "tier",
        "chosen_role",
        "set_name",
        "format",
        "item",
        "ability",
        "nature",
        "tera_type",
        "move_1",
        "move_2",
        "move_3",
        "move_4"
    ]])

    print("\nDuplicate Items:")
    print(get_duplicate_items(team))