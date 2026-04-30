"""
train_model.py
--------------
Fits the chosen model on the training period and optionally validates on the
test period. Run via run_workflow.sh, or directly:

    python train_model.py --email YOU@EMAIL.COM --pin 1234 [--other-options]
"""

import os
import argparse
import pandas as pd
import hf_hydrodata
from forecast_functions import (
    get_training_test_data,
    fit_longterm_avg_model,
    fit_monthly_avg_model,
    fit_seasonal_doy_model,
    predict_seasonal_doy_model,
    compute_metrics,
    plot_validation,
    save_model,
    load_model,
)

parser = argparse.ArgumentParser()
parser.add_argument('--email',         required=True)
parser.add_argument('--pin',           required=True)
parser.add_argument('--gauge-id',      default='09506000')
parser.add_argument('--ar-order',      type=int, default=7)
parser.add_argument('--train-start',   default='1990-01-01')
parser.add_argument('--train-end',     default='2022-12-31')
parser.add_argument('--test-start',    default='2023-01-01')
parser.add_argument('--test-end',      default='2024-12-31')
parser.add_argument('--model',         default='seasonal_doy', choices=['longterm_avg', 'monthly_avg', 'seasonal_doy'])
parser.add_argument('--forecast-days', type=int, default=14)
parser.add_argument('--doy-window',    type=int, default=15)
parser.add_argument('--refit',         default='True')
parser.add_argument('--validate',      default='True')
args = parser.parse_args()

REFIT_MODEL    = args.refit.lower()    == 'true'
RUN_VALIDATION = args.validate.lower() == 'true'
MODEL_PATH = f"saved_model_{args.model}.pkl"

hf_hydrodata.register_api_pin(email=args.email, pin=args.pin)

print("\n--- Step 1: Download streamflow data ---")
train, test = get_training_test_data(
    args.gauge_id, args.train_start, args.train_end,
    args.test_start, args.test_end
)

# =============================================================================
# MODEL 1: LONG-TERM AVERAGE
# =============================================================================

if args.model == 'longterm_avg':
    model_label = 'Long-term Average'
    print("\n--- Step 2: Fit long-term average model ---")

    if REFIT_MODEL or not os.path.exists(MODEL_PATH):
        model = fit_longterm_avg_model(train)
        print(f"  Long-term mean: {model:.2f} cfs")
        save_model(model, MODEL_PATH)
    else:
        model = load_model(MODEL_PATH)
        if not isinstance(model, float):
            raise TypeError(
                f"{MODEL_PATH} does not contain a longterm_avg model. "
                "Re-run with --refit True --model longterm_avg."
            )

    if RUN_VALIDATION:
        train_fitted = pd.Series(model, index=train.index)
        forecast_series = pd.Series(model, index=test.index)


# =============================================================================
# MODEL 2: MONTHLY AVERAGE
# =============================================================================

elif args.model == 'monthly_avg':
    model_label = 'Monthly Average'
    print("\n--- Step 2: Fit monthly average model ---")

    if REFIT_MODEL or not os.path.exists(MODEL_PATH):
        model = fit_monthly_avg_model(train)
        print("  Monthly means calculated for months 1-12.")
        save_model(model, MODEL_PATH)
    else:
        model = load_model(MODEL_PATH)
        if not isinstance(model, dict):
            raise TypeError(
                f"{MODEL_PATH} does not contain a monthly_avg model. "
                "Re-run with --refit True --model monthly_avg."
            )

    if RUN_VALIDATION:
        train_fitted = pd.Series([model[d.month] for d in train.index], index=train.index)
        forecast_series = pd.Series([model[d.month] for d in test.index], index=test.index)


# =============================================================================
# MODEL 3: SEASONAL DAY-OF-YEAR AVERAGE
# =============================================================================

elif args.model == 'seasonal_doy':
    model_label = 'Seasonal Day-of-Year Average'
    print("\n--- Step 2: Fit seasonal day-of-year average model ---")

    if REFIT_MODEL or not os.path.exists(MODEL_PATH):
        model = fit_seasonal_doy_model(train, window_days=args.doy_window)
        print(
            f"  Seasonal means calculated for each day of year using "
            f"+/- {args.doy_window} days."
        )
        save_model(model, MODEL_PATH)
    else:
        model = load_model(MODEL_PATH)
        if not (isinstance(model, dict) and model.get('model_type') == 'seasonal_doy'):
            raise TypeError(
                f"{MODEL_PATH} does not contain a seasonal_doy model. "
                "Re-run with --refit True --model seasonal_doy."
            )

    if RUN_VALIDATION:
        train_fitted = pd.Series(
            predict_seasonal_doy_model(model, train.index),
            index=train.index
        )
        forecast_series = pd.Series(
            predict_seasonal_doy_model(model, test.index),
            index=test.index
        )


# =============================================================================
# VALIDATION
# =============================================================================

if RUN_VALIDATION:
    print("\n--- Step 3: Validate on test period ---")

    metrics = compute_metrics(test['streamflow_cfs'].values, forecast_series.values)

    print("\n  Validation metrics:")
    for name, val in metrics.items():
        print(f"    {name:<12}: {val:.4f}")

    print(
        "\n  NSE guide: >0.75 very good | 0.65–0.75 good | "
        "0.50–0.65 satisfactory | <0.50 poor"
    )

    print("\n  Generating validation plot ...")
    plot_validation(
        train['streamflow_cfs'],
        test['streamflow_cfs'],
        forecast_series,
        metrics,
        model_label,
        train_forecast_cfs=train_fitted,
        save_path=f"validation_plot_{args.model}.png"
    )