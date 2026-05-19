import pandas as pd

from src.path_utils import get_data_path


def parse_roles(role_string):
    if pd.isna(role_string) or role_string == "":
        return []

    return [
        role.strip()
        for role in str(role_string).split(";")
        if role.strip()
    ]


def load_pokemon_sets(path=None):
    if path is None:
        path = get_data_path("pokemon_sets.csv")

    sets_df = pd.read_csv(path)

    sets_df["roles"] = sets_df["roles"].apply(parse_roles)
    sets_df["generation"] = sets_df["generation"].astype(int)

    text_columns = [
        "pokemon",
        "set_name",
        "format",
        "tier",
        "item",
        "ability",
        "nature",
        "tera_type",
        "move_1",
        "move_2",
        "move_3",
        "move_4",
    ]

    for column in text_columns:
        if column in sets_df.columns:
            sets_df[column] = sets_df[column].fillna("")

    return sets_df


if __name__ == "__main__":
    sets_df = load_pokemon_sets()

    print("Smogon sets loaded successfully")
    print(f"Number of sets: {len(sets_df)}")
    print(sets_df.head())