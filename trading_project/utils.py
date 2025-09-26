# trading_project/utils.py
import pandas as pd

def format_date_for_display(date_obj):
    """Formats a date object into a human-readable string."""
    if isinstance(date_obj, pd.Timestamp):
        return date_obj.strftime('%Y-%m-%d')
    return str(date_obj)

# Add other utility functions here
