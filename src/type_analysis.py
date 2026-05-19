import pandas as pd

from src.data_loader import load_pokemon_data, filter_by_generation_and_tier
from src.path_utils import get_data_path


def get_type_distribution(team_df):
    type_counts = {}

    for _, row in team_df.iterrows():
        type_1 = row.get("type_1", "-")
        type_2 = row.get("type_2", "-")

        if pd.notna(type_1) and type_1 != "-":
            type_counts[type_1] = type_counts.get(type_1, 0) + 1

        if pd.notna(type_2) and type_2 != "-":
            type_counts[type_2] = type_counts.get(type_2, 0) + 1

    return type_counts


def get_offensive_balance(team_df):
    physical_roles = [
        "physical_attacker",
        "physical_wallbreaker",
    ]

    special_roles = [
        "special_attacker",
        "special_wallbreaker",
    ]

    mixed_roles = [
        "mixed_attacker",
    ]

    physical_count = 0
    special_count = 0
    mixed_count = 0

    for roles in team_df["roles"]:
        if any(role in roles for role in physical_roles):
            physical_count += 1

        if any(role in roles for role in special_roles):
            special_count += 1

        if any(role in roles for role in mixed_roles):
            mixed_count += 1

    return {
        "physical_attackers": physical_count,
        "special_attackers": special_count,
        "mixed_attackers": mixed_count,
    }


def get_team_roles(team_df):
    role_counts = {}

    for roles in team_df["roles"]:
        for role in roles:
            role_counts[role] = role_counts.get(role, 0) + 1

    return role_counts


def get_missing_roles(team_df, template_name):
    from src.team_generator import TEAM_TEMPLATES

    if template_name == "Pure Random":
        return []

    required_roles = TEAM_TEMPLATES.get(template_name, [])
    team_roles = get_team_roles(team_df)

    missing_roles = [
        role for role in required_roles
        if role not in team_roles
    ]

    return missing_roles


def load_type_chart(path=None):
    if path is None:
        path = get_data_path("type_chart.csv")

    type_chart = pd.read_csv(path)

    rename_map = {}

    if "attack_type" in type_chart.columns:
        rename_map["attack_type"] = "attacking_type"

    if "attacker_type" in type_chart.columns:
        rename_map["attacker_type"] = "attacking_type"

    if "defense_type" in type_chart.columns:
        rename_map["defense_type"] = "defending_type"

    if "defender_type" in type_chart.columns:
        rename_map["defender_type"] = "defending_type"

    if "defend_type" in type_chart.columns:
        rename_map["defend_type"] = "defending_type"

    type_chart = type_chart.rename(columns=rename_map)

    required_columns = ["attacking_type", "defending_type", "multiplier"]

    missing_columns = [
        column for column in required_columns
        if column not in type_chart.columns
    ]

    if missing_columns:
        raise ValueError(
            "type_chart.csv is missing required columns: "
            + ", ".join(missing_columns)
        )

    type_chart["attacking_type"] = type_chart["attacking_type"].astype(str).str.title()
    type_chart["defending_type"] = type_chart["defending_type"].astype(str).str.title()
    type_chart["multiplier"] = pd.to_numeric(type_chart["multiplier"])

    return type_chart


def get_type_multiplier(attacking_type, defending_type, type_chart):
    if defending_type == "-" or pd.isna(defending_type):
        return 1.0

    match = type_chart[
        (type_chart["attacking_type"] == attacking_type) &
        (type_chart["defending_type"] == defending_type)
    ]

    if match.empty:
        return 1.0

    return float(match.iloc[0]["multiplier"])


def get_combined_type_multiplier(attacking_type, type_1, type_2, type_chart):
    multiplier_1 = get_type_multiplier(
        attacking_type,
        type_1,
        type_chart
    )

    multiplier_2 = get_type_multiplier(
        attacking_type,
        type_2,
        type_chart
    )

    return multiplier_1 * multiplier_2


def analyze_team_weaknesses(team_df):
    type_chart = load_type_chart()

    attacking_types = sorted(type_chart["attacking_type"].unique())

    weakness_summary = []

    for attacking_type in attacking_types:
        weak_count = 0
        resist_count = 0
        immune_count = 0
        neutral_count = 0

        for _, row in team_df.iterrows():
            type_1 = row.get("type_1", "-")
            type_2 = row.get("type_2", "-")

            combined_multiplier = get_combined_type_multiplier(
                attacking_type,
                type_1,
                type_2,
                type_chart
            )

            if combined_multiplier == 0:
                immune_count += 1
            elif combined_multiplier > 1:
                weak_count += 1
            elif combined_multiplier < 1:
                resist_count += 1
            else:
                neutral_count += 1

        weakness_summary.append({
            "attacking_type": attacking_type,
            "weak_count": weak_count,
            "resist_count": resist_count,
            "immune_count": immune_count,
            "neutral_count": neutral_count,
        })

    return pd.DataFrame(weakness_summary)


def generate_team_feedback(summary):
    feedback = []

    average_speed = summary["average_speed"]
    offensive_balance = summary["offensive_balance"]
    missing_roles = summary["missing_roles"]

    if average_speed < 70:
        feedback.append(
            "The team is relatively slow. Consider adding more speed control or a faster attacker."
        )
    elif average_speed >= 100:
        feedback.append(
            "The team has strong overall speed, which can help with offensive pressure."
        )
    else:
        feedback.append(
            "The team has a reasonable average speed."
        )

    if offensive_balance["physical_attackers"] == 0:
        feedback.append(
            "The team may lack physical attacking pressure."
        )

    if offensive_balance["special_attackers"] == 0:
        feedback.append(
            "The team may lack special attacking pressure."
        )

    if (
        offensive_balance["physical_attackers"] > 0 and
        offensive_balance["special_attackers"] > 0
    ):
        feedback.append(
            "The team has some offensive variety between physical and special pressure."
        )

    if missing_roles:
        feedback.append(
            "Some expected roles are missing for this team style: "
            + ", ".join(missing_roles)
            + "."
        )
    else:
        feedback.append(
            "The team covers all required roles for the selected team style."
        )

    return feedback


def generate_weakness_feedback(weakness_df):
    feedback = []

    shared_weaknesses = weakness_df[
        weakness_df["weak_count"] >= 3
    ]

    strong_resistances = weakness_df[
        weakness_df["resist_count"] >= 3
    ]

    useful_immunities = weakness_df[
        weakness_df["immune_count"] >= 1
    ]

    if not shared_weaknesses.empty:
        weakness_text = ", ".join(
            shared_weaknesses["attacking_type"].tolist()
        )

        feedback.append(
            f"Potential shared weaknesses detected against: {weakness_text}."
        )
    else:
        feedback.append(
            "No major shared type weaknesses were detected."
        )

    if not strong_resistances.empty:
        resistance_text = ", ".join(
            strong_resistances["attacking_type"].tolist()
        )

        feedback.append(
            f"The team has strong defensive coverage against: {resistance_text}."
        )

    if not useful_immunities.empty:
        immunity_text = ", ".join(
            useful_immunities["attacking_type"].tolist()
        )

        feedback.append(
            f"The team includes useful immunities against: {immunity_text}."
        )

    return feedback


def get_team_summary(team_df, template_name):
    type_distribution = get_type_distribution(team_df)
    offensive_balance = get_offensive_balance(team_df)
    team_roles = get_team_roles(team_df)
    missing_roles = get_missing_roles(team_df, template_name)

    average_speed = round(team_df["speed"].mean(), 1)
    average_hp = round(team_df["hp"].mean(), 1)

    weakness_analysis = analyze_team_weaknesses(team_df)

    return {
        "type_distribution": type_distribution,
        "offensive_balance": offensive_balance,
        "team_roles": team_roles,
        "missing_roles": missing_roles,
        "average_speed": average_speed,
        "average_hp": average_hp,
        "weakness_analysis": weakness_analysis,
    }


if __name__ == "__main__":
    df = load_pokemon_data()
    team_df = filter_by_generation_and_tier(
        df,
        generation=9,
        tier="OU"
    ).head(6)

    summary = get_team_summary(team_df, "Balanced")

    print("Type Distribution:")
    print(summary["type_distribution"])

    print("\nOffensive Balance:")
    print(summary["offensive_balance"])

    print("\nTeam Roles:")
    print(summary["team_roles"])

    print("\nMissing Roles:")
    print(summary["missing_roles"])

    print("\nAverage Speed:")
    print(summary["average_speed"])

    print("\nAverage HP:")
    print(summary["average_hp"])

    print("\nWeakness Analysis:")
    print(summary["weakness_analysis"].head())

    print("\nWeakness Feedback:")
    for item in generate_weakness_feedback(summary["weakness_analysis"]):
        print(f"- {item}")