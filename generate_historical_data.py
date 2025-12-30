import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# HISTORICAL DATA GENERATION (1940-2023)
# -----------------------------------------------------------------------------
# Sources: US Census Bureau Decennial Censuses, NCHS Vital Statistics

def interpolate_series(anchors, index):
    """Interpolates values between anchor points."""
    s = pd.Series(np.nan, index=index)
    for year, val in anchors.items():
        if year in index:
            s.loc[year] = val
    return s.interpolate(method='linear')

years = np.arange(1940, 2024)

# -----------------------------------------------------------------------------
# 1. OFFICIAL POPULATION (Census + Estimates)
# -----------------------------------------------------------------------------
pop_anchors = {
    1940: 132_164_569,
    1950: 151_325_798,
    1960: 179_323_175,
    1970: 203_211_926,
    1980: 226_545_805,
    1990: 248_709_873,
    2000: 281_421_906,
    2010: 308_745_538,
    2020: 331_449_281,
    2023: 336_800_000
}
pop_series = interpolate_series(pop_anchors, years)

df_pop = pd.DataFrame({
    "DATE": pd.to_datetime([f"{y}-01-01" for y in years]),
    "VALUE": pop_series.values
})
df_pop.to_csv("us_pop_official.csv", index=False)
print("Created us_pop_official.csv (1940-2023)")

# -----------------------------------------------------------------------------
# 2. HOUSING UNITS
# -----------------------------------------------------------------------------
# 1940-1990: Decennial Census Housing Counts
# 2000-2023: Housing Unit Estimates
housing_anchors = {
    1940: 37_325_470,
    1950: 46_137_000,
    1960: 58_326_000,
    1970: 68_679_030,
    1980: 88_410_627,
    1990: 102_263_678,
    2000: 119_600_000,
    2010: 131_800_000,
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

# -----------------------------------------------------------------------------
# 3. OCCUPANCY & PERSONS PER HOUSEHOLD (PPH)
# -----------------------------------------------------------------------------
# PPH has dropped significantly from 3.67 (1940) to ~2.5 (2023).
pph_anchors = {
    1940: 3.67, 1950: 3.37, 1960: 3.33, 
    1970: 3.14, 1980: 2.76, 1990: 2.63,
    2000: 2.62, 2010: 2.58, 2020: 2.53, 2023: 2.50
}
# Occupancy rates (approximate)
occ_anchors = {
    1940: 0.93, 1950: 0.93, 1960: 0.91,
    1970: 0.92, 1980: 0.91, 1990: 0.89,
    2000: 0.89, 2010: 0.87, 2020: 0.90, 2023: 0.899
}

df_occ = pd.DataFrame({
    "year": years,
    "occupancy_rate": interpolate_series(occ_anchors, years).values,
    "persons_per_household": interpolate_series(pph_anchors, years).values
})
df_occ.to_csv("occupancy_pph.csv", index=False)
print("Created occupancy_pph.csv")

# -----------------------------------------------------------------------------
# 4. BIRTHS & DEATHS (Vital Statistics)
# -----------------------------------------------------------------------------
# Note the Baby Boom (1946-1964) peak
births_anchors = {
    1940: 2_559_000, 
    1945: 2_858_000,
    1950: 3_632_000, 
    1957: 4_300_000, # Baby boom peak
    1965: 3_760_000, 
    1975: 3_144_000, # Baby bust
    1980: 3_612_000,
    1990: 4_158_000, # Echo boom
    2007: 4_316_000, 
    2020: 3_613_000, 
    2023: 3_596_000
}
deaths_anchors = {
    1940: 1_417_000, 
    1950: 1_452_000, 
    1960: 1_711_000,
    1970: 1_921_000, 
    1980: 1_989_000, 
    1990: 2_148_000,
    2000: 2_403_000, 
    2010: 2_468_000, 
    2019: 2_854_000,
    2020: 3_383_000, # COVID spike
    2023: 3_090_000
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

# -----------------------------------------------------------------------------
# 5. NET MIGRATION
# -----------------------------------------------------------------------------
# Low during WWII. Rising after 1965 Immigration Act.
# Spikes in 90s. Dip in 2008 and 2020.
mig_anchors = {
    1940: 50_000,
    1945: 100_000, # War brides etc
    1950: 250_000,
    1960: 330_000,
    1970: 450_000, # Post-1965 act effects start
    1980: 700_000, # Mariel boatlift era / general rise
    1990: 1_000_000,
    2000: 1_000_000,
    2016: 1_000_000,
    2020: 400_000, # Covid restrictions
    2023: 1_600_000
}
df_mig = pd.DataFrame({
    "year": years,
    "net_mig": interpolate_series(mig_anchors, years).values
})
df_mig.to_csv("us_netmig.csv", index=False)
print("Created us_netmig.csv")

print("\nHistorical data (1940-2023) generated successfully.")