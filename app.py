import random

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import (
    load_pokemon_data,
    get_available_generations,
    get_available_tiers,
    filter_by_generation_and_tier
)
from src.set_loader import load_pokemon_sets
from src.team_generator import (
    generate_role_based_team,
    TEAM_TEMPLATES,
    get_duplicate_items,
    determine_shiny_status
)
from src.type_analysis import (
    get_team_summary,
    generate_team_feedback,
    generate_weakness_feedback
)
from src.showdown_exporter import export_to_showdown
from src.portrait_utils import get_portrait_url
from src.update_data import update_all_data
from src.ability_utils import (
    get_single_regular_ability_from_pokeapi,
    infer_competitive_ability_from_row
)


MAX_TOTAL_EVS = 508
MAX_STAT_EVS = 252


TYPE_COLORS = {
    "Normal": "#A8A77A",
    "Fire": "#EE8130",
    "Water": "#6390F0",
    "Electric": "#F7D02C",
    "Grass": "#7AC74C",
    "Ice": "#96D9D6",
    "Fighting": "#C22E28",
    "Poison": "#A33EA1",
    "Ground": "#E2BF65",
    "Flying": "#A98FF3",
    "Psychic": "#F95587",
    "Bug": "#A6B91A",
    "Rock": "#B6A136",
    "Ghost": "#735797",
    "Dragon": "#6F35FC",
    "Dark": "#705746",
    "Steel": "#B7B7CE",
    "Fairy": "#D685AD",
}


st.set_page_config(
    page_title="Oops All Sweepers",
    page_icon="⚔️",
    layout="wide"
)


@st.dialog("Update application data")
def show_update_dialog():
    st.markdown(
        """
        This will update the local data used by the app.

        The update will:

        - Download the latest processed Smogon moveset data
        - Rebuild the local Pokémon dataset
        - Download the latest SpriteCollab credits file
        - Clear and refresh the app cache after completion

        This may take a few minutes, especially because the Pokémon dataset has to be rebuilt.
        The app may be temporarily unresponsive while the update is running.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        start_update = st.button("Start update")

    with col2:
        cancel_update = st.button("Cancel")

    if cancel_update:
        st.rerun()

    if start_update:
        with st.spinner("Updating data. This may take a few minutes..."):
            update_all_data()

        st.cache_data.clear()

        st.session_state.last_generated_team = None
        st.session_state.last_generated_seed = None
        st.session_state.last_generated_generation = None
        st.session_state.last_generated_tier = None
        st.session_state.last_generated_mode = None

        st.success("Data update completed successfully.")

        if st.button("Reload app"):
            st.rerun()


def initialize_session_state():
    if "custom_team" not in st.session_state:
        st.session_state.custom_team = []

    if "last_generated_team" not in st.session_state:
        st.session_state.last_generated_team = None

    if "last_generated_seed" not in st.session_state:
        st.session_state.last_generated_seed = None

    if "last_generated_generation" not in st.session_state:
        st.session_state.last_generated_generation = None

    if "last_generated_tier" not in st.session_state:
        st.session_state.last_generated_tier = None

    if "last_generated_mode" not in st.session_state:
        st.session_state.last_generated_mode = None

    if "active_page" not in st.session_state:
        st.session_state.active_page = "Team Generator"

    if "navigation_page" not in st.session_state:
        st.session_state.navigation_page = "Team Generator"


@st.cache_data
def load_data():
    return load_pokemon_data()


@st.cache_data
def load_sets():
    return load_pokemon_sets()


@st.cache_data(show_spinner=False)
def infer_single_regular_ability_from_api(pokemon_name):
    return get_single_regular_ability_from_pokeapi(pokemon_name)


def get_unique_roles_from_sets(sets_df):
    roles = set()

    for role_list in sets_df["roles"]:
        for role in role_list:
            if role:
                roles.add(role)

    return sorted(roles)


def build_custom_team_row(selected_set, tier_df, shiny_chance):
    pokemon_name = selected_set["pokemon"]

    matching_base_rows = tier_df[tier_df["name"] == pokemon_name]

    if matching_base_rows.empty:
        return None

    base_row = matching_base_rows.iloc[0].to_dict()

    set_roles = selected_set["roles"]
    chosen_role = set_roles[0] if len(set_roles) > 0 else "custom"

    is_shiny = determine_shiny_status(
        pokemon_name,
        shiny_chance=shiny_chance
    )

    custom_row = base_row.copy()

    custom_row.update({
        "chosen_role": chosen_role,
        "set_name": selected_set["set_name"],
        "format": selected_set["format"],
        "item": selected_set["item"],
        "ability": selected_set["ability"],
        "nature": selected_set["nature"],
        "tera_type": selected_set["tera_type"],
        "shiny": is_shiny,

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
        "item_clause_warning": False
    })

    return custom_row


def add_to_custom_team(custom_row):
    if custom_row is None:
        st.warning("Could not add this Pokémon because base data is missing.")
        return

    if len(st.session_state.custom_team) >= 6:
        st.warning("Your custom team already has 6 Pokémon.")
        return

    existing_names = [
        row["name"] for row in st.session_state.custom_team
    ]

    if custom_row["name"] in existing_names:
        st.warning("This Pokémon is already on your custom team.")
        return

    st.session_state.custom_team.append(custom_row)
    st.success(f"Added {custom_row['name']} to your custom team.")


def add_generated_row_to_custom_team(row):
    custom_row = row.to_dict()
    add_to_custom_team(custom_row)


def remove_from_custom_team(index):
    if 0 <= index < len(st.session_state.custom_team):
        removed = st.session_state.custom_team.pop(index)
        st.success(f"Removed {removed['name']} from your custom team.")


def clear_custom_team():
    st.session_state.custom_team = []
    st.success("Custom team cleared.")


def update_custom_team_member(index, updated_values):
    if 0 <= index < len(st.session_state.custom_team):
        for key, value in updated_values.items():
            st.session_state.custom_team[index][key] = value

        st.success(
            f"Updated {st.session_state.custom_team[index]['name']}."
        )


def is_missing_value(value):
    if pd.isna(value):
        return True

    value = str(value).strip()

    return value in [
        "",
        "nan",
        "None",
        "none",
        "NaN",
        "Not specified",
        "Not listed",
        "Flexible / not listed",
    ]


def infer_ability_from_known_sets(row):
    try:
        pokemon_name = row.get("name", row.get("pokemon", ""))
        generation = int(row.get("generation", 9))
        tier = row.get("tier", "")

        if pokemon_name == "":
            return None

        competitive_ability = infer_competitive_ability_from_row(row)

        if competitive_ability:
            return competitive_ability

        matching_sets = sets_df[
            (sets_df["pokemon"] == pokemon_name) &
            (sets_df["generation"] == generation)
        ].copy()

        if tier:
            tier_matching_sets = matching_sets[
                matching_sets["tier"] == tier
            ].copy()

            if not tier_matching_sets.empty:
                matching_sets = tier_matching_sets

        known_abilities = sorted(
            ability
            for ability in matching_sets["ability"].dropna().unique()
            if str(ability).strip() not in [
                "",
                "nan",
                "None",
                "none",
                "NaN",
                "Not specified",
                "Not listed",
            ]
        )

        if len(known_abilities) == 1:
            return known_abilities[0]

        if generation >= 3:
            api_ability = infer_single_regular_ability_from_api(pokemon_name)

            if api_ability:
                return api_ability

        return None

    except Exception:
        return None


def format_missing_display_value(column, row):
    generation = int(row.get("generation", 9))

    if column == "item":
        if generation == 1:
            return "N/A in Gen 1"
        return "Not listed"

    if column == "ability":
        if generation < 3:
            return "N/A before Gen 3"

        inferred_ability = infer_ability_from_known_sets(row)

        if inferred_ability:
            return f"Inferred: {inferred_ability}"

        return "Not listed"

    if column == "nature":
        if generation < 3:
            return "N/A before Gen 3"
        return "Not listed"

    if column == "tera_type":
        if generation < 9:
            return "N/A before Gen 9"
        return "Flexible / not listed"

    if column == "set_name":
        return "Not listed"

    return "Not listed"


def clean_display_columns(display_df):
    display_df = display_df.copy()

    display_columns = [
        "item",
        "ability",
        "nature",
        "tera_type",
        "set_name"
    ]

    for column in display_columns:
        if column not in display_df.columns:
            continue

        for index, row in display_df.iterrows():
            if is_missing_value(row.get(column, "")):
                display_df.at[index, column] = format_missing_display_value(
                    column,
                    row
                )

    return display_df


def prepare_team_for_showdown_export(team_df):
    export_df = team_df.copy()

    for index, row in export_df.iterrows():
        generation = int(row.get("generation", 9))
        current_ability = row.get("ability", "")

        if generation >= 3 and is_missing_value(current_ability):
            inferred_ability = infer_ability_from_known_sets(row)

            if inferred_ability:
                export_df.at[index, "ability"] = inferred_ability

    return export_df


def display_team_preview(
    team_df,
    image_width=80,
    allow_add_to_custom=False,
    key_prefix="team"
):
    preview_cols = st.columns(6)

    for index, (_, row) in enumerate(team_df.iterrows()):
        with preview_cols[index]:
            portrait_url = get_portrait_url(
                row["name"],
                shiny=bool(row.get("shiny", False))
            )

            if portrait_url:
                st.image(portrait_url, width=image_width)

            st.markdown(f"**{row['name']}**")
            st.caption(f"Set: {row.get('set_name', 'Not specified')}")
            st.caption(f"Role: {row.get('chosen_role', 'custom')}")

            if bool(row.get("shiny", False)):
                st.caption("Shiny: Yes")
            else:
                st.caption("Shiny: No")

            if allow_add_to_custom:
                if st.button(
                    "Add to Custom",
                    key=f"{key_prefix}_add_{index}_{row['name']}_{row.get('set_name', '')}"
                ):
                    add_generated_row_to_custom_team(row)


def display_team_details(team_df, title):
    st.subheader(title)

    display_df = team_df.copy()
    display_df = clean_display_columns(display_df)

    st.dataframe(
        display_df[
            [
                "generation",
                "name",
                "tier",
                "type_1",
                "type_2",
                "chosen_role",
                "set_name",
                "item",
                "ability",
                "nature",
                "tera_type",
                "shiny",
                "hp",
                "attack",
                "defense",
                "special_attack",
                "special_defense",
                "speed"
            ]
        ],
        width="stretch",
        hide_index=True
    )


def display_moveset_table(team_df):
    st.subheader("Moves")

    moves_df = team_df[
        [
            "generation",
            "tier",
            "name",
            "set_name",
            "item",
            "ability",
            "nature",
            "tera_type",
            "shiny",
            "move_1",
            "move_2",
            "move_3",
            "move_4"
        ]
    ].copy()

    moves_df = clean_display_columns(moves_df)

    st.dataframe(
        moves_df.drop(columns=["generation", "tier"]),
        width="stretch",
        hide_index=True
    )

    st.markdown("---")

    st.subheader("EVs and IVs")

    stats_df = team_df[
        [
            "name",
            "ev_hp",
            "ev_atk",
            "ev_def",
            "ev_spa",
            "ev_spd",
            "ev_spe",
            "iv_hp",
            "iv_atk",
            "iv_def",
            "iv_spa",
            "iv_spd",
            "iv_spe"
        ]
    ].copy()

    st.dataframe(
        stats_df,
        width="stretch",
        hide_index=True
    )


def display_team_analysis(team_df, template_name="Pure Random"):
    summary = get_team_summary(team_df, template_name)

    col1, col2, col3 = st.columns(3)

    col1.metric("Average Speed", summary["average_speed"])
    col2.metric("Average HP", summary["average_hp"])
    col3.metric("Missing Required Roles", len(summary["missing_roles"]))

    if summary["missing_roles"]:
        st.warning(
            "Missing roles: " + ", ".join(summary["missing_roles"])
        )
    else:
        st.success("All required roles for this team style are covered.")

    duplicate_items = get_duplicate_items(team_df)

    if duplicate_items:
        duplicate_text = ", ".join(
            [f"{item} ({count}x)" for item, count in duplicate_items.items()]
        )

        st.info(
            "Duplicate items detected: "
            + duplicate_text
            + ". This is usually allowed in Smogon formats."
        )
    else:
        st.success("No duplicate held items detected.")

    feedback = generate_team_feedback(summary)

    st.subheader("Team Quality Feedback")

    for item in feedback:
        st.write(f"- {item}")

    st.markdown("---")

    st.subheader("Chosen Team Roles")

    if "chosen_role" in team_df.columns:
        chosen_roles_df = (
            team_df["chosen_role"]
            .fillna("custom")
            .value_counts()
            .reset_index()
        )

        chosen_roles_df.columns = ["role", "count"]

        st.dataframe(
            chosen_roles_df,
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No chosen roles available for this team.")

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Type Distribution")

        type_df = pd.DataFrame(
            list(summary["type_distribution"].items()),
            columns=["type", "count"]
        )

        fig_type = px.bar(
            type_df,
            x="type",
            y="count",
            color="type",
            color_discrete_map=TYPE_COLORS,
            title="Team Type Distribution"
        )

        st.plotly_chart(fig_type, width="stretch")

    with chart_col2:
        st.subheader("Offensive Balance")

        balance_df = pd.DataFrame(
            list(summary["offensive_balance"].items()),
            columns=["category", "count"]
        )

        fig_balance = px.bar(
            balance_df,
            x="category",
            y="count",
            color="category",
            title="Physical / Special / Mixed Balance"
        )

        st.plotly_chart(fig_balance, width="stretch")

    st.markdown("---")

    st.subheader("Type Weakness Analysis")

    weakness_df = summary["weakness_analysis"]

    st.dataframe(
        weakness_df.sort_values(by="weak_count", ascending=False),
        width="stretch",
        hide_index=True
    )

    major_weaknesses = weakness_df[weakness_df["weak_count"] >= 3]

    if not major_weaknesses.empty:
        weakness_text = ", ".join(major_weaknesses["attacking_type"].tolist())
        st.warning(f"Potential shared weaknesses detected: {weakness_text}")
    else:
        st.success("No major shared type weaknesses detected.")

    weakness_feedback = generate_weakness_feedback(weakness_df)

    st.subheader("Weakness Feedback")

    for item in weakness_feedback:
        st.write(f"- {item}")


def display_generated_team_section(team_mode):
    if st.session_state.last_generated_team is None:
        st.info("Select a generation, tier and generation mode, then click 'Generate Team'.")
        return

    team_df = st.session_state.last_generated_team
    random_seed = st.session_state.last_generated_seed

    st.caption(
        f"Generated for Gen {st.session_state.last_generated_generation} "
        f"{st.session_state.last_generated_tier} using random seed {random_seed}."
    )

    st.subheader("Team Preview")
    display_team_preview(
        team_df,
        allow_add_to_custom=True,
        key_prefix="generated_team"
    )

    st.markdown("---")

    display_team_details(team_df, "Generated Team Details")

    st.markdown("---")

    display_moveset_table(team_df)

    st.markdown("---")

    display_team_analysis(
        team_df,
        template_name=st.session_state.last_generated_mode or team_mode
    )

    st.markdown("---")

    st.subheader("Pokémon Showdown Export")

    export_team_df = prepare_team_for_showdown_export(team_df)
    showdown_text = export_to_showdown(export_team_df)

    st.text_area(
        "Copy this team into Pokémon Showdown",
        showdown_text,
        height=450
    )


def display_set_browser(tier_sets_df, tier_df, selected_generation, selected_tier, shiny_chance):
    st.markdown(
        "Browse Smogon-inspired sets by generation, tier, role, Pokémon and set name."
    )

    if len(tier_sets_df) == 0:
        st.warning("No sets available for this generation and tier.")
        return

    available_roles = get_unique_roles_from_sets(tier_sets_df)

    role_filter = st.selectbox(
        "Filter by Role",
        options=["All"] + available_roles
    )

    filtered_sets_df = tier_sets_df.copy()

    if role_filter != "All":
        filtered_sets_df = filtered_sets_df[
            filtered_sets_df["roles"].apply(lambda roles: role_filter in roles)
        ]

    if len(filtered_sets_df) == 0:
        st.warning("No sets match the selected role filter.")
        return

    available_pokemon = sorted(filtered_sets_df["pokemon"].unique())

    selected_pokemon = st.selectbox(
        "Select Pokémon",
        options=available_pokemon
    )

    pokemon_sets_df = filtered_sets_df[
        filtered_sets_df["pokemon"] == selected_pokemon
    ].copy()

    selected_set_name = st.selectbox(
        "Select Set",
        options=sorted(pokemon_sets_df["set_name"].unique())
    )

    selected_set = pokemon_sets_df[
        pokemon_sets_df["set_name"] == selected_set_name
    ].iloc[0]

    st.subheader("Selected Set Details")

    col1, col2 = st.columns([1, 3])

    with col1:
        portrait_url = get_portrait_url(selected_pokemon, shiny=False)

        if portrait_url:
            st.image(portrait_url, width=100)

        st.markdown(f"**{selected_pokemon}**")
        st.caption(f"Gen {selected_generation} {selected_tier}")

        add_button = st.button("Add Selected Set to Custom Team")

        if add_button:
            custom_row = build_custom_team_row(
                selected_set=selected_set,
                tier_df=tier_df,
                shiny_chance=shiny_chance
            )

            add_to_custom_team(custom_row)

    with col2:
        set_details = pd.DataFrame([{
            "generation": selected_set["generation"],
            "tier": selected_set["tier"],
            "pokemon": selected_set["pokemon"],
            "set_name": selected_set["set_name"],
            "roles": ", ".join(selected_set["roles"]),
            "item": selected_set["item"],
            "ability": selected_set["ability"],
            "nature": selected_set["nature"],
            "tera_type": selected_set["tera_type"],
            "move_1": selected_set["move_1"],
            "move_2": selected_set["move_2"],
            "move_3": selected_set["move_3"],
            "move_4": selected_set["move_4"],
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
        }])

        set_details = clean_display_columns(set_details)

        st.dataframe(set_details, width="stretch", hide_index=True)

    st.markdown("---")

    st.subheader("Available Sets for Selected Pokémon")

    display_sets_df = pokemon_sets_df.copy()
    display_sets_df["roles"] = display_sets_df["roles"].apply(lambda roles: ", ".join(roles))
    display_sets_df = clean_display_columns(display_sets_df)

    st.dataframe(
        display_sets_df[
            [
                "generation",
                "tier",
                "pokemon",
                "set_name",
                "roles",
                "item",
                "ability",
                "nature",
                "tera_type",
                "move_1",
                "move_2",
                "move_3",
                "move_4"
            ]
        ],
        width="stretch",
        hide_index=True
    )


def display_basic_manual_editor(custom_team_df):
    st.subheader("Manual Team Editor")

    pokemon_options = [
        f"{index + 1}. {row['name']} - {row['set_name']}"
        for index, row in custom_team_df.iterrows()
    ]

    selected_option = st.selectbox(
        "Select a team member to edit",
        options=pokemon_options
    )

    selected_index = pokemon_options.index(selected_option)
    selected_row = custom_team_df.iloc[selected_index]

    with st.form("manual_team_editor_form"):
        st.markdown("### Basic Set Details")

        item = st.text_input(
            "Item",
            value=str(selected_row.get("item", ""))
        )

        ability = st.text_input(
            "Ability",
            value=str(selected_row.get("ability", ""))
        )

        nature = st.text_input(
            "Nature",
            value=str(selected_row.get("nature", ""))
        )

        tera_type = st.text_input(
            "Tera Type",
            value=str(selected_row.get("tera_type", ""))
        )

        shiny = st.checkbox(
            "Shiny",
            value=bool(selected_row.get("shiny", False))
        )

        st.markdown("### Moves")

        move_1 = st.text_input(
            "Move 1",
            value=str(selected_row.get("move_1", ""))
        )

        move_2 = st.text_input(
            "Move 2",
            value=str(selected_row.get("move_2", ""))
        )

        move_3 = st.text_input(
            "Move 3",
            value=str(selected_row.get("move_3", ""))
        )

        move_4 = st.text_input(
            "Move 4",
            value=str(selected_row.get("move_4", ""))
        )

        st.markdown("### EV Spread")

        ev_col1, ev_col2, ev_col3 = st.columns(3)

        with ev_col1:
            ev_hp = st.number_input(
                "EV HP",
                min_value=0,
                max_value=MAX_STAT_EVS,
                value=int(selected_row.get("ev_hp", 0)),
                step=4
            )

            ev_spa = st.number_input(
                "EV SpA",
                min_value=0,
                max_value=MAX_STAT_EVS,
                value=int(selected_row.get("ev_spa", 0)),
                step=4
            )

        with ev_col2:
            ev_atk = st.number_input(
                "EV Atk",
                min_value=0,
                max_value=MAX_STAT_EVS,
                value=int(selected_row.get("ev_atk", 0)),
                step=4
            )

            ev_spd = st.number_input(
                "EV SpD",
                min_value=0,
                max_value=MAX_STAT_EVS,
                value=int(selected_row.get("ev_spd", 0)),
                step=4
            )

        with ev_col3:
            ev_def = st.number_input(
                "EV Def",
                min_value=0,
                max_value=MAX_STAT_EVS,
                value=int(selected_row.get("ev_def", 0)),
                step=4
            )

            ev_spe = st.number_input(
                "EV Spe",
                min_value=0,
                max_value=MAX_STAT_EVS,
                value=int(selected_row.get("ev_spe", 0)),
                step=4
            )

        total_evs = ev_hp + ev_atk + ev_def + ev_spa + ev_spd + ev_spe

        if total_evs > MAX_TOTAL_EVS:
            st.error(
                f"EV total is {total_evs}. Maximum allowed usable EV total is {MAX_TOTAL_EVS}."
            )
        else:
            st.caption(f"EV total: {total_evs} / {MAX_TOTAL_EVS}")

        st.markdown("### IV Spread")

        iv_col1, iv_col2, iv_col3 = st.columns(3)

        with iv_col1:
            iv_hp = st.number_input(
                "IV HP",
                min_value=0,
                max_value=31,
                value=int(selected_row.get("iv_hp", 31)),
                step=1
            )

            iv_spa = st.number_input(
                "IV SpA",
                min_value=0,
                max_value=31,
                value=int(selected_row.get("iv_spa", 31)),
                step=1
            )

        with iv_col2:
            iv_atk = st.number_input(
                "IV Atk",
                min_value=0,
                max_value=31,
                value=int(selected_row.get("iv_atk", 31)),
                step=1
            )

            iv_spd = st.number_input(
                "IV SpD",
                min_value=0,
                max_value=31,
                value=int(selected_row.get("iv_spd", 31)),
                step=1
            )

        with iv_col3:
            iv_def = st.number_input(
                "IV Def",
                min_value=0,
                max_value=31,
                value=int(selected_row.get("iv_def", 31)),
                step=1
            )

            iv_spe = st.number_input(
                "IV Spe",
                min_value=0,
                max_value=31,
                value=int(selected_row.get("iv_spe", 31)),
                step=1
            )

        submitted = st.form_submit_button("Save Changes")

        if submitted:
            if total_evs > MAX_TOTAL_EVS:
                st.error(
                    f"Cannot save changes. EV total is {total_evs}, but the maximum allowed is {MAX_TOTAL_EVS}."
                )
                st.stop()

            updated_values = {
                "item": item,
                "ability": ability,
                "nature": nature,
                "tera_type": tera_type,
                "shiny": shiny,

                "move_1": move_1,
                "move_2": move_2,
                "move_3": move_3,
                "move_4": move_4,

                "ev_hp": ev_hp,
                "ev_atk": ev_atk,
                "ev_def": ev_def,
                "ev_spa": ev_spa,
                "ev_spd": ev_spd,
                "ev_spe": ev_spe,

                "iv_hp": iv_hp,
                "iv_atk": iv_atk,
                "iv_def": iv_def,
                "iv_spa": iv_spa,
                "iv_spd": iv_spd,
                "iv_spe": iv_spe,
            }

            update_custom_team_member(
                selected_index,
                updated_values
            )

            st.rerun()


def display_custom_team_builder():
    custom_team_df = pd.DataFrame(st.session_state.custom_team)

    if custom_team_df.empty:
        st.info("Your custom team is empty. Use the Set Browser, or add Pokémon from a generated team.")
        return

    st.subheader("Custom Team Preview")
    display_team_preview(custom_team_df)

    st.markdown("---")

    st.subheader("Custom Team Members")

    for index, row in custom_team_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        with col1:
            st.markdown(f"**{row['name']}**")

        with col2:
            st.write(row["set_name"])

        with col3:
            st.write(row["item"] if row["item"] else "No item")

        with col4:
            if st.button("Remove", key=f"remove_custom_{index}"):
                remove_from_custom_team(index)
                st.rerun()

    if st.button("Clear Custom Team"):
        clear_custom_team()
        st.rerun()

    st.markdown("---")

    display_basic_manual_editor(custom_team_df)

    st.markdown("---")

    display_team_details(custom_team_df, "Custom Team Details")

    st.markdown("---")

    display_moveset_table(custom_team_df)

    st.markdown("---")

    st.subheader("Custom Team Analysis")
    display_team_analysis(custom_team_df, template_name="Pure Random")

    st.markdown("---")

    st.subheader("Custom Team Pokémon Showdown Export")

    export_custom_team_df = prepare_team_for_showdown_export(custom_team_df)
    custom_showdown_text = export_to_showdown(export_custom_team_df)

    st.text_area(
        "Copy this custom team into Pokémon Showdown",
        custom_showdown_text,
        height=450
    )


initialize_session_state()

df = load_data()
sets_df = load_sets()

st.title("Oops All Sweepers")

st.markdown(
    "Generate, browse, edit and export competitive Pokémon teams by generation and tier."
)

st.sidebar.header("Team Settings")
st.sidebar.caption(f"Loaded Smogon sets: {len(sets_df)}")

selected_generation = st.sidebar.selectbox(
    "Select Generation",
    get_available_generations(df),
    format_func=lambda generation: f"Gen {generation}"
)

available_tiers = get_available_tiers(df, generation=selected_generation)

selected_tier = st.sidebar.selectbox(
    "Select Tier",
    available_tiers
)

team_mode = st.sidebar.selectbox(
    "Select Generation Mode",
    list(TEAM_TEMPLATES.keys())
)

enforce_item_clause = st.sidebar.checkbox(
    "Enforce Item Clause",
    value=False,
    help=(
        "When enabled, the generator tries to avoid duplicate held items. "
        "Smogon formats normally do not require this."
    )
)

shiny_chance = st.sidebar.slider(
    "Random Shiny Chance",
    min_value=0.0,
    max_value=1.0,
    value=1 / 6,
    step=0.01,
    help="Chance that each generated Pokémon is shiny. Koffing and Weezing are always shiny."
)

st.sidebar.markdown("---")

generate_button = st.sidebar.button("Generate Team")

st.sidebar.markdown("---")

with st.sidebar.expander("Advanced data options"):
    st.caption(
        "Refresh Smogon movesets, Pokémon data and SpriteCollab credits. "
        "This may take a few minutes."
    )

    if st.button("Update Data"):
        show_update_dialog()

tier_df = filter_by_generation_and_tier(
    df,
    generation=selected_generation,
    tier=selected_tier
)

tier_sets_df = sets_df[
    (sets_df["generation"] == selected_generation) &
    (sets_df["tier"] == selected_tier)
].copy()

if generate_button:
    random_seed = random.randint(1, 999999)

    team_df = generate_role_based_team(
        tier_df,
        template_name=team_mode,
        random_state=random_seed,
        enforce_item_clause=enforce_item_clause,
        shiny_chance=shiny_chance
    )

    st.session_state.last_generated_team = team_df
    st.session_state.last_generated_seed = random_seed
    st.session_state.last_generated_generation = selected_generation
    st.session_state.last_generated_tier = selected_tier
    st.session_state.last_generated_mode = team_mode

    st.session_state.active_page = "Team Generator"
    st.session_state.navigation_page = "Team Generator"

page_options = [
    "Team Generator",
    "Set Browser",
    "Custom Team Builder"
]

if st.session_state.navigation_page not in page_options:
    st.session_state.navigation_page = "Team Generator"

active_page = st.radio(
    "Navigation",
    page_options,
    key="navigation_page",
    horizontal=True,
    label_visibility="collapsed"
)

st.session_state.active_page = active_page

if active_page == "Team Generator":
    display_generated_team_section(team_mode)

elif active_page == "Set Browser":
    display_set_browser(
        tier_sets_df=tier_sets_df,
        tier_df=tier_df,
        selected_generation=selected_generation,
        selected_tier=selected_tier,
        shiny_chance=shiny_chance
    )

elif active_page == "Custom Team Builder":
    display_custom_team_builder()

st.markdown("---")

st.markdown(
    """
##### Credits and disclaimer

**Portraits:** Pokémon portraits are sourced from PMDCollab/SpriteCollab. Full artist attribution is available in the official SpriteCollab `spritebot_credits.txt` credits file.  
**Moveset data:** Moveset data is based on pkmn/smogon processed Smogon set data.  
**Built with:** Streamlit, pandas, Plotly, requests and PyInstaller.  
**Showdown export:** Export formatting is provided for compatibility with Pokémon Showdown team import.  

**Disclaimer:** Pokémon, Pokémon names, moves, items, types and related assets are trademarks of Nintendo, Game Freak and The Pokémon Company. This is an unofficial, non-commercial, fan-made project and is not affiliated with, endorsed by, or sponsored by Nintendo, Game Freak, The Pokémon Company, Smogon, Pokémon Showdown, PMDCollab, SpriteCollab or pkmn.
"""
)