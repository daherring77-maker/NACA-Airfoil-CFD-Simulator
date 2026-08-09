import streamlit as st
import pandas as pd
import os, pathlib
import matplotlib.pyplot as plt

st.set_page_config(page_title="NACA CFD Streamlit", layout="wide")

def plot_flap_deflection_sweep():
    """
    Creates plots showing CL and CD vs flap deflection for a given airfoil and AOA.
    """
    st.subheader("Flap Deflection Sweep Analysis")
    WORK_DIR = pathlib.Path("cfd_workspace").absolute()
    # Load the run log
    log_file = WORK_DIR / "run_log.csv"
    if not os.path.exists(log_file):
        st.warning("No run_log.csv found. Run some simulations first!")
        return
    
    df = pd.read_csv(log_file)
    
    # Filter to only flap simulations (deflection > 0 or explicit flap config)
    flap_df = df[df['deflection'] > 0].copy()
    
    if flap_df.empty:
        st.info("No flap deflection data found. Run flap simulations with various deflection angles.")
        return
    
    # Get unique airfoils and AOAs from flap data
    available_airfoils = flap_df['airfoil'].unique()
    available_aoas = flap_df['aoa'].unique()
    
    # User selection
    col1, col2 = st.columns(2)
    with col1:
        selected_airfoil = st.selectbox("Select Airfoil", available_airfoils)
    with col2:
        selected_aoa = st.selectbox("Select AOA (°)", available_aoas)
    
    # Filter data for selected airfoil and AOA
    plot_df = flap_df[(flap_df['airfoil'] == selected_airfoil) & 
                      (flap_df['aoa'] == selected_aoa)].copy()
    
    if plot_df.empty:
        st.warning(f"No data found for {selected_airfoil} at {selected_aoa}° AOA with flap deflection.")
        return
    
    # Sort by deflection
    plot_df = plot_df.sort_values('deflection')
    
    # Create plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # CL vs Deflection
    ax1.plot(plot_df['deflection'], plot_df['CL'], 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Flap Deflection (°)', fontsize=12)
    ax1.set_ylabel('Lift Coefficient (CL)', fontsize=12)
    ax1.set_title(f'{selected_airfoil} at {selected_aoa}° AOA\nCL vs Flap Deflection', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    # Add value labels
    for i, (defl, cl) in enumerate(zip(plot_df['deflection'], plot_df['CL'])):
        ax1.annotate(f'{cl:.3f}', (defl, cl), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9)
    
    # CD vs Deflection
    ax2.plot(plot_df['deflection'], plot_df['CD'], 'ro-', linewidth=2, markersize=8)
    ax2.set_xlabel('Flap Deflection (°)', fontsize=12)
    ax2.set_ylabel('Drag Coefficient (CD)', fontsize=12)
    ax2.set_title(f'{selected_airfoil} at {selected_aoa}° AOA\nCD vs Flap Deflection', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    # Add value labels
    for i, (defl, cd) in enumerate(zip(plot_df['deflection'], plot_df['CD'])):
        ax2.annotate(f'{cd:.4f}', (defl, cd), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Show data table
 #   st.subheader("Raw Data")
 #   display_df = plot_df[['deflection', 'cl', 'cd', 'cm', 'mesh_type', 'physics_type']].copy()
 #   display_df.columns = ['Deflection (°)', 'CL', 'CD', 'CM', 'Mesh Type', 'Physics']
 #  st.dataframe(display_df, width='stretch')
    
    # Summary statistics
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Max CL", f"{plot_df['CL'].max():.3f}", 
                 f"+{plot_df['CL'].max() - plot_df['CL'].min():.3f}")
    with col2:
        st.metric("Min CD", f"{plot_df['CD'].min():.4f}")
    with col3:
        max_cl_defl = plot_df.loc[plot_df['CL'].idxmax(), 'deflection']
        st.metric("Deflection for Max CL", f"{max_cl_defl}°")

summary_df = plot_flap_deflection_sweep()
        