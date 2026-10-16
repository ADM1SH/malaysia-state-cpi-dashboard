from typing import Dict, List
from pathlib import Path
import pandas as pd
from pydantic import BaseModel, Field

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "table_3_16_state_cpi.csv"

HYGR_TARGET_REGIONS: List[str] = [
    "Klang Valley",
    "Penang",
    "Sabah",
    "Sarawak",
]

URBAN_WEIGHT_MAP: Dict[str, float] = {
    "Federal Territory of Kuala Lumpur": 1.00,
    "Federal Territory of Putrajaya": 1.00,
    "Selangor": 0.92,
    "Pulau Pinang": 0.90,
    "Johor": 0.82,
    "Melaka": 0.80,
    "Negeri Sembilan": 0.75,
    "Perak": 0.72,
    "Kedah": 0.68,
    "Pahang": 0.65,
    "Terengganu": 0.64,
    "Perlis": 0.60,
    "Sabah": 0.58,
    "Sarawak": 0.57,
    "Kelantan": 0.52,
    "Federal Territory of Labuan": 0.85,
    "Malaysia": 0.78,
}

class StateCPIRecord(BaseModel):
    state: str
    region_group: str
    cpi_2022: float
    cpi_2023: float
    cpi_2024: float
    cpi_2025: float
    cpi_2026: float
    food_2022: float
    food_2023: float
    food_2024: float
    food_2025: float
    food_2026: float
    retail_pressure_index: float = Field(default=0.0)

def load_state_cpi_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

def compute_state_cpi_and_rpi() -> List[StateCPIRecord]:
    df = load_state_cpi_data()
    records: List[StateCPIRecord] = []

    for _, row in df.iterrows():
        state_name = str(row["state"])
        u_weight = URBAN_WEIGHT_MAP.get(state_name, 0.70)
        cum_cpi = (
            float(row["cpi_2022"])
            + float(row["cpi_2023"])
            + float(row["cpi_2024"])
            + float(row["cpi_2025"])
            + float(row["cpi_2026"])
        )
        cum_food = (
            float(row["food_2022"])
            + float(row["food_2023"])
            + float(row["food_2024"])
            + float(row["food_2025"])
            + float(row["food_2026"])
        )
        recent_momentum = 0.6 * float(row["cpi_2026"]) + 0.4 * float(row["food_2026"])
        rpi = round(
            0.35 * (cum_cpi / 5.0)
            + 0.35 * (cum_food / 5.0)
            + 0.20 * recent_momentum
            + 0.10 * (u_weight * 2.5),
            2,
        )
        records.append(
            StateCPIRecord(
                state=state_name,
                region_group=str(row["region_group"]),
                cpi_2022=float(row["cpi_2022"]),
                cpi_2023=float(row["cpi_2023"]),
                cpi_2024=float(row["cpi_2024"]),
                cpi_2025=float(row["cpi_2025"]),
                cpi_2026=float(row["cpi_2026"]),
                food_2022=float(row["food_2022"]),
                food_2023=float(row["food_2023"]),
                food_2024=float(row["food_2024"]),
                food_2025=float(row["food_2025"]),
                food_2026=float(row["food_2026"]),
                retail_pressure_index=rpi,
            )
        )
    return records

def get_hygr_regional_pressure_summary() -> pd.DataFrame:
    records = compute_state_cpi_and_rpi()
    df = pd.DataFrame([r.model_dump() for r in records])
    filtered = df[df["region_group"].isin(HYGR_TARGET_REGIONS)].copy()
    grouped = (
        filtered.groupby("region_group", as_index=False)
        .agg(
            states_covered=("state", lambda s: ", ".join(s)),
            cpi_2025=("cpi_2025", "mean"),
            cpi_2026=("cpi_2026", "mean"),
            food_2025=("food_2025", "mean"),
            food_2026=("food_2026", "mean"),
            retail_pressure_index=("retail_pressure_index", "mean"),
        )
        .round(2)
    )
    return grouped.sort_values("retail_pressure_index", ascending=False).reset_index(drop=True)
