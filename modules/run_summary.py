import json
import pandas as pd
from datetime import datetime

def create_run_summary(params, work_dir):
    """
    Parses SU2 history.csv and creates a comprehensive run summary.
    
    Args:
        params: dict of all input parameters (airfoil, AoA, Mach, Re, etc.)
        work_dir: pathlib.Path to the cfd_workspace folder
    
    Returns:
        dict: Complete run summary
    """
    history_file = work_dir / "history.csv"
    
    if not history_file.exists():
        return {"error": "history.csv not found"}
    
    # Parse the history file
    df = pd.read_csv(history_file, skipinitialspace=True)
    
    # Clean column names (SU2 sometimes adds spaces)
    df.columns = [c.strip().strip('"') for c in df.columns]
    
    # Get the final row (converged values)
    final = df.iloc[-1]
    
    # Extract key values safely
    def safe_get(row, key, default=0.0):
        try:
            return float(row[key])
        except (KeyError, ValueError):
            return default

    # Robust extraction function that tries multiple possible column names
    def get_val(df, possible_names, default=0.0):
        last_row = df.iloc[-1]
        for name in possible_names:
            # Clean the column name just in case SU2 added spaces or quotes
            clean_cols = [c.strip().strip('"').strip() for c in df.columns]
            for i, clean_name in enumerate(clean_cols):
                if clean_name.lower() == name.lower():
                    try:
                        return float(df.iloc[-1].iloc[i])
                    except (ValueError, TypeError):
                        pass
        return default
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "status": "converged" if len(df) < params.get("num_iter", 99999) else "max_iterations",
        
        # Input Parameters
        "inputs": {
            "airfoil": params.get("airfoil_param"),
            "airfoil_type": params.get("airfoil_type"),
            "aoa_deg": params.get("aoa"),
            "mach": params.get("mach"),
            "reynolds": params.get("reynolds"),
            "farfield_type": params.get("farfield_type"),
            "boundary_layer": params.get("use_bl"),
            "solver": "RANS" if params.get("use_bl") else "EULER",
            "turbulence_model": "SA" if params.get("use_bl") else "NONE",
        },
                
        "results": {
            "CL": get_val(df, ["CL", "Total_CL", "CLift"]),
            "CD": get_val(df, ["CD", "Total_CD", "CDrag"]),
            "CM": get_val(df, ["CMz", "Total_CMz", "CM"]),
            "Lift_N": get_val(df, ["Lift", "Total_Lift"]),
            "Drag_N": get_val(df, ["Drag", "Total_Drag"]),
        },
                
        # Convergence
        "convergence": {
            "iterations": int(safe_get(final, "Inner_Iter")),
            "final_residual": safe_get(final, "rms[Rho]", safe_get(final, "res[Rho]")),
            "converged": safe_get(final, "rms[Rho]", -1) < -6,
        },
        
        # Files generated
        "output_files": [f.name for f in work_dir.glob("*.*") if f.suffix in ['.vtk', '.vtu', '.csv', '.su2']]
    }
    
    # Save to JSON
    summary_file = work_dir / f"run_summary_{params.get('airfoil_param')}_{params.get('aoa')}deg.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary