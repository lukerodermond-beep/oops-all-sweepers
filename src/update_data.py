from pathlib import Path
import requests

from src import fetch_smogon_sets
from src import build_pokemon_data


SPRITECOLLAB_CREDITS_URL = (
    "https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/spritebot_credits.txt"
)


def download_spritecollab_credits(output_path="data/spritebot_credits.txt"):
    Path("data").mkdir(exist_ok=True)

    response = requests.get(SPRITECOLLAB_CREDITS_URL, timeout=30)
    response.raise_for_status()

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(response.text)

    print(f"Downloaded SpriteCollab credits to: {output_path}")


def update_all_data():
    print("Starting data update...")

    print("\nStep 1/3: Fetching latest Smogon set data...")
    fetch_smogon_sets.main()

    print("\nStep 2/3: Rebuilding Pokémon base data...")
    build_pokemon_data.build_pokemon_data()

    print("\nStep 3/3: Downloading latest SpriteCollab credits...")
    download_spritecollab_credits()

    print("\nData update completed successfully.")


if __name__ == "__main__":
    update_all_data()