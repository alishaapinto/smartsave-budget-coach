from flask import current_app


def format_inr(value):
    try:
        amt = float(value or 0)
    except Exception:
        return value
    # Since database values are already in INR, format directly
    return f"₹{amt:,.2f}"
