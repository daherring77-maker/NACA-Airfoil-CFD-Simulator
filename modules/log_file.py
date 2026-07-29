import pandas as pd

def append_to_run_log(summary, log_file):
    """Appends a run summary to a cumulative CSV log."""
    flat_row = {
        "timestamp": summary["timestamp"],
        "airfoil": summary["inputs"]["airfoil"],
        "aoa": summary["inputs"]["aoa_deg"],
        "mach": summary["inputs"]["mach"],
        "reynolds": summary["inputs"]["reynolds"],
        "farfield": summary["inputs"]["farfield_type"],
        "viscous": summary["inputs"]["boundary_layer"],
        "iterations": summary["convergence"]["iterations"],
        "CL": summary["results"]["CL"],
        "CD": summary["results"]["CD"],
        "L/D": summary["results"]["CL"]/summary["results"]["CD"] if summary["results"]["CD"] > 0 else 0,
    }
    
    df_new = pd.DataFrame([flat_row])
    if log_file.exists():
        df_new.to_csv(log_file, mode='a', header=False, index=False)
    else:
        df_new.to_csv(log_file, index=False)