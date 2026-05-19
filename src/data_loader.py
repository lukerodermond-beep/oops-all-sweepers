import pandas as pd

from src.path_utils import get_data_path


def load_pokemon_data(path=None):
    if path is None:
        path = get_data_path("pokemon_data.csv")

    df = pd.read_csv(path)

    df["type_2"] = (
        df["type_2"]
        .fillna("-")
        .replace(["None", "none", "NaN", "nan"], "-")
    )

    df["roles"] = df["roles"].fillna("").apply(
        lambda x: x.split(";") if x else []
    )

    df["generation"] = df["generation"].astype(int)

    return df


def get_available_generations(df):
    return sorted([int(gen) for gen in df["generation"].unique()], reverse=True)


def get_available_tiers(df, generation=None):
    if generation is not None:
        df = df[df["generation"] == generation]

    return sorted(df["tier"].unique())


def filter_by_tier(df, tier):
    return df[df["tier"] == tier].copy()


def filter_by_generation_and_tier(df, generation, tier):
    return df[
        (df["generation"] == generation) &
        (df["tier"] == tier)
    ].copy()


if __name__ == "__main__":
    pokemon_df = load_pokemon_data()

    print("Dataset loaded successfully")
    print(f"Number of Pokémon: {len(pokemon_df)}")
    print(f"Available generations: {get_available_generations(pokemon_df)}")
    print(f"Available tiers: {get_available_tiers(pokemon_df)}")
    print(pokemon_df.head())