"""
Risk-adjusted outcome analysis using logistic regression.

Implements Expected vs. Observed (E/O) outcome analysis for fair
institutional comparisons. Hospitals treating higher-acuity patients
have their outcomes adjusted accordingly.
"""

import numpy as np
from scipy import stats


def calculate_expected_rate(
    patient_risk_scores: list[float],
) -> float:
    """Calculate expected outcome rate from individual patient risk scores.

    Each risk score is the predicted probability of adverse outcome
    from the logistic regression model.
    """
    if not patient_risk_scores:
        return 0.0
    return float(np.mean(patient_risk_scores))


def calculate_oe_ratio(
    observed_events: int,
    expected_rate: float,
    total_cases: int,
) -> dict:
    """Calculate Observed/Expected ratio with confidence interval.

    O/E < 1.0 = better than expected
    O/E = 1.0 = as expected
    O/E > 1.0 = worse than expected
    """
    if total_cases == 0 or expected_rate == 0:
        return {"oe_ratio": None, "ci_lower": None, "ci_upper": None, "interpretation": "insufficient_data"}

    expected_events = expected_rate * total_cases
    oe_ratio = observed_events / expected_events

    # Poisson-based 95% CI for the O/E ratio
    ci_lower = stats.chi2.ppf(0.025, 2 * observed_events) / (2 * expected_events) if observed_events > 0 else 0
    ci_upper = stats.chi2.ppf(0.975, 2 * (observed_events + 1)) / (2 * expected_events)

    if ci_upper < 1.0:
        interpretation = "significantly_better"
    elif ci_lower > 1.0:
        interpretation = "significantly_worse"
    else:
        interpretation = "as_expected"

    return {
        "oe_ratio": round(oe_ratio, 3),
        "ci_lower": round(ci_lower, 3),
        "ci_upper": round(ci_upper, 3),
        "observed": observed_events,
        "expected": round(expected_events, 2),
        "total_cases": total_cases,
        "interpretation": interpretation,
    }


def risk_adjust_rate(
    observed_rate: float,
    expected_rate: float,
    national_rate: float,
) -> float:
    """Calculate risk-adjusted rate.

    Formula: (Observed / Expected) * National Average
    This standardizes the hospital's rate to what would be expected
    if they had a nationally average patient mix.
    """
    if expected_rate == 0:
        return 0.0
    return round((observed_rate / expected_rate) * national_rate, 4)


def logistic_risk_score(
    coefficients: dict[str, float],
    intercept: float,
    patient_data: dict[str, float],
) -> float:
    """Calculate individual patient risk score from logistic regression model.

    Args:
        coefficients: Variable name -> coefficient mapping
        intercept: Model intercept (beta_0)
        patient_data: Variable name -> value mapping for this patient

    Returns:
        Predicted probability of adverse outcome (0 to 1)
    """
    log_odds = intercept
    for var, coef in coefficients.items():
        value = patient_data.get(var, 0)
        log_odds += coef * value

    # Sigmoid function
    probability = 1 / (1 + np.exp(-log_odds))
    return float(probability)


# Pre-built model coefficients for common VQI risk models
# These are illustrative - real coefficients would come from VQI national data
CAROTID_MORTALITY_MODEL = {
    "coefficients": {
        "age_over_80": 0.85,
        "diabetes": 0.35,
        "chf": 1.2,
        "copd": 0.45,
        "renal_insufficiency": 0.75,
        "emergent": 1.5,
        "symptomatic": 0.55,
    },
    "intercept": -5.2,
}

EVAR_MORTALITY_MODEL = {
    "coefficients": {
        "age_over_80": 0.65,
        "diabetes": 0.25,
        "chf": 1.4,
        "copd": 0.55,
        "renal_insufficiency": 0.90,
        "emergent": 2.1,
        "aneurysm_diameter_over_65mm": 0.45,
    },
    "intercept": -4.8,
}
