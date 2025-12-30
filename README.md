# Population Analysis

A Python project for analyzing US population data and demographics.

## Overview

This project analyzes historical and contemporary US population trends, including births, deaths, net migration, housing units, and occupancy metrics. It includes tools for generating synthetic data and performing statistical analysis on population dynamics.

## Files

- `population_analysis.py` - Main analysis module with statistical models
- `generate_data.py` - Generate synthetic population data
- `generate_historical_data.py` - Generate historical population datasets
- `us_*.csv` - Historical US population data files
- `occupancy_pph.csv` - Occupancy per person-hour metrics

## Requirements

See `requirements.txt` for dependencies:
- numpy
- pandas
- matplotlib
- pymc
- arviz

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the main analysis:
```bash
python population_analysis.py
```

Generate new datasets:
```bash
python generate_data.py
python generate_historical_data.py
```

## License

MIT
