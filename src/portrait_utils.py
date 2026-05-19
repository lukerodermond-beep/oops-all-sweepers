import requests
from functools import lru_cache


BASE_PORTRAIT_URL = (
    "https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/portrait"
)

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

    "Ogerpon-Wellspring": "ogerpon-wellspring-mask",
    "Ogerpon-Hearthflame": "ogerpon-hearthflame-mask",
    "Ogerpon-Cornerstone": "ogerpon-cornerstone-mask",

    "Tauros-Paldea-Aqua": "tauros-paldea-aqua-breed",
    "Tauros-Paldea-Blaze": "tauros-paldea-blaze-breed",
    "Tauros-Paldea-Combat": "tauros-paldea-combat-breed",

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


PORTRAIT_FORM_CANDIDATES = {
    "Ogerpon-Wellspring": ["0001", "0002", "0003", "0004", "0005", "0006", "0007"],
    "Ogerpon-Hearthflame": ["0002", "0001", "0003", "0004", "0005", "0006", "0007"],
    "Ogerpon-Cornerstone": ["0003", "0004", "0002", "0001", "0005", "0006", "0007"],

    "Tornadus-Therian": ["0001", "0002"],
    "Thundurus-Therian": ["0001", "0002"],
    "Landorus-Therian": ["0001", "0002"],
    "Enamorus-Therian": ["0001", "0002"],

    "Calyrex-Ice": ["0001", "0002", "0003"],
    "Calyrex-Shadow": ["0002", "0001", "0003"],

    "Zacian-Crowned": ["0001", "0002"],
    "Zamazenta-Crowned": ["0001", "0002"],

    "Giratina-Origin": ["0001", "0002"],
    "Dialga-Origin": ["0001", "0002"],
    "Palkia-Origin": ["0001", "0002"],

    "Kyurem-Black": ["0001", "0002"],
    "Kyurem-White": ["0002", "0001"],

    "Necrozma-Dusk-Mane": ["0001", "0002", "0003"],
    "Necrozma-Dawn-Wings": ["0002", "0001", "0003"],

    "Hoopa-Unbound": ["0001", "0002"],

    "Indeedee-F": ["0001", "0002"],
    "Basculegion-F": ["0001", "0002"],
    "Basculegion-M": ["0000", "0001"],

    "Urshifu-Rapid-Strike": ["0001", "0002"],
    "Urshifu-Single-Strike": ["0000", "0001"],

    "Toxtricity-Low-Key": ["0001", "0002"],

    "Maushold-Four": ["0001", "0002"],
    "Maushold-Three": ["0000", "0001"],

    "Dudunsparce-Three-Segment": ["0001", "0002"],
    "Dudunsparce-Two-Segment": ["0000", "0001"],

    "Weezing-Galar": ["0001", "0002"],
    "Slowking-Galar": ["0001", "0002"],
    "Slowbro-Galar": ["0001", "0002"],
    "Zapdos-Galar": ["0001", "0002"],
    "Moltres-Galar": ["0001", "0002"],
    "Articuno-Galar": ["0001", "0002"],

    "Tauros-Paldea-Aqua": ["0002", "0001", "0003"],
    "Tauros-Paldea-Blaze": ["0003", "0001", "0002"],
    "Tauros-Paldea-Combat": ["0001", "0002", "0003"],
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


def extract_species_id_from_url(species_url):
    parts = species_url.rstrip("/").split("/")
    return int(parts[-1])


@lru_cache(maxsize=1000)
def get_pokedex_number(pokemon_name):
    """
    Uses the Pokémon species ID, not the form-specific Pokémon ID.
    This matters for forms such as Tornadus-Therian, Ogerpon-Cornerstone,
    Zacian-Crowned, etc.
    """
    api_name = smogon_name_to_pokeapi_name(pokemon_name)
    url = f"{POKEAPI_BASE_URL}/{api_name}"

    try:
        response = requests.get(url, timeout=15)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()

    species = data.get("species", {})
    species_url = species.get("url")

    if species_url:
        try:
            return extract_species_id_from_url(species_url)
        except ValueError:
            pass

    return data.get("id")


def format_pokedex_folder(pokedex_number):
    return str(pokedex_number).zfill(4)


@lru_cache(maxsize=20000)
def url_exists(url):
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)

        if response.status_code == 200:
            return True

        response = requests.get(url, timeout=10, stream=True)
        return response.status_code == 200

    except requests.RequestException:
        return False


def get_first_existing_url(candidates):
    for url in candidates:
        if url_exists(url):
            return url

    return None


def get_base_normal_candidates(folder):
    return [
        f"{BASE_PORTRAIT_URL}/{folder}/Normal.png",
        f"{BASE_PORTRAIT_URL}/{folder}/0000/Normal.png",
    ]


def get_base_shiny_candidates(folder):
    return [
        # Most likely shiny paths for base form.
        f"{BASE_PORTRAIT_URL}/{folder}/0000/0001/Normal.png",
        f"{BASE_PORTRAIT_URL}/{folder}/0000/0000/0001/Normal.png",

        # Fallback shiny-style names, if present.
        f"{BASE_PORTRAIT_URL}/{folder}/Shiny.png",
        f"{BASE_PORTRAIT_URL}/{folder}/0000/Shiny.png",
    ]


def get_form_normal_candidates(folder, form_folder):
    return [
        f"{BASE_PORTRAIT_URL}/{folder}/{form_folder}/Normal.png",
        f"{BASE_PORTRAIT_URL}/{folder}/{form_folder}/0000/Normal.png",
    ]


def get_form_shiny_candidates(folder, form_folder):
    return [
        # Most likely shiny paths inside a specific form folder.
        f"{BASE_PORTRAIT_URL}/{folder}/{form_folder}/0001/Normal.png",
        f"{BASE_PORTRAIT_URL}/{folder}/{form_folder}/0000/0001/Normal.png",

        # Fallback shiny-style names, if present.
        f"{BASE_PORTRAIT_URL}/{folder}/{form_folder}/Shiny.png",
        f"{BASE_PORTRAIT_URL}/{folder}/{form_folder}/0000/Shiny.png",
    ]


def get_form_portrait_url(pokemon_name, folder, shiny=False):
    form_folders = PORTRAIT_FORM_CANDIDATES.get(pokemon_name, [])

    for form_folder in form_folders:
        if shiny:
            shiny_url = get_first_existing_url(
                get_form_shiny_candidates(folder, form_folder)
            )

            if shiny_url:
                return shiny_url

        normal_url = get_first_existing_url(
            get_form_normal_candidates(folder, form_folder)
        )

        if normal_url:
            return normal_url

    return None


def get_base_portrait_url(folder, shiny=False):
    if shiny:
        shiny_url = get_first_existing_url(get_base_shiny_candidates(folder))

        if shiny_url:
            return shiny_url

    return get_first_existing_url(get_base_normal_candidates(folder))


def get_portrait_url(pokemon_name, shiny=False):
    pokedex_number = get_pokedex_number(pokemon_name)

    if pokedex_number is None:
        return None

    folder = format_pokedex_folder(pokedex_number)

    form_url = get_form_portrait_url(
        pokemon_name,
        folder,
        shiny=shiny
    )

    if form_url:
        return form_url

    return get_base_portrait_url(folder, shiny=shiny)


if __name__ == "__main__":
    test_names = [
        "Clefable",
        "Bulbasaur",
        "Weezing",
        "Weezing-Galar",
        "Mewtwo",
        "Great Tusk",
        "Ribombee",
        "Calyrex-Ice",
        "Magearna",
        "Ogerpon-Cornerstone",
        "Ogerpon-Wellspring",
        "Tornadus-Therian",
        "Landorus-Therian",
        "Zacian-Crowned",
    ]

    for name in test_names:
        print(name)
        print("Normal:", get_portrait_url(name, shiny=False))
        print("Shiny:", get_portrait_url(name, shiny=True))
        print()