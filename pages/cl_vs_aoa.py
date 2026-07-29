import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import pathlib

WORK_DIR = pathlib.Path("cfd_workspace").absolute()

# Load your database
log_file = WORK_DIR / "run_log.csv"
if log_file.exists():
    df_log = pd.read_csv(log_file)

st.subheader("CL vs AOA: Domain Comparison")

# Filter for specific airfoil and conditions
selected_airfoil = st.selectbox("Select Airfoil", df_log['airfoil'].unique())
selected_mach = st.selectbox("Select Mach", df_log['mach'].unique())

df_log = df_log.sort_values('aoa')

# Filter the data
df_filtered = df_log[
    (df_log['airfoil'] == selected_airfoil) & 
    (df_log['mach'] == selected_mach)
]

# Create the plot with color coding by domain type
fig = px.line(
    df_filtered,
    x='aoa',
    y='CL',
    color='farfield',  # This creates separate lines for Box and Circle
    markers=True,
    title=f"{selected_airfoil} at Mach {selected_mach}",
    labels={
        'aoa': 'Angle of Attack (degrees)',
        'CL': 'Lift Coefficient (CL)',
        'farfield': 'Domain Type'
    }
)

# Customize the layout
fig.update_layout(
    hovermode='x unified',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

st.plotly_chart(fig, width = 'content')
# Show data table
st.subheader("Raw Data")
st.dataframe(df_filtered.sort_values(['farfield', 'aoa']))

st.subheader("📚 Run History")
log_file = WORK_DIR / "run_log.csv"
if log_file.exists():
    df_log = pd.read_csv(log_file)
    st.dataframe(df_log, width='stretch')
    
    # Bonus: Plot CL vs AoA
    fig, ax = plt.subplots()
    for airfoil in df_log['airfoil'].unique():
        subset = df_log[df_log['airfoil'] == airfoil].sort_values('aoa')
        ax.plot(subset['aoa'], subset['CL'], 'o-', label=airfoil)
    ax.set_xlabel("Angle of Attack (°)")
    ax.set_ylabel("CL")
    ax.legend()
    st.pyplot(fig)