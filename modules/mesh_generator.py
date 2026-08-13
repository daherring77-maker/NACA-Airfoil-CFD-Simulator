"""
mesh_generator.py
Shared mesh generation logic for both direct and adjoint simulations.
"""

import subprocess
import os
import streamlit as st


def build_mesh_command(mesh_filename, 
                       geometry_type, 
                       mesh_topology, 
                       use_bl, 
                       mesh_airfoil_flag, 
                       airfoil_param, 
                       log_mesh_type, 
                       farfield_radius, 
                       box_length, 
                       box_height, 
                       wake_elements, 
                       first_layer, 
                       growth_ratio, 
                       num_layers, 
                       airfoil_mesh_size, 
                       ext_mesh_size, 
                       height_elements, 
                       main_airfoil_path, 
                       flap_path, 
                       flap_angle):
    """
    Builds the gmshairfoil2d command based on geometry and mesh type.
    
    Returns:
        list: Command arguments for subprocess
    """
    mesh_args = []
    
    # Geometry-specific arguments
   # if geometry_type == "Single Airfoil":
   #     mesh_args.extend(airfoil_params)
   # elif geometry_type == "Multi-Element (Flap)":
   #     mesh_args.extend(flap_params)
    
    # Mesh topology arguments
   # if mesh_type == "Structured (C-H Grid)":
   #     mesh_args.extend(["--structured"])
   # elif mesh_type == "Hybrid C Grid":
   #     mesh_args.extend(["--hybrid"])
    
   # return ["gmshairfoil2d"] + mesh_args

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
        mesh_cmd.extend(["--arg_struc", f"{int(wake_elements)}x{int(height_elements)}"])
        
    else:
        mesh_topology = "Hybrid C Grid" 
        mesh_cmd.append("--farfield_ctype")   
        mesh_cmd.extend(["--arg_struc", f"{int(wake_elements)}x{int(height_elements)}"])                     

    # Add common parameters
    if not use_bl:
        mesh_cmd.append("--no_bl")
    else:
        mesh_cmd.extend([
                    "--first_layer", str(first_layer),
                    "--ratio", str(growth_ratio),
                    "--nb_layers", str(num_layers)
                ])    
        
    mesh_cmd.extend(["--airfoil_mesh_size", str(airfoil_mesh_size)])
    mesh_cmd.extend(["--ext_mesh_size", str(ext_mesh_size)])
    
    bl_flag = [] if use_bl else ["--no_bl"]              
    return(mesh_cmd)                
    #mesh_result = subprocess.run(mesh_cmd, capture_output=True, text=True, check=True, cwd=WORK_DIR)
    #status.write("✅ Mesh generated successfully.")
    #full_mesh_path = os.path.join(WORK_DIR, mesh_filename)

def generate_mesh(mesh_cmd, workspace_dir):
    """
    Executes mesh generation and handles cleanup.
    
    Returns:
        str: Path to generated mesh file
    """
    result = subprocess.run(
        mesh_cmd,
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Mesh generation failed: {result.stderr}")
    
    # Find the generated mesh file
    import glob
    mesh_files = glob.glob(os.path.join(workspace_dir, "*.su2"))
    if not mesh_files:
        raise Exception("No mesh file generated")
    
    mesh_path = max(mesh_files, key=os.path.getmtime)
    
    # Clean hybrid mesh if needed
    if "hybrid" in mesh_cmd:
        from .mesh_cleaner import clean_hybrid_mesh
        clean_hybrid_mesh(mesh_path)
    
    return mesh_path