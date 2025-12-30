import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# REAL-WORLD DATA GENERATION (US CENSUS & FRED SOURCES)
# -----------------------------------------------------------------------------
# This script creates the CSV files required for population_analysis.py
# using data approximated from official sources (2000-2023).

def interpolate_series(anchors, index):
    """Interpolates values between anchor points."""
    s = pd.Series(np.nan, index=index)
    for year, val in anchors.items():
        if year in index:
            s.loc[year] = val
    return s.interpolate(method='linear')

years = np.arange(2000, 2024)

# 1. OFFICIAL POPULATION (Source: US Census Bureau / FRED POPTHM)
# Anchors: 2000 Census, 2010 Census, 2020 Census, 2023 Estimate
pop_anchors = {
    2000: 282_162_411,
    2010: 308_745_538,
    2020: 331_449_281,
    2021: 332_000_000,
    2022: 334_000_000,
    2023: 336_800_000
}
pop_series = interpolate_series(pop_anchors, years)

# Create DataFrame compatible with FRED format (DATE, VALUE)
df_pop = pd.DataFrame({
    "DATE": pd.to_datetime([f"{y}-01-01" for y in years]),
    "VALUE": pop_series.values
})
df_pop.to_csv("us_pop_official.csv", index=False)
print("Created us_pop_official.csv")


# 2. HOUSING UNITS (Source: FRED ETOTALUSQ176N)
# Anchors based on Housing Inventory Estimates
housing_anchors = {
    2000: 119_600_000,
    2005: 124_000_000,
    2010: 131_800_000,
    2015: 134_500_000,
    2020: 140_800_000,
    2023: 146_000_000
}
housing_series = interpolate_series(housing_anchors, years)

df_housing = pd.DataFrame({
    "DATE": pd.to_datetime([f"{y}-01-01" for y in years]),
    "VALUE": housing_series.values
})
df_housing.to_csv("us_housing_units.csv", index=False)
print("Created us_housing_units.csv")


# 3. OCCUPANCY & PERSONS PER HOUSEHOLD (Source: Census HVS)
# Occupancy rate: ~89% (fairly stable, dip in 2008-2010, rise in 2020)
# PPH: 2.62 (2000) -> 2.58 (2010) -> 2.63 (2018 rise) -> 2.50 (2023 drop)
occupancy_anchors = {2000: 0.89, 2010: 0.87, 2015: 0.88, 2020: 0.90, 2023: 0.899}
pph_anchors = {2000: 2.62, 2010: 2.58, 2018: 2.63, 2023: 2.50}

df_occ = pd.DataFrame({
    "year": years,
    "occupancy_rate": interpolate_series(occupancy_anchors, years).values,
    "persons_per_household": interpolate_series(pph_anchors, years).values
})
df_occ.to_csv("occupancy_pph.csv", index=False)
print("Created occupancy_pph.csv")


# 4. BIRTHS & DEATHS (Source: CDC/NCHS)
# Births: ~4M (2000-2007), Drop to 3.6M (2020-2023)
# Deaths: ~2.4M (2000) -> 2.85M (2019) -> 3.38M (2020 Covid) -> 3.09M (2023)
births_anchors = {
    2000: 4_058_000, 2007: 4_316_000, 2010: 3_999_000, 
    2019: 3_747_000, 2020: 3_613_000, 2023: 3_596_000
}
deaths_anchors = {
    2000: 2_403_000, 2010: 2_468_000, 2019: 2_854_000, 
    2020: 3_383_000, 2021: 3_464_000, 2023: 3_090_000
}

df_vital = pd.DataFrame({
    "year": years,
    "births": interpolate_series(births_anchors, years).values
})
df_vital.to_csv("us_births.csv", index=False)
print("Created us_births.csv")

df_deaths = pd.DataFrame({
    "year": years,
    "deaths": interpolate_series(deaths_anchors, years).values
})
df_deaths.to_csv("us_deaths.csv", index=False)
print("Created us_deaths.csv")


# 5. NET MIGRATION (Source: Census Estimates)
# Generally ~1M/year, dropped 2017-2021, surged 2022-2023
mig_anchors = {
    2000: 1_000_000, 2016: 1_000_000, 
    2018: 600_000, 2020: 400_000, 
    2022: 1_011_000, 2023: 1_600_000
}
df_mig = pd.DataFrame({
    "year": years,
    "net_mig": interpolate_series(mig_anchors, years).values
})
df_mig.to_csv("us_netmig.csv", index=False)
print("Created us_netmig.csv")

print("\nAll data files generated successfully.")