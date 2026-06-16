import pandas as pd


def apply_filters(
    frame: pd.DataFrame,
    selected_priority_levels: list[str],
    selected_jobs: list[str],
    selected_months: list[str],
    selected_contacts: list[str],
    selected_age_groups: list[str],
) -> pd.DataFrame:
    if not any(
        (
            selected_priority_levels,
            selected_jobs,
            selected_months,
            selected_contacts,
            selected_age_groups,
        )
    ):
        return frame

    filtered = frame.copy()
    if selected_priority_levels:
        filtered = filtered[filtered["priority_level"].isin(selected_priority_levels)]
    if selected_jobs:
        filtered = filtered[filtered["job"].isin(selected_jobs)]
    if selected_months:
        filtered = filtered[filtered["month"].isin(selected_months)]
    if selected_contacts:
        filtered = filtered[filtered["contact"].isin(selected_contacts)]
    if selected_age_groups:
        filtered = filtered[filtered["age_group"].isin(selected_age_groups)]
    return filtered.reset_index(drop=True)


def default_selected_customer_id(frame: pd.DataFrame) -> int | None:
    if frame.empty:
        return None
    return int(frame.iloc[0]["customer_id"])
