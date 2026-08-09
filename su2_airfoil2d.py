import streamlit as st

# ----------------------------
# Main App
# ----------------------------
pages = {
        "SU2 Code - Using gmshairfoil2d": [
           st.Page("pages/su2_faqs.py", title="SU2 Code FAQs", icon="📊"),
           st.Page("pages/aero2d_runner.py", title="NACA CFD Streamlit", icon="📊"),
           st.Page("pages/cl_vs_aoa.py", title="CL versus AOA", icon="📊"),
           st.Page("pages/cl_vs_flap_deflection.py", title="CL versus Flap Deflection", icon="📊"),
        ],
        
        }
       
pg = st.navigation(pages)
pg.run()