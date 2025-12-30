import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymc as pm
import arviz as az

# -----------------------------------------------------------------------------
# 1) LOAD DATA
# -----------------------------------------------------------------------------

try:
    pop_off = pd.read_csv("us_pop_official.csv", parse_dates=["DATE"])
    pop_off["year"] = pop_off["DATE"].dt.year
    pop_off = pop_off.groupby("year").last()["VALUE"].rename("pop_off")

    housing = pd.read_csv("us_housing_units.csv", parse_dates=["DATE"])
    housing["year"] = housing["DATE"].dt.year
    annual_housing = housing.groupby("year")["VALUE"].mean().rename("housing_units")

    occupancy_pph = pd.read_csv("occupancy_pph.csv", index_col="year")
    births = pd.read_csv("us_births.csv", index_col="year")
    deaths = pd.read_csv("us_deaths.csv", index_col="year")
    
    try:
        netmig = pd.read_csv("us_netmig.csv", index_col="year")
    except FileNotFoundError:
        netmig = pd.DataFrame({"net_mig": 0}, index=births.index)

except FileNotFoundError as e:
    print(f"Data loading error: {e}")
    print("Please run 'generate_historical_data.py' first.")
    # Dummy data fallback for 1940-2023 just in case
    years_dummy = np.arange(1940, 2024)
    pop_off = pd.Series(np.linspace(132, 336, len(years_dummy)) * 1e6, index=years_dummy, name="pop_off")
    annual_housing = pd.Series(np.linspace(37, 146, len(years_dummy)) * 1e6, index=years_dummy, name="housing_units")
    occupancy_pph = pd.DataFrame({
        "occupancy_rate": np.full(len(years_dummy), 0.9), 
        "persons_per_household": np.linspace(3.6, 2.5, len(years_dummy))
    }, index=years_dummy)
    births = pd.DataFrame({"births": np.full(len(years_dummy), 3e6)}, index=years_dummy)
    deaths = pd.DataFrame({"deaths": np.full(len(years_dummy), 2e6)}, index=years_dummy)
    netmig = pd.DataFrame({"net_mig": 500_000}, index=years_dummy)

# -----------------------------------------------------------------------------
# 2) HOUSING-BASED ESTIMATOR
# -----------------------------------------------------------------------------

df_housing = pd.concat([annual_housing, occupancy_pph], axis=1).dropna()
df_housing["pop_housing_est"] = (
    df_housing["housing_units"]
    * df_housing["occupancy_rate"]
    * df_housing["persons_per_household"]
)

# -----------------------------------------------------------------------------
# 3) COHORT SURVIVAL ESTIMATOR
# -----------------------------------------------------------------------------

years = sorted(set(pop_off.index) | set(births.index) | set(deaths.index))
valid_years = [y for y in years if y in pop_off.index]
if not valid_years:
    valid_years = years 

pop_model = pd.Series(index=years, dtype=float)

# Anchor at 1940 (or earliest available)
start_year = min(valid_years)
pop_model.loc[start_year] = pop_off.loc[start_year]

for i in range(len(years)-1):
    y = years[i]
    next_y = years[i+1]
    
    if pd.notna(pop_model.loc[y]):
        b_val = births.loc[y, "births"] if y in births.index else 0
        d_val = deaths.loc[y, "deaths"] if y in deaths.index else 0
        m_val = netmig.loc[y, "net_mig"] if y in netmig.index else 0
        
        pop_model.loc[next_y] = pop_model.loc[y] + b_val - d_val + m_val

# -----------------------------------------------------------------------------
# 4) DISCREPANCY & PLOTTING
# -----------------------------------------------------------------------------

df = pd.DataFrame({
    "official": pop_off,
    "model": pop_model,
    "housing": df_housing["pop_housing_est"],
}).dropna()

df["disc_model_off"] = df["official"] - df["model"]
df["disc_housing_off"] = df["official"] - df["housing"]

# Plot 1: Long-term estimates
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["official"] / 1e6, label="Official (Census)", linewidth=2, color='black')
plt.plot(df.index, df["model"] / 1e6, label="Cohort Model (Births-Deaths+Mig)", linestyle="--", color='blue')
plt.plot(df.index, df["housing"] / 1e6, label="Housing-based Estimate", linestyle=":", color='green')
plt.legend()
plt.title(f"US Population Estimates ({df.index.min()}-{df.index.max()})")
plt.xlabel("Year")
plt.ylabel("Population (Millions)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Plot 2: Discrepancies
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["disc_model_off"] / 1e6, label="Official - Cohort Model", color='blue')
plt.plot(df.index, df["disc_housing_off"] / 1e6, label="Official - Housing Est", color='green', alpha=0.7)
plt.legend()
plt.title("Discrepancy Series (Sensitivity to Errors)")
plt.xlabel("Year")
plt.ylabel("Difference (Millions)")
plt.axhline(0, color='black', linewidth=1)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# 5) BAYESIAN CHANGEPOINT (Modern PyMC)
# -----------------------------------------------------------------------------

years_arr = df.index.values
disc_vals = df["disc_model_off"].values

print("Running Bayesian Changepoint Detection...")

with pm.Model() as changepoint_model:
    # Allow for potentially two changepoints given the long history (e.g., 1960s and 2000s)
    # For now, we stick to one major structural break in error
    
    tau = pm.DiscreteUniform("tau", lower=years_arr.min(), upper=years_arr.max())
    
    alpha1 = pm.Normal("alpha1", mu=0, sigma=1e7)
    alpha2 = pm.Normal("alpha2", mu=0, sigma=1e7)
    sigma = pm.HalfNormal("sigma", sigma=1e7)
    
    mu = pm.math.switch(tau >= years_arr, alpha1, alpha2)
    
    pm.Normal("obs", mu=mu, sigma=sigma, observed=disc_vals)
    
    # Sampling
    trace = pm.sample(1000, tune=1000, chains=2, return_inferencedata=True, progressbar=True)

az.plot_posterior(trace, var_names=["tau"])
plt.title("Posterior of Major Changepoint in Model Discrepancy")
plt.xlabel("Year")
plt.show()

# -----------------------------------------------------------------------------
# 6) HYPOTHETICAL SCALED POPULATION ANALYSIS
# -----------------------------------------------------------------------------
# Feature: Check if user wants to calculate the scaled hypothetical scenario.
# (Today ~130M instead of ~335M)

print("\n" + "="*60)
print("HYPOTHETICAL SCENARIO: PROPORTIONAL SCALING")
print("="*60)
print("This module calculates a revised timeline assuming the current US population")
print("is actually ~130 million (approx 38.8% of official figures).")

# In a script, we default to running it, or we could use input(). 
# For automation purposes, we'll run the calculation and display results.

current_year = df.index.max()
current_pop_official = df.loc[current_year, "official"]
target_pop_present = 130_000_000

# Calculate scaling factor
scaling_factor = target_pop_present / current_pop_official

print(f"\n[1] Current Official Population ({current_year}): {current_pop_official:,.0f}")
print(f"[2] Target 'Real' Population: {target_pop_present:,.0f}")
print(f"[3] Scaling Factor (Target / Official): {scaling_factor:.5f}")

# Apply scaling to the whole dataframe
df["hypothetical_scaled"] = df["official"] * scaling_factor

# Calculate 1940 estimate specifically
pop_1940_official = df.loc[1940, "official"] if 1940 in df.index else None

if pop_1940_official:
    pop_1940_scaled = df.loc[1940, "hypothetical_scaled"]
    print(f"\n--- 1940 ESTIMATES ---")
    print(f"Actual U.S. population in 1940 (Official): {pop_1940_official:,.0f}")
    print(f"Scaled estimate (Hypothetical): {pop_1940_scaled:,.0f}")
    print(f"Approximation: ~{pop_1940_scaled/1e6:.1f} Million")
else:
    print("\nWarning: 1940 data not found in current dataset range.")

# Plot the Hypothetical vs Official
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["official"] / 1e6, label="Official Census Trajectory", color='black', alpha=0.3, linestyle="--")
plt.plot(df.index, df["hypothetical_scaled"] / 1e6, label="Hypothetical (Scaled to 130M)", color='red', linewidth=2)

plt.fill_between(df.index, df["hypothetical_scaled"]/1e6, df["official"]/1e6, color='gray', alpha=0.1, label="Divergence")

plt.title(f"Hypothetical 'Real' Population vs Official Stats (Scale Factor $\\approx$ {scaling_factor:.3f})")
plt.xlabel("Year")
plt.ylabel("Population (Millions)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("\nScenario calculation complete.")