# Vehicle-to-Home Charging Can Cut Costs and Greenhouse Gas Emissions across the US Project

This repository contains various components and analyses related to the 'Vehicle-to-Home Charging Can Cut Costs and Greenhouse Gas Emissions across the US' project. Below is an overview of the main directories and their purposes:

## Project Structure

### Analysis Components

The `Scripts/` directory contains core simulation and analysis tools for vehicle activity simulation, EV and ICEV energy consumption simulation, EV charging simulation:

#### Parking and Activity Analysis
- `Parkingrecog_trb.py`, `Parkingrecog_db.py`: Scripts for analyzing vehicle parking patterns
- `activeness_trb.py`, `activeness_0.py`: Vehicle activity pattern analysis. Vehicles are not driven everyday. These scripts analyze the National Household Travel Survey (NHTS) dataset to determine activity level
- `partition_2.py`: Data partitioning for analysis


#### Vehicle Analysis
- `simulator_trb.py`: Generates synthetic year-long driving profiles based on NHTS (National Household Travel Survey) data. Key features:
  - Regional customization for 9 U.S. regions with region-specific driving patterns
  - Distinguishes between weekday/weekend/holiday travel patterns
  - Considers vehicle types (SUV/Truck) and urban/rural driving
  - Models trip chains based on trip purposes (home, work, shopping, etc.)
  - Uses activity rates to determine daily vehicle usage probability
- **Driving_profile_simu_trb/**: Contains simulation and analysis scripts for driving profiles.
- `ICEV_db.py`: Internal Combustion Engine Vehicle energy consumption simulation
- `evhhec_trb.py`, `evhhec_olec_trb.py`, `evhhec_trb_db.py`: Electric vehicle home charging analysis scripts. Determines operating constraints of vehicle-to-home based on vehicle availability and home energy consumption
- `hour_to_cr_trb.py`, `hour_to_cr_db.py`: Scripts for calculating and processing charging rates
- `hour_to_cr_db_60.py`: Variant for specific battery capacity (60 kWh) analysis
- `soc_drop_rd_trb.py`, `soc_drop_rd_dashboard.py`: These scripts calculate the battery state of charge changes during vehicle trips, including EV . Key features:
  - Calculates energy consumption for each trip based on:
    - Trip distance and duration
    - Urban/Highway driving patterns
    - Temperature impact on energy efficiency
    - Real-world adjustment factors for EPA fuel economy ratings
  - Processes hourly SOC drops considering:
    - Trip start and end times
    - Temperature-dependent efficiency coefficients
    - Distribution of energy consumption across multi-hour trips
  - Outputs detailed SOC profiles with:
    - Trip-by-trip energy consumption
    - Hourly SOC changes
    - Temperature-adjusted efficiency factors


#### Charging Simulation

- `uc_80.py`: Uncontrolled charging simulation with 80% SOC target. Key features:
  - Identifies long-duration parking events (≥8 hours) at home or work locations
  - Uses GAMS optimization to simulate charging behavior with:
    - Slow charging (Level 2, 10kW) at identified parking locations
    - Fast charging used only between long parking events when L2 charging cannot satisfy driving needs
    - Maintains battery SOC between 20-80%
  
- `CC_rd.py`: Cost-minimizing charging simulation. Key features:
  - Uses GAMS solver for cost minimization
  - Incorporates regional electricity prices and carbon costs
  - Considers both slow (Level 2) and fast charging options
  - Processes charging in cycles to handle year-long simulations
  - Uses Cambium database for hourly electricity prices and short-run marginal emissions factors

- `v2h_rd.py`: Core V2H simulation scripts that optimize charging/discharging schedules using GAMS solver
- `v2h_rd_nonelec.py`, `v2h_trb_nonelec.py`: V2H simulation variants for non-electrified-home scenarios
- `v2h_rd_cons.py`: V2H simulation variants for constrained V2H scenarios

The scripts use various optimization techniques (GAMS solver) and data processing methods to simulate electric vehicle energy consumption, and cost optimization across different charging strategy scenarios.

#### DegradationAssessment/
Contains scripts and data for assessing battery degradation.

Key Files:
- `degradation.ipynb`, `degradation_trb.ipynb`, `degradation_cons.ipynb`: Main notebooks for battery degradation visualization
- `meanSOC.ipynb`, `meanSOC.py`: State of Charge analysis scripts
- `deg_agg.py`, `deg_agg_cons.py`: Aggregation scripts for degradation data
- `deg_50AhB1.py`, `deg_250AhLFP.py`, `deg_75Ah.py`, `deg_50AhB2.py`: Battery-specific degradation models for different capacities and chemistries
- `degradation_agg.py`, `degradation_agg_laptp.py`: Aggregation and analysis scripts for degradation data

#### CostEmissionAssessment/
Scripts and analysis for cost and emission assessments.

Key Files:
- `analysis_func_*.py`: Various analysis functions for different scenarios:
  - `analysis_func_v2h.py`: Vehicle-to-home analysis
  - `analysis_func_cc.py`: Carbon credit analysis
  - `analysis_func_uc.py`: Use case analysis
  - `analysis_func_icev.py`: Internal combustion engine vehicle analysis
- `aggregate_results.py`, `aggregate_ICEV.py`: Data aggregation scripts

#### ResStock/
ResStock model integration and analysis scripts.

Key Files:
- `processing.ipynb`: Main data processing notebook
- `dataacq.py`, `dataacq_2025.py`: Data acquisition scripts for current and future scenarios
- `dataacq.ipynb`, `dataacq_2025.ipynb`, `dataacq_noelec.ipynb`: Notebooks for data acquisition and processing

#### Cambium/
Integration with Cambium data and related analyses. Contains primarily data files with CSV format for emissions and energy analysis.

#### Raw/
Contains raw NHTS driving record data files for analysis.

#### BLAST/
BLAST-related analysis and data for battery degradation analysis.

### Energy Consumption Intermediate Results

Several directories contain intermediate results from energy consumption analysis for different scenarios:

- **Energy consumption_ICEV_2/**: Energy consumption results for Internal Combustion Engine Vehicles.
- **Energy consumption_adjusted_1_1_Y60_db/**: Energy consumption analysis for 60kWh-battery EVs.
- **Energy consumption_adjusted_1_2_Y60_db/**: Energy consumption analysis for 60kWh-battery EVs.
- **Energy consumption_adjusted_1_1_Y82_db/**: Energy consumption analysis for 82kWh-battery EVs.
- **Energy consumption_adjusted_1_2_Y82_db/**: Energy consumption analysis for 82kWh-battery EVs.
- **Energy consumption_adjusted_1_1_Y82/**: Energy consumption analysis for 82kWh-battery EVs.
- **Energy consumption_adjusted_1_2_Y82/**: Energy consumption analysis for 82kWh-battery EVs.


## Note

This repository contains various analysis components and data processing scripts. Some directories and files are excluded from version control (see .gitignore) to maintain repository cleanliness and manage large data files appropriately.

For detailed information about specific components or how to use the scripts, please refer to the documentation within each directory.
