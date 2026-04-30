"""
generate_forecast.py
--------------------
Generates a 5-day streamflow forecast starting on a user-specified date.
Run via run_workflow.sh, or directly:

    python generate_forecast.py --email YOU@EMAIL.COM --pin 1234 [--other-options]
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import hf_hydrodata
from forecast_functions import (
    get_recent_data,
    make_5day_forecast_longterm,
    make_5day_forecast_monthly,
    make_forecast_seasonal_doy,
    load_model,
)

parser = argparse.ArgumentParser()
parser.add_argument('--email',         required=True)
parser.add_argument('--pin',           required=True)
parser.add_argument('--gauge-id',      default='09506000')
parser.add_argument('--ar-order',      type=int, default=7)
parser.add_argument('--forecast-date', default='2024-04-30')
parser.add_argument('--model', default='seasonal_doy', choices=['longterm_avg', 'monthly_avg', 'seasonal_doy'])
parser.add_argument('--forecast-days', type=int, default=14)

parser.add_argument('--doy-window', type=int, default=15)
args = parser.parse_args()

forecast_date_ts = pd.Timestamp(args.forecast_date)
MODEL_PATH = f"saved_model_{args.model}.pkl"

hf_hydrodata.register_api_pin(email=args.email, pin=args.pin)

print("\n--- Step 1: Download recent streamflow data ---")
recent = get_recent_data(args.gauge_id, args.forecast_date, args.ar_order)

# =============================================================================
# LOAD MODEL AND GENERATE FORECAST
# =============================================================================

print("\n--- Step 2: Load saved model ---")
model = load_model(MODEL_PATH)

if args.model == 'longterm_avg':
    if not isinstance(model, float):
        raise TypeError(
            f"{MODEL_PATH} does not contain a longterm_avg model. "
            "Re-run train_model.py with --refit True --model longterm_avg first."
        )

    print("\n--- Step 3: Generate long-term average forecast ---")
    forecast_df = make_5day_forecast_longterm(
        model,
        args.forecast_date,
        n_days=args.forecast_days
    )
    model_label = 'Long-term Average'


elif args.model == 'monthly_avg':
    if not isinstance(model, dict):
        raise TypeError(
            f"{MODEL_PATH} does not contain a monthly_avg model. "
            "Re-run train_model.py with --refit True --model monthly_avg first."
        )

    print("\n--- Step 3: Generate monthly average forecast ---")
    forecast_df = make_5day_forecast_monthly(
        model,
        args.forecast_date,
        n_days=args.forecast_days
    )
    model_label = 'Monthly Average'


elif args.model == 'seasonal_doy':
    if not (isinstance(model, dict) and model.get('model_type') == 'seasonal_doy'):
        raise TypeError(
            f"{MODEL_PATH} does not contain a seasonal_doy model. "
            "Re-run train_model.py with --refit True --model seasonal_doy first."
        )

    print("\n--- Step 3: Generate seasonal day-of-year forecast ---")
    forecast_df = make_forecast_seasonal_doy(
        model,
        args.forecast_date,
        n_days=args.forecast_days
    )
    model_label = 'Seasonal Day-of-Year Average'

# ── Monthly average model ────────────────────────────────────────────────────
elif args.model == 'monthly_avg':
    print("\n--- Step 2: Load monthly average model ---")

    monthly_means = load_model()

    if not isinstance(monthly_means, dict):
        raise TypeError(
            "saved_model.pkl does not contain a monthly_avg model. "
            "Re-run train_model.py with --refit True --model monthly_avg first."
        )

    print("\n--- Step 3: Generate 5-day monthly average forecast ---")

    forecast_df = make_5day_forecast_monthly(monthly_means, args.forecast_date)
    model_label = 'Monthly Average'

print(f"\n  {args.forecast_days}-Day Streamflow Forecast — Verde River ({model_label})")
print(f"  Starting: {forecast_date_ts.date()}\n")
print(f"  {'Date':<14}  Forecast (cfs)")
print(f"  {'-'*30}")
for date, row in forecast_df.iterrows():
    print(f"  {str(date.date()):<14}  {row['Forecast_cfs']:.1f}")

recent_cfs = recent['streamflow_cfs'].iloc[-30:]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(recent_cfs.index, recent_cfs.values,
        color='steelblue', linewidth=1.3, label='Recent Observed (30 days)')
ax.plot(forecast_df.index, forecast_df['Forecast_cfs'],
        'ro--', linewidth=1.5, markersize=6,
        label=f'{args.forecast_days}-Day Forecast')
ax.axvline(forecast_date_ts, color='gray', linestyle=':', linewidth=1.2)
ax.set_yscale('log')
ax.set_ylabel('Streamflow (cfs)')
ax.set_title(
    f'Verde River {args.forecast_days}-Day Forecast  |  '
    f'Starting {forecast_date_ts.date()}  ({model_label})'
)
ax.legend()
plt.tight_layout()
plot_name = f"forecast_plot_{args.model}.png"
plt.savefig(plot_name, dpi=150, bbox_inches='tight')
print(f"  Plot saved to {plot_name}")
plt.show()
