# CODE ARTIFACT: scoring_engine.py
# SYSTEM MODULE: HOLDS SYSTEM CREDIT SCORING LOGIC MATRICES

def compute_credit_profile(gst_delay, upi_volatility, workforce_delta, power_slope):
    """
    Executes core algebraic grading algorithms for alternative data streams.
    Returns composite density metrics and standard credit rating bands.
    """
    gst_score = max(0, 100 - (float(gst_delay) * 3.5))
    upi_score = max(0, 100 - (float(upi_volatility) * 1.1))
    epfo_score = min(100, max(0, 80 + (int(workforce_delta) * 10)))
    power_score = min(100, max(0, 75 + (float(power_slope) * 0.02)))

    composite_percentage = (gst_score * 0.30) + (upi_score * 0.30) + (epfo_score * 0.15) + (power_score * 0.25)
    final_credit_score = int(300 + (composite_percentage * 6))

    if final_credit_score >= 750:
        verdict = "DISCIPLINED (YES GO)"
        description = "The enterprise displays robust cross-network operational health."
        color_theme = {"bg": "#dcfce7", "text": "#166534"}
    elif final_credit_score >= 550:
        verdict = "NON-DISCIPLINED (MANUAL REVIEW)"
        description = "The applicant exhibits decent baselines but displays localized operational volatility."
        color_theme = {"bg": "#fef3c7", "text": "#92400e"}
    else:
        verdict = "STRESSED (NO GO)"
        description = "High operational risk detected. Critical ambient indicators point to systemic stress."
        color_theme = {"bg": "#fee2e2", "text": "#991b1b"}

    return {
        "credit_score": f"{final_credit_score} / 900",
        "percentage": f"{round(composite_percentage, 1)}%",
        "verdict": verdict,
        "description": description,
        "theme": color_theme
    }