from datetime import datetime
import os

def to_native(val):
    # Convert numpy scalars to native Python types
    if hasattr(val, "item"):
        return val.item()
    return val

def name_run_output(name, out, leverage, ftype):
   """
    Create a file name for output files.

    Parameters
    ----------
    name :str
        file name
    out : str
        Base output path or directory.
    leverage : list[float]
        List of leverage values.
    ftype : str
        File extension or type (e.g., 'csv', 'png').

    Returns
    -------
    str
        Generated file name with leverage values and timestamp.
    """
   timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   lev_str = "_".join(str(lev) for lev in leverage)
   fname = os.path.join(out, f"{name}_lev_{lev_str}_run_{timestamp}.{ftype}")
   return fname

def is_not_numeric(val):
    try:
        float(val)
        return False
    except (ValueError, TypeError):
        return True

