# Oops All Sweepers

**Oops All Sweepers** is an unofficial, fan-made competitive Pokémon team builder, team randomizer and moveset browser.

The app lets users generate, browse, edit, analyze and export competitive Pokémon teams by **generation** and **tier**. It combines Smogon-style moveset data, Pokémon stats/types, role-based team generation, PMDCollab/SpriteCollab portraits, team analysis tools and Pokémon Showdown-compatible export.

The name is a joke about competitive teambuilding: sometimes, when you are not careful, a team accidentally becomes “oops, all sweepers.” Despite the name, the app supports many different roles, including walls, pivots, hazard setters, hazard removers, weather setters, wallbreakers, clerics, screen setters, phazers, revenge killers and more.

---

## Table of contents

- [Overview](#overview)
- [Main features](#main-features)
- [Screenshots](#screenshots)
- [Downloadable Windows app](#downloadable-windows-app)
- [Running from source](#running-from-source)
- [How the app works](#how-the-app-works)
- [Team Generator](#team-generator)
- [Set Browser](#set-browser)
- [Custom Team Builder](#custom-team-builder)
- [Manual Team Editor](#manual-team-editor)
- [Team analysis](#team-analysis)
- [Pokémon Showdown export](#pokémon-showdown-export)
- [Data sources](#data-sources)
- [Data update system](#data-update-system)
- [Project structure](#project-structure)
- [Building the Windows app](#building-the-windows-app)
- [Files not included in GitHub](#files-not-included-in-github)
- [Known limitations](#known-limitations)
- [Credits and disclaimer](#credits-and-disclaimer)
- [License / usage note](#license--usage-note)

---

## Overview

Oops All Sweepers is designed as a local teambuilding tool for competitive Pokémon fans.

It can be used in two main ways:

1. **Generate teams automatically**
   - Select a generation.
   - Select a tier.
   - Select a team style.
   - Generate a full team with sets, moves, EVs, IVs, items, abilities and roles.

2. **Build a custom team manually**
   - Browse available Smogon-style sets.
   - Add selected sets to a custom team.
   - Add Pokémon from generated teams.
   - Manually edit items, abilities, moves, EVs, IVs, Tera Type and shiny status.
   - Analyze the team.
   - Export the team to Pokémon Showdown.

The app runs locally in a browser using Streamlit. The downloadable Windows version starts the local app automatically through an `.exe`.

---

## Main features

### Team generation

- Generate full teams by generation and tier.
- Supports multiple team generation modes.
- Uses role-based templates for different playstyles.
- Selects matching Smogon-style sets for the correct generation and tier.
- Prevents Pokémon from receiving sets from the wrong generation.
- Supports optional Item Clause.
- Includes random shiny generation.
- Koffing, Weezing and Weezing-Galar are always shiny by design.

### Set browsing

- Browse sets by:
  - Generation
  - Tier
  - Role
  - Pokémon
  - Set name
- View moves, item, ability, nature, Tera Type, EVs and IVs.
- Add selected sets directly to a custom team.

### Custom teambuilding

- Add Pokémon from generated teams.
- Add Pokémon from the Set Browser.
- Remove individual Pokémon.
- Clear the full custom team.
- Edit team members manually.
- Analyze the custom team.
- Export the custom team to Pokémon Showdown format.

### Team analysis

- Type distribution chart.
- Offensive balance chart.
- Type weakness analysis.
- Shared weakness detection.
- Resistances and immunities overview.
- Chosen team role summary.
- Duplicate item detection.
- Average Speed and HP metrics.

### Export

- Exports generated and custom teams in a Pokémon Showdown-compatible text format.
- Includes moves, items, abilities, natures, EVs, IVs, Tera Type and shiny status when available.

---

## Credits, third-party software and disclaimer

Oops All Sweepers is an unofficial, non-commercial fan-made project. It uses external data, assets and open-source software. This project does not claim ownership of any Pokémon-related intellectual property, external assets, competitive data, or third-party software.

### Pokémon intellectual property

Pokémon, Pokémon names, moves, items, types, mechanics and related assets are trademarks or intellectual property of Nintendo, Game Freak and The Pokémon Company.

This project is not affiliated with, endorsed by, sponsored by, or officially connected to Nintendo, Game Freak, The Pokémon Company, Smogon, Pokémon Showdown, PMDCollab, SpriteCollab, or pkmn.

### PMDCollab / SpriteCollab portraits

Pokémon portraits are sourced from PMDCollab/SpriteCollab.

Full artist attribution is available in the official SpriteCollab credits file:

https://github.com/PMDCollab/SpriteCollab/blob/master/spritebot_credits.txt

Full credit belongs to the original SpriteCollab artists and contributors. This project does not claim ownership of any SpriteCollab portraits.

### Smogon-style moveset data

Moveset data is based on processed Smogon-style set data obtained through pkmn/smogon-style resources.

This project does not claim ownership of Smogon sets, analyses, competitive formats, or related data.

### Pokémon Showdown compatibility

Pokémon Showdown export formatting is included only for compatibility with Pokémon Showdown team import.

This project is not affiliated with Pokémon Showdown.

### Open-source Python libraries

This project is built with several open-source Python libraries, including:

- Streamlit — app interface and local web app framework
- pandas — data loading and manipulation
- Plotly — interactive charts
- requests — downloading remote data files
- PyInstaller — Windows app packaging
- Altair and PyArrow — dependencies used by Streamlit and the packaged app

All third-party libraries remain under their own licenses. Please refer to each project’s official license for full terms.

### Project source code

The source code written specifically for Oops All Sweepers may be shared for educational and portfolio purposes.

External Pokémon-related names, data, portraits, sprites, moves, items, types, mechanics, trademarks and third-party libraries remain the property of their respective owners.