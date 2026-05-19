# Oops All Sweepers

**Oops All Sweepers** is an unofficial, fan-made Pokémon team builder and randomizer for competitive teambuilding.

This project started as a personal passion project around competitive Pokémon. I built it to combine something I enjoy with practical coding practice in Python, data processing, app development, UI design, packaging, and GitHub release management.

The app lets users generate, browse, edit, analyze, and export competitive Pokémon teams by generation and tier.

---

## Features

- Generate competitive Pokémon teams by generation and tier
- Browse Smogon-inspired sets
- Add Pokémon from generated teams to a custom team
- Build and edit a custom team manually
- Edit moves, items, abilities, natures, Tera Types, EVs, IVs, and shiny status
- Analyze team roles, type distribution, offensive balance, and weaknesses
- Export teams directly to Pokémon Showdown format
- Uses Pokémon portraits from PMDCollab/SpriteCollab
- Includes update functionality for local data refreshes
- Packaged as a downloadable Windows app

---

## Screenshots

### Team Preview

The generated team is shown with portraits, set names, selected roles, and shiny status.

![Team Preview](screenshots/team_preview.png)

---

### Team Details

The app shows the selected Pokémon, types, roles, items, abilities, natures, Tera Types, and base stats.

![Team Details](screenshots/team_details.png)

---

### Moves, EVs and IVs

Moves are displayed separately from EV and IV spreads to keep the team overview readable.

![Moves, EVs and IVs](screenshots/moves_eviv.png)

---

### Type Analysis

The app analyzes type distribution, offensive balance, shared weaknesses, resistances, and immunities.

![Type Analysis](screenshots/type_analysis.png)

---

### Pokémon Showdown Export

Generated and custom teams can be copied directly into Pokémon Showdown.

![Pokémon Showdown Export](screenshots/smogon_export.png)

---

## Downloadable Windows App

A downloadable Windows version is available through the GitHub Releases page.

### How to run

1. Download `OopsAllSweepers_Windows.zip`.
2. Extract the full folder.
3. Open the extracted folder.
4. Double-click `OopsAllSweepers.exe`.

Do **not** move the `.exe` file out of the extracted folder. The executable depends on the internal files inside the same folder.

No Python, VS Code, Streamlit, or package installation is needed for the Windows release.

Windows SmartScreen may show a warning because the app is not code-signed.

---

## Running from Source

If you want to run the source code instead of using the Windows release:

```bash
git clone https://github.com/lukerodermond-bep/oops-all-sweepers.git
cd oops-all-sweepers
pip install -r requirements.txt
streamlit run app.py