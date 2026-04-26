# Final_Anal_HW7: Streamflow Forecasting Workflow

## Project Description

This repository contains a Python workflow for forecasting daily average streamflow for the Verde River near Camp Verde, Arizona using USGS Gauge 09506000. The workflow allows a user to generate a 5-day streamflow forecast starting on a selected date. The user can also choose whether to re-fit the model, use the existing saved model, and run model validation.

The main workflow is controlled through one file:

```bash
Week14_StreamflowForecast/run_workflow.sh
```

# Part A) Instructions for Setting Up the Repository and Environment
## **Step 1: Clone the GitHub repository**

Open a terminal and run:

```bash
git clone https://github.com/gretafreeman/Final_Anal_HW7.git
```

Then move into the project folder:

```bash
cd Final_Anal_HW7/Week14_StreamflowForecast
```
## **Step 2: Create the conda environment**

This repository includes an environment.yml file that installs the packages needed to run the workflow.

Run:

```bash
conda env create -f environment.yml
```
This creates a conda environment called 'hw7_forecast'

## **Step 3: Activate the environment**

After the environment is created, activate it using:
```bash
conda activate hw7_forecast
```

## **Step 4: Check that the required files are present**

Inside the Week14_StreamflowForecast folder, you should see these main files:

```bash
environment.yml
forecast_functions.py
generate_forecast.py
run_workflow.sh
saved_model.pkl
train_model.py
```

The workflow should be run from inside the Week14_StreamflowForecast folder.

## **Step 5: HydroFrame login information**

This workflow downloads streamflow data using HydroFrame. When the workflow runs, it will ask for:

```bash
HydroFrame email:
HydroFrame PIN:
```

Enter your HydroFrame email and PIN when prompted. The PIN will not show on the screen while typing, but it is still being entered.

# Part B) Instructions for Generating a Forecast
## **Step 1: Open the main workflow file**

Open the following file in VS Code or another text editor:

```bash
run_workflow.sh
```

This is the only file the user needs to edit before running the workflow.

## **Step 2: Edit the user options**

Near the top of run_workflow.sh, edit the options under the section called USER OPTIONS.

Example:
```bash
GAUGE_ID="09506000"
AR_ORDER=7

TRAIN_START="1990-01-01"
TRAIN_END="2022-12-31"

TEST_START="2023-01-01"
TEST_END="2024-12-31"

FORECAST_DATE="2024-04-30"

REFIT_MODEL="True"
RUN_VALIDATION="True"

MODEL="monthly_avg"
```

## **Step 3: Choose the forecast start date**

To change the first day of the 5-day forecast, edit:
```bash
FORECAST_DATE="2024-04-30"
```
Use the format:
```bash
YYYY-MM-DD
```

For example, to forecast starting on May 1, 2024, use:
```bash
FORECAST_DATE="2024-05-01"
```

The workflow will generate a 5-day daily average streamflow forecast starting on the date selected.

## **Step 4: Choose whether to re-fit the model**

The user can choose whether to re-fit the model or use the saved model.

To re-fit the model from the training data, use:
```bash
REFIT_MODEL="True"
```

To use the existing saved model file, use:
```bash
REFIT_MODEL="False"
```

The saved model is stored as:
```bash
saved_model.pkl
```

If you change the model type, it is recommended to set REFIT_MODEL="True" so that the saved model matches the selected model.

## **Step 5: Choose whether to run validation**

The user can also choose whether to run model validation.

To run validation and create validation outputs, use:
```bash
RUN_VALIDATION="True"
```
To skip validation and only generate the forecast, use:
```bash
RUN_VALIDATION="False"
```

When validation is turned on, the workflow prints model performance statistics and creates a validation plot.

The validation plot is saved as:
```bash
validation_plot.png
```

## **Step 6: Choose the model type**

The workflow currently allows the user to choose between two simple model options:
```bash
MODEL="longterm_avg"
```
or
```bash
MODEL="monthly_avg"
```

The longterm_avg model predicts streamflow using the overall average flow from the training period.

The monthly_avg model predicts streamflow using the average streamflow for each calendar month.

## **Step 7: Run the workflow**

After editing and saving run_workflow.sh, run:
```bash
bash run_workflow.sh
```

The workflow will ask for your HydroFrame email and PIN. After that, it will download the necessary streamflow data, optionally fit and validate the model, and then generate the 5-day forecast.

## **Step 8: View the forecast output**

The forecast will print in the terminal as a table showing the forecasted streamflow for each of the 5 days.

The workflow also creates a forecast figure saved as:

```bash
forecast_plot.png
```

This plot shows recent observed streamflow and the 5-day forecast.

# Part C. Outline of the Workflow (User Guidance)
## **1. User sets workflow options**

The user starts by editing run_workflow.sh. This file controls the full workflow, including:

*USGS gauge ID*

*Training period*
  
*Testing period*
  
*Forecast start date*

*Whether to re-fit the model*

*Whether to run validation*

*Which model type to use*

## **2. The workflow collects HydroFrame credentials**

When run_workflow.sh is run, the user is asked to enter their HydroFrame email and PIN. These are used to access streamflow data through the HydroFrame API.

## *3. Training and validation are run if selected*

If either REFIT_MODEL="True" or RUN_VALIDATION="True", the workflow runs:
```bash
train_model.py
```

Note:

This script downloads historical streamflow data, separates it into a training period and testing period, fits the selected model, saves the model as saved_model.pkl, and optionally evaluates the model on the testing period.

If validation is selected, the script prints model performance statistics and saves a validation plot.

## *4. The forecast script runs

After the training and validation step, the workflow runs:
```bash
generate_forecast.py
```

This script loads the saved model and generates a 5-day forecast beginning on the user-selected forecast date.

## 5. Forecast results are printed and plotted

The final forecast is printed in the terminal as daily streamflow values in cubic feet per second.

The workflow also saves a figure called:
```bash
forecast_plot.png
```

This plot shows recent observed streamflow and the forecasted values.

# Example Full Run

A typical run would look like this:

```bash
cd Final_Anal_HW7/Week14_StreamflowForecast
conda activate hw7_forecast
bash run_workflow.sh
```

Then enter your HydroFrame email and PIN when prompted.

Troubleshooting
If the conda environment does not create correctly

Make sure you are in the correct folder:
```bash
cd Final_Anal_HW7/Week14_StreamflowForecast
```

Then try:

```bash
conda env create -f environment.yml
```

If conda gives an error related to the prefix line in environment.yml, delete the last line of the file that starts with prefix: and try creating the environment again.

If the workflow cannot find a saved model

Set:
```bash
REFIT_MODEL="True"
```

Then run:
```bash
bash run_workflow.sh
```

This will create a new saved_model.pkl file.

If you switch model types

If you change from:
```bash
MODEL="longterm_avg"
```

to:

```bash
MODEL="monthly_avg"
```
or the other way around, set:
```bash
REFIT_MODEL="True"
```

This ensures that the saved model matches the model type selected.

If the script does not run on Windows

This workflow uses a .sh file, which is a bash script. On Windows, run it using Git Bash, WSL, or another terminal that supports bash commands.

Use:
```bash
bash run_workflow.sh
```
