import streamlit as st
import subprocess
import pathlib
import pyvista as pv
import matplotlib.pyplot as plt
import numpy as np
import os
from modules.run_summary import create_run_summary
from modules.log_file import append_to_run_log 

# --- Page Config ---
st.set_page_config(page_title="NACA CFD Streamlit", layout="wide")

# --- Helper: Path Management ---
WORK_DIR = pathlib.Path("cfd_workspace").absolute()
WORK_DIR.mkdir(exist_ok=True)
log_file = WORK_DIR / "run_log.csv"
DEFAULT_MESH_SIZE = 0.01

def get_su2_cfg_path(): return WORK_DIR / "inv_config.cfg"

st.sidebar.header("🛠️ CFD Parameters")

# --- Group 1: Geometry ---
with st.sidebar.expander("📐 Geometry & Mesh", expanded=True):
    geometry_type = st.radio("Configuration", 
                             ["Single Airfoil", "Multi-Element (Flap)"],
                             index=0)
    
    if geometry_type == "Single Airfoil":
        airfoil_source = st.radio("Airfoil Source", ["NACA 4-Digit", "Database Name"])
        if airfoil_source == "NACA 4-Digit":
            airfoil_param = st.text_input("NACA Code", "0012")
            mesh_airfoil_flag = "--naca"
        else:
            airfoil_param = st.text_input("Airfoil Name", "CH10SM")
            mesh_airfoil_flag = "--airfoil"
            
    else:  # Multi-Element (Flap)
        st.subheader("Multi-Element Airfoil (Flap) Configuration")
        
        # Base directory for your test data
        test_data_dir = r"E:\Streamlit\Su2_Code\tests\test_data"
        
        flap_config = st.selectbox("Flap Configuration", 
                                    ["NLR 7301 (Predefined)", 
                                    "Custom (Manual Paths)"])
        
        if flap_config.startswith("NLR 7301"):
            main_airfoil_path = os.path.join(test_data_dir, "NLR_7301.dat")
            flap_path = os.path.join(test_data_dir, "Flap_NLR_7301.dat")
            
            col1, col2 = st.columns(2)
            with col1:
                flap_angle = st.slider("Flap Deflection (°)", -15, 30, 15, 
                                        help="Positive values typically deflect trailing edge down.")
            with col2:
                st.info(f"**Main Airfoil:** `NLR_7301.dat`\n**Flap:** `Flap_NLR_7301.dat`")
            airfoil_param = "NLR_7301_Flap"
                           
             
  
    # --- NEW: Mesh Topology Selection ---
    st.markdown("---")
    # 1. Initialize all possible variables to None at the top.
    # This prevents "UnboundLocalError" if the user switches topologies 
    # and a variable from a previous block is called later in the script.
    farfield_radius = None
    box_length = None
    box_height = None
    first_layer = None
    wake_elements = None
    height_elements = None
    ext_mesh_size = None
    "---"
    
    
    # This variable will hold the exact string you want in your log file
    log_mesh_type = None 

    mesh_topology = st.radio(
        "Mesh Topology",
        ["Unstructured (Circle/Box)", "Structured (C-H Grid)", "Hybrid C Grid"],
        index=0,
        help="Unstructured: Standard mesh with flexible domain shapes. Structured: Organized C-H grid requiring specific resolution parameters."
    )

    if mesh_topology == "Unstructured (Circle/Box)":
        farfield_ui_choice = st.radio("Farfield Shape", ["Circle", "Box"], index=0)

        # Map the UI choice directly to the exact string for the log file
        log_mesh_type = farfield_ui_choice 

        if farfield_ui_choice == "Circle":
            farfield_radius = st.slider("Farfield Radius (chords)", 5.0, 50.0, 10.0, 1.0)
        else:
            st.write("Box Dimensions (chords):")
            col1, col2 = st.columns(2)
            with col1:
                box_length = st.slider("Length (X)", 5.0, 50.0, 15.0, 1.0)
            with col2:
                box_height = st.slider("Height (Y)", 5.0, 50.0, 10.0, 1.0)

    elif mesh_topology == "Structured (C-H Grid)":
        st.info("📐 Structured mesh requires specific resolution parameters")

        # Hardcode the exact string for the log file
        log_mesh_type = "C-Type" 

        first_layer = st.number_input(
            "First Layer Height", 
            min_value=0.0001, 
            value=0.01, 
            step=0.001, 
            format="%.4f",
            help="Height of the first boundary layer cell"
        )
    # Add your wake_elements and height_elements inputs here...
        col1, col2 = st.columns(2)
        with col1:
            wake_elements = st.number_input(
                "Wake Elements (x)", 
                min_value=1, 
                value=6, 
                step=1,
                help="Number of elements in wake region"
            )
        with col2:
            height_elements = st.number_input(
                "Height Elements (y)", 
                min_value=1, 
                value=7, 
                step=1,
                help="Number of elements in vertical direction"
            )
    elif mesh_topology == "Hybrid C Grid":
        st.info("🔀 Hybrid mesh combines structured boundary layers with an unstructured outer fill.")

    # Hardcode the exact string for the log file
        log_mesh_type = "Hybrid"

        # Add the new parameter you discovered for the hybrid mesh
        ext_mesh_size = st.number_input(
            "External Mesh Size (m)",
            min_value=0.01,
            value=0.2,
            step=0.01,
            format="%.2f",
            help="Target size of the unstructured triangles in the outer region (default 0.2m)."
        )

    # ==========================================
    # LATER IN YOUR CODE (Execution & Logging)
    # ==========================================

    # 1. Write to your log file using the exact string:
    # log_file.write(f"Mesh Topology Selected: {log_mesh_type}\n")

    # 2. Build your CLI command. 
    # Assuming gmshairfoil2d expects lowercase for the --farfield_ctype argument:
    #cli_farfield_arg = log_mesh_type.lower() # Converts "C-type" to "c-type", "Hybrid" to "hybrid", etc.
 
    # Conditionally add the ext_mesh_size if it was defined (Hybrid mesh)
    #if ext_mesh_size is not None:
    #    cmd.extend(["--ext_mesh_size", str(ext_mesh_size)])
        
    # --- Continue with common parameters ---
    use_bl = st.checkbox("Enable Boundary Layer (Viscous/RANS)", value=False)
    if use_bl:
        st.info("ℹ️ BL is enabled by default in mesher. Omitting --no_bl flag.")

    airfoil_mesh_size = st.slider(
        "Mesh Size (chords)", 
        min_value=0.001, 
        max_value=0.015, 
        value=DEFAULT_MESH_SIZE, 
        step=0.001,
        format="%.3f"
    )

            
    # At the top of your execution block, create a dynamic filename
    safe_name = airfoil_param.replace(" ", "_").lower() # e.g., "ch10sm" or "0012"
    mesh_filename = f"mesh_airfoil_{safe_name}.su2"
    # Farfield options continue as before...
    # BL is enabled by default in mesher. Omitting --no_bl flag.")

    # --- Group 2: Flow Physics ---
with st.sidebar.expander("🌪️ Flow Conditions", expanded=True):
    mach = st.slider("Mach Number", 0.1, 0.8, 0.3, 0.05)
    aoa = st.slider("Angle of Attack (°)", -5.0, 15.0, 5.0, 0.5)
    
    if use_bl:
        reynolds = st.number_input("Reynolds Number", value=6000000, step=100000)
    else:
        reynolds = 0.0 # Dummy value for Euler

# --- Group 3: Solver Controls ---
with st.sidebar.expander("⚙️ Solver Controls", expanded=False):
    cfl = st.slider("CFL Number", 1.0, 20.0, 10.0 if not use_bl else 5.0, 0.5)
    num_iter = st.slider("Max Iterations", 100, 10000, 500, 100)

st.sidebar.markdown("---")
run_sim = st.sidebar.button("🚀 Generate Mesh & Run SU2", type="primary", width='stretch')

# --- Main Area ---
st.title("NACA Airfoil CFD Simulator")

# Determine boundary conditions based on farfield shape
if mesh_topology == "Structured (C-H Grid)":
    # Structured meshes use a single 'farfield' marker
    bc_definitions = "MARKER_FAR= ( farfield )"
elif mesh_topology == "Hybrid C Grid":
    # Tell SU2 that both markers act as the farfield
    bc_definitions = "MARKER_FAR= ( farfield, PhysicalLine5 )"    
elif log_mesh_type == "Circle":
    bc_definitions = "MARKER_FAR= ( farfield )"
else:  # Box
    bc_definitions = "MARKER_FAR= ( inlet, outlet, wall )"

# Determine Marker Heatflux conditions based on Geometry Type
if geometry_type == "Single Airfoil":
    mh_definitions = "MARKER_HEATFLUX= ( airfoil, 0.0 )" if use_bl else "MARKER_EULER= ( airfoil )"
else:
    mh_definitions = "MARKER_HEATFLUX= ( airfoil, flap )" if use_bl else "MARKER_EULER= ( airfoil, flap )"

# Dynamically generate SU2 Config String
su2_config = f"""% --- Mesh & Problem ---
MESH_FILENAME= {mesh_filename}
MESH_FORMAT= SU2
SOLVER= {"RANS" if use_bl else "EULER"}
MATH_PROBLEM= DIRECT
KIND_TURB_MODEL= {"SA" if use_bl else "NONE"}

% --- Physical Conditions ---
MACH_NUMBER= {mach}
AOA= {aoa}
FREESTREAM_PRESSURE= 101325.0
FREESTREAM_TEMPERATURE= 288.15
GAS_CONSTANT= 287.87
SPECIFIC_HEAT_CP= 1004.5

% --- Viscous Conditions (Required for RANS) ---
REYNOLDS_NUMBER= {reynolds}
REYNOLDS_LENGTH= 1.0

% --- Boundary Conditions ---
{bc_definitions}
{mh_definitions}
MARKER_PLOTTING= ( airfoil )
MARKER_MONITORING= ( airfoil )
REF_ORIGIN_MOMENT_X= 0.25
REF_ORIGIN_MOMENT_Y= 0.25
REF_ORIGIN_MOMENT_Z= 0.25
REF_LENGTH= 1.0
REF_AREA= 1.0

% --- Convergence Strategy ---
CONV_FIELD= RMS_DENSITY
CONV_RESIDUAL_MINVAL= -6
CONV_STARTITER= 10

% --- Cauchy criterion on forces (stops when CL stabilizes) ---
CONV_CAUCHY_ELEMS= 100
CONV_CAUCHY_EPS= 1E-4

% --- Numerical stabilization ---
CONV_NUM_METHOD_FLOW= JST
JST_SENSOR_COEFF= ( 0.5, 0.02 )

% --- Multigrid (optional but powerful) ---
MGLEVEL= 2
MGCYCLE= W_CYCLE
MG_DAMP_PROLONGATION= 0.75

% --- Adaptive CFL ---
CFL_NUMBER= {cfl} 
CFL_ADAPT= YES
CFL_ADAPT_PARAM= ( 0.1, 2.0, 5.0, 100.0 )
ITER= {num_iter}

% --- Output ---
OUTPUT_FILES= PARAVIEW, SURFACE_PARAVIEW_ASCII
SCREEN_OUTPUT= (INNER_ITER, RMS_DENSITY, LIFT, DRAG)
HISTORY_OUTPUT= INNER_ITER, RMS_DENSITY, LIFT, DRAG, MOMENT_Z
"""

with st.expander("📄 View Generated SU2 Config"):
    st.code(su2_config, language="ini")

# --- Execution Engine ---
if run_sim:
    with st.status("Running CFD Pipeline...", expanded=True) as status:
        try:
            # 1. Generate Mesh
            status.write("⚙️ Generating mesh with gmshairfoil2d...")
            # If use_bl is True, we pass nothing (letting the default happen).
            # If use_bl is False, we explicitly pass "--no_bl".
            # Build mesh command
            if geometry_type == "Single Airfoil": 
                mesh_cmd = ["gmshairfoil2d", mesh_airfoil_flag, airfoil_param]
                    
            else:
                #geometry_type == "Multi-Element (Flap)" 
                mesh_cmd = ["gmshairfoil2d"]
                mesh_cmd.extend(["--airfoil_path", str(main_airfoil_path)])
                mesh_cmd.extend(["--flap_path", str(flap_path)])
                mesh_cmd.extend(["--deflection", f"{int(flap_angle)}"])

            if mesh_topology == "Unstructured (Circle/Box)":
                # Add farfield parameters
                if log_mesh_type == "Circle":
                    mesh_cmd.extend(["--farfield", str(farfield_radius)])
                else:  # Box
                    mesh_cmd.extend(["--box", f"{box_length}x{box_height}"])

            elif mesh_topology  == "Structured (C-H Grid)":        
                mesh_cmd.append("--structured")
                mesh_cmd.extend(["--first_layer", str(first_layer)])
                mesh_cmd.extend(["--arg_struc", f"{int(wake_elements)}x{int(height_elements)}"])
                # Conditionally add the ext_mesh_size if it was defined (Hybrid mesh)
            else:
                mesh_topology = "Hybrid C Grid" 
                mesh_cmd.append("--farfield_ctype")   
                if ext_mesh_size is not None:
                        mesh_cmd.extend(["--ext_mesh_size", str(ext_mesh_size)])
                        

            # Add common parameters
            if not use_bl:
                mesh_cmd.append("--no_bl")
                
            mesh_cmd.extend(["--airfoil_mesh_size", str(airfoil_mesh_size)])
            #mesh_cmd.extend(["--output", mesh_filename])
           
            bl_flag = [] if use_bl else ["--no_bl"]              
                         
            mesh_result = subprocess.run(mesh_cmd, capture_output=True, text=True, check=True, cwd=WORK_DIR)
            status.write("✅ Mesh generated successfully.")

            # 2. Write SU2 Config
            get_su2_cfg_path().write_text(su2_config)
            status.write("💾 SU2 config file written.")

            # 3. Run SU2
            status.write("🌪️ Running SU2_CFD solver...")
            solve_cmd = ["SU2_CFD", "inv_config.cfg"]
            solve_result = subprocess.run(solve_cmd, capture_output=True, text=True, check=True, cwd=WORK_DIR)
            status.write("✅ SU2 simulation completed.")
            
            status.update(label="Simulation Complete!", state="complete", expanded=False)
                    
            # 4. Create Run Summary
            status.write("📊 Generating run summary...")
            run_params = {
                "airfoil_param": airfoil_param,
                "airfoil_type": mesh_airfoil_flag if 'airfoil_type' in locals() else "NACA",
                "aoa": aoa,
                "mach": mach,
                "reynolds": reynolds if use_bl else 0,
                "farfield_type": log_mesh_type,
                "use_bl": use_bl,
                "num_iter": num_iter,
            }
            summary = create_run_summary(run_params, WORK_DIR)
            status.write("✅ Run summary saved.")
            
            status.update(label="Simulation Complete!", state="complete", expanded=False)
        except subprocess.CalledProcessError as e:
                    st.error("❌ Simulation failed!")
                    st.code(f"STDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}")
                    st.stop()
    
    # --- Display the Run Summary ---
    st.success("Simulation finished!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lift Coefficient (CL)", f"{summary['results']['CL']:.4f}")
    with col2:
        st.metric("Drag Coefficient (CD)", f"{summary['results']['CD']:.5f}")
    with col3:
        st.metric("L/D Ratio", 
                f"{summary['results']['CL']/summary['results']['CD']:.1f}" 
                if summary['results']['CD'] > 0 else "∞")
    
    with st.expander("📋 Full Run Summary"):
        st.json(summary)

    append_to_run_log(summary, log_file)    

    # --- VERBOSE OUTPUT EXPANDER ---
    st.success("Simulation finished! Check the outputs below.")
    with st.expander("🖥️ View Terminal Output (Verbose)"):
        st.markdown("**Gmsh Output:**")
        st.code(mesh_result.stdout if mesh_result.stdout else "No output")
        st.markdown("**SU2 Output:**")
        st.code(solve_result.stdout if solve_result.stdout else "No output")
        if solve_result.stderr:
            st.markdown("**SU2 Errors/Warnings:**")
            st.error(solve_result.stderr)

    # --- DYNAMIC FILE DISCOVERY ---
    st.markdown("### 📂 Generated Files")
    files = [f.name for f in WORK_DIR.iterdir() if f.suffix in ['.vtk', '.vtu', '.csv', '.su2']]
    st.write(f"Found {len(files)} relevant files: `{', '.join(files)}`")

    # --- Visualization ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Flow Field (Mach)")
        # Find any volume/solution vtk file
        vol_files = [f for f in WORK_DIR.iterdir() if f.suffix in ['.vtk', '.vtu'] and 'surface' not in f.name.lower()]
        if vol_files:
            try:
                vtk_data = pv.read(vol_files[0])
                # Find Mach array dynamically
                mach_key = next((k for k in vtk_data.point_data.keys() if "Mach" in k), None)
                scalar_to_plot = mach_key if mach_key else None
                
                plotter = pv.Plotter(window_size=[400, 400], off_screen=True)
                plotter.add_mesh(vtk_data, scalars=scalar_to_plot, cmap="jet")
                plotter.view_xy()
                plotter.screenshot("flow_field.png", window_size=[1600, 1000])
                st.image("flow_field.png", width='stretch')
                if not mach_key:
                    st.warning(f"Could not find 'Mach' array. Available: {list(vtk_data.point_data.keys())}")
            except Exception as e:
                st.warning(f"Could not load volume VTK: {e}")
        else:
            st.warning("No volume solution file found.")

    with col2:
        st.subheader("Pressure Coefficient (Cp)")
        # Find surface vtk file
        surf_files = [f for f in WORK_DIR.iterdir() if f.suffix in ['.vtk', '.vtu'] and 'surface' in f.name.lower()]
        if surf_files:
            try:
                surface = pv.read(surf_files[0])
                # Find Pressure array dynamically
                cp_key = next((k for k in surface.point_data.keys() if "Pressure" in k), None)
                
                if cp_key:
                    cp = surface.point_data[cp_key]
                    x = surface.points[:, 0]
                    sort_idx = np.argsort(x)
                    
                    fig, ax = plt.subplots(figsize=(5, 4))
                    ax.plot(x[sort_idx], cp[sort_idx], 'b-', linewidth=2)
                    ax.set_xlabel("X/C")
                    ax.set_ylabel(cp_key) # Dynamic label
                    ax.invert_yaxis()
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                else:
                    st.warning(f"Could not find 'Pressure' array. Available: {list(surface.point_data.keys())}")
            except Exception as e:
                st.warning(f"Could not plot Cp: {e}")
        else:
            st.warning("No surface VTK file found. Check if MARKER_PLOTTING is set in config.")