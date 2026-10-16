from src.cpi_model import compute_state_cpi_and_rpi, get_hygr_regional_pressure_summary

def test_state_cpi_records():
    records = compute_state_cpi_and_rpi()
    assert len(records) == 17
    assert all(r.retail_pressure_index > 0 for r in records)

def test_hygr_regional_summary():
    df = get_hygr_regional_pressure_summary()
    assert set(df["region_group"]) == {"Klang Valley", "Penang", "Sabah", "Sarawak"}
    assert len(df) == 4
