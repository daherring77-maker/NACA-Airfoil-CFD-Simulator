"""
su2_config_generator.py
Generates SU2 configuration files dynamically based on simulation parameters.
"""

import os


def generate_su2_config(
    mesh_filename,
    use_bl,
    mach,
    aoa,
    reynolds,
    mesh_topology,
    geometry_type,
    log_mesh_type,
    cfl,
    num_iter
    
):
    """
    Generates a complete SU2 configuration string.
    
    Parameters:
    -----------
    mesh_filename : str
        Name of the mesh file (no path - SU2 runs from workspace dir)
    use_bl : bool
        Whether boundary layer is enabled (RANS vs EULER)
    mach : float
        Freestream Mach number
    aoa : float
        Angle of attack in degrees
    reynolds : float
        Reynolds number
    mesh_topology : str
        One of: "Structured (C-H Grid)", "Hybrid C Grid", "Circle", "Box"
    geometry_type : str
        One of: "Single Airfoil", "Multi-Element (Flap)"
    flap_deflection : float, optional
        Flap deflection angle in degrees (default: 0)
    
    Returns:
    --------
    str : Complete SU2 configuration as a string
    """
    
    # Determine boundary conditions based on farfield shape
    if mesh_topology == "Structured (C-H Grid)":
        # Structured meshes use a single 'farfield' marker
        bc_definitions = "MARKER_FAR= ( farfield )"
    elif mesh_topology == "Hybrid C Grid":
        # Tell SU2 that both markers act as the farfield
        bc_definitions = "MARKER_FAR= ( farfield )"    
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

    return su2_config


def write_config_to_workspace(config_string, workspace_dir, filename="config.cfg"):
    """
    Writes the config string to a file in the workspace directory.
    
    Parameters:
    -----------
    config_string : str
        The config content to write
    workspace_dir : str
        Path to the workspace directory
    filename : str
        Output filename (default: "config.cfg")
    
    Returns:
    --------
    str : Full path to the written config file
    """
    config_path = os.path.join(workspace_dir, filename)
    with open(config_path, 'w') as f:
        f.write(config_string)
    return config_path