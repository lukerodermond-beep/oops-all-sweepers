from src.data_loader import load_pokemon_data, filter_by_tier
from src.team_generator import generate_role_based_team


def format_evs(row):
    ev_fields = [
        ("HP", row.get("ev_hp", 0)),
        ("Atk", row.get("ev_atk", 0)),
        ("Def", row.get("ev_def", 0)),
        ("SpA", row.get("ev_spa", 0)),
        ("SpD", row.get("ev_spd", 0)),
        ("Spe", row.get("ev_spe", 0)),
    ]

    parts = [
        f"{int(value)} {label}"
        for label, value in ev_fields
        if int(value) > 0
    ]

    return " / ".join(parts)


def format_ivs(row):
    iv_fields = [
        ("HP", row.get("iv_hp", 31)),
        ("Atk", row.get("iv_atk", 31)),
        ("Def", row.get("iv_def", 31)),
        ("SpA", row.get("iv_spa", 31)),
        ("SpD", row.get("iv_spd", 31)),
        ("Spe", row.get("iv_spe", 31)),
    ]

    parts = [
        f"{int(value)} {label}"
        for label, value in iv_fields
        if int(value) < 31
    ]

    return " / ".join(parts)


def export_to_showdown(team_df):
    showdown_text = ""

    for _, row in team_df.iterrows():
        name = row["name"]
        item = row.get("item", "")
        ability = row.get("ability", "")
        nature = row.get("nature", "")
        tera_type = row.get("tera_type", row.get("type_1", ""))
        shiny = row.get("shiny", False)

        move_1 = row.get("move_1", "")
        move_2 = row.get("move_2", "")
        move_3 = row.get("move_3", "")
        move_4 = row.get("move_4", "")

        if item:
            showdown_text += f"{name} @ {item}\n"
        else:
            showdown_text += f"{name}\n"

        if ability:
            showdown_text += f"Ability: {ability}\n"

        if shiny:
            showdown_text += "Shiny: Yes\n"

        if tera_type:
            showdown_text += f"Tera Type: {tera_type}\n"

        ev_text = format_evs(row)
        if ev_text:
            showdown_text += f"EVs: {ev_text}\n"

        if nature:
            showdown_text += f"{nature} Nature\n"

        iv_text = format_ivs(row)
        if iv_text:
            showdown_text += f"IVs: {iv_text}\n"

        for move in [move_1, move_2, move_3, move_4]:
            if move:
                showdown_text += f"- {move}\n"

        showdown_text += "\n"

    return showdown_text.strip()


if __name__ == "__main__":
    df = load_pokemon_data()
    ou_df = filter_by_tier(df, "OU")

    team = generate_role_based_team(
        ou_df,
        template_name="Balanced",
        random_state=42,
        shiny_chance=1 / 6
    )

    print(export_to_showdown(team))