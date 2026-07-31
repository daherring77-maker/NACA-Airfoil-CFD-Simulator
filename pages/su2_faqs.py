import streamlit as st

st.set_page_config(page_title="CFD Solver FAQ", page_icon="🔬", layout="wide")

# ─── Sidebar / branding ──────────────────────────────────────────────
with st.sidebar:
    st.title("🔬 CFD Solver FAQ")
    st.markdown("**Gmsh + SU2** quick-reference guide.")
    st.info("Answers build up over time as you run into real questions.")

# ─── Main page title ─────────────────────────────────────────────────
st.title("💡 Common Questions — Beginner Friendly")
st.caption("Punchy answers to the things nobody explains until it's too late.")
st.divider()

# ─── FAQ 1 ──────────────────────────────────────────────────────────────
with st.expander("Q1: Why is a Reynolds number required whenever a boundary layer is involved, and what's a good choice?"):
    st.write("**Short answer:** The Reynolds number tells the solver *how thick* your boundary layer should be, which drives mesh resolution requirements and turbulence model behavior near walls.")

    st.markdown("### Why Re matters with boundary layers")
    st.write("- **Inertial vs Viscous forces:** Viscous forces dominate inside the boundary layer. Re sets the ratio between them.")
    st.write("- **Boundary-layer thickness:** Roughly delta ≈ L / sqrt(Re) for laminar flow. You must resolve this thin region with your mesh, or wall shear stress and heat transfer will be inaccurate.")
    st.write("- **Turbulence modeling:** Wrong Re → wrong reference viscosity → incorrect turbulent eddy viscosity near walls.")

    st.markdown("### How to pick a good Reynolds number")
    st.latex(r"\text{Re} = \frac{\rho \cdot V \cdot L}{\mu}")
    st.write("| Symbol | Typical source |")
    st.write(":   :--- | :--- |")
    st.write("| rho | Free-stream density (kg/m3) |")
    st.write("| V | Free-stream velocity (m/s) |")
    st.write("| L | Characteristic length (chord, diameter, etc.) |")
    st.write("| mu | Dynamic viscosity at free-stream temperature |")

    st.markdown("### Quick SU2 configuration tip")
    st.code("""REYNOLDS_NUMBER = 3.0e6
FREESTREAM_TEMPERATURE = 288.15   # lets SU2 compute mu via Sutherland's law
VISCOSITY_MODEL = SAUTER""", language="cfg")
    st.info("💡 Using Sutherland's viscosity model is generally preferred because mu changes with temperature inside the boundary layer.")


# ─── FAQ 2 ──────────────────────────────────────────────────────────────
with st.expander("Q2: What are the main differences between using RANS solver and Euler solver in SU2? Are there other choices?"):
    st.write("**Short answer:** Euler solves inviscid flow (fast, no boundary layers). RANS adds viscosity + turbulence modeling (slower but physically complete). SU2 also supports laminar NS, potential flow, LES/DNS, and adjoint formulations.")

    st.markdown("### Euler vs RANS in SU2")
    st.write("| Feature               | Euler Solver                  | RANS Solver                          |")
    st.write(":   :---            | :---                          | :---                                 |")
    st.write("| Physics             | Inviscid (zero viscosity)     | Viscous + turbulent closure          |")
    st.write("| Governing equations | Euler equations               | Reynolds-Averaged Navier-Stokes      |")
    st.write("| Boundary layer      | Ignored entirely              | Resolved (with proper mesh & wall treatment) |")
    st.write("| Drag prediction     | Pressure drag only            | Pressure + viscous skin friction     |")
    st.write("| Mesh requirement    | Moderate/coarse OK            | Fine near walls (y-plus control critical) |")

    st.markdown("### Other SU2 Solver Choices")
    st.write("- **Laminar Navier-Stokes:** Low Reynolds number flows, internal channels, benchmark validation.")
    st.write("- **Potential Flow:** Low-speed subsonic, fast design exploration (inviscid + irrotational).")
    st.write("- **LES / DNS:** High-fidelity transient turbulence research (very expensive, requires fine 3D time-dependent mesh).")
    st.write("- **Adjoint Solver:** Shape optimization & sensitivity analysis (runs after a converged primal solution).")

    st.markdown("### How to switch in SU2.cfg")
    st.code("""% Euler (default if NS_FLOW not set)
EULER_EQULATIONS = YES
NS_FLOW = NO

% RANS (viscous + turbulence)
EULER_EQULATIONS = NO
NS_FLOW = YES
RANS_TURBULENCE_MODEL = SA          % Spalart-Allmaras or k-omega SST
WALL_FUNCTION_TYPE = LOG_LAW""", language="cfg")

    st.info("💡 Note: In SU2, \"RANS\" isn't a separate solver binary. It's the Navier-Stokes solver + a turbulence closure model. You pick both via config keywords.")


# ─── FAQ 3 ──────────────────────────────────────────────────────────────
with st.expander("Q3: What is meant by a structured mesh as opposed to a 'normal' mesh? What are the pros and cons?"):
    st.write("**Short answer:** A *structured* mesh arranges cells in a strict logical grid (like graph paper stretched over your geometry), while an unstructured (\"normal\") mesh uses arbitrary connectivity to fill complex shapes. For most Gmsh → SU2 workflows, unstructured or hybrid meshes are the practical default.")

    st.markdown("### Structured vs Unstructured: Core Difference")
    st.write("| Property            | Structured Mesh                                    | Unstructured Mesh                                        |")
    st.write(":   :---             | :---                                               | :---                                                     |")
    st.write("| Connectivity        | Fixed I-J-K indexing; every cell has exactly 4 faces (2D quad) or 6 faces (3D hex) | Arbitrary adjacency lists; cells can have varying numbers of faces/edges |")
    st.write("| Topology            | Global logical grid that wraps around the domain   | Local patchwork of triangles/tetrahedra glued together   |")
    st.write("| Geometry fit        | Requires manual topology planning (O-grid, H-grid, C-grid) or specialized tools | Handles any CAD import automatically via Delaunay/advancing-front algorithms |")

    st.markdown("### Pros & Cons at a Glance")
    st.write("- **Structured ✅:** Lower numerical diffusion, faster convergence per cell, excellent parallel scalability. ❌ High meshing effort, hard to refine locally.")
    st.write("- **Unstructured ✅:** Handles complex CAD automatically, easy local refinement, industry standard for engineering. ❌ Slightly higher cell count needed for same boundary-layer resolution.")

    st.markdown("### Gmsh + SU2 Reality Check")
    st.write("- Gmsh defaults to unstructured (`Mesh.Algorithm = 5`). This is almost always fine for engineering CAD.")
    st.write("- **Hybrid meshes are the sweet spot:** Unstructured tetrahedra in the far-field + structured/prismatic layers near walls. SU2 reads these seamlessly.")

    st.markdown("### Quick Gmsh tip for boundary layers")
    st.code("""// 1. Generate volume mesh (default unstructured)
Mesh.Algorithm3D = 5; // Tetrahedra

// 2. Add structured prismatic layers on walls
Mesh.BoundaryLayers{AllFaces} = {{10, 0.3, 0.01}}; 
// {n_layers, growth_rate, first_thickness}""", language="gmsh")

    st.info("💡 Bottom line: Don't force structure where CAD demands flexibility. Start with an unstructured + prism boundary layer mesh in Gmsh. Only switch to fully structured if you hit convergence bottlenecks that are strictly topology-dependent.")


# ─── FAQ 4 ──────────────────────────────────────────────────────────────
with st.expander("Q4: Why do I need MARKER_INLET for a box farfield but not a circle farfield? What's the significance of the 6 entries?"):
    st.write("**Short answer:** A circle naturally wraps around your geometry so SU2 can auto-detect it as a pressure farfield where flow freely enters/exits. A box has multiple distinct faces with different physical roles, so SU2 needs explicit markers to know which face gets which boundary condition. The 6 entries define the *stagnation state* and *flow direction* of that wind tunnel inlet.")

    st.markdown("### Circle vs Box: Why one auto-detects and the other doesn't")
    st.write("| Geometry             | How SU2 interprets it                                                                 | Why explicit BCs are usually needed |")
    st.write(":   :---              | :---                                                                                  | :---                                |")
    st.write("| **Circle / O-grid**  | Wrapped topology → outer ring is unmistakably a \"farfield\" where characteristics carry information in/out freely. Older SU2 versions auto-assumed farfield if no explicit marker was given. | Modern best practice: explicitly define it to avoid silent defaults or Mach/Re mismatches. |")
    st.write("| **Box / Wind tunnel**| Topologically symmetric → four faces look identical to the solver. Without markers, SU2 wouldn't know which face supplies flow vs. where it exits.                       | Must explicitly tag MARKER_INLET, MARKER_OUTLET, and optionally MARKER_SYMMETRY or MARKER_WALL. |")

    st.markdown("### The 6 entries decoded: `( Name, Total_Temp, Total_Press, Dir_X, Dir_Y, Dir_Z )`")
    st.write("| Entry                  | Meaning                                              | Why it matters in CFD / SU2 |")
    st.write(":   :---                 | :---                                                 | :---                        |")
    st.write("| `Name` (e.g., inlet)   | The Gmsh physical marker name assigned to that face  | Links geometry to solver's BC table. Must match exactly between `.msh` and `.cfg` |")
    st.write("| `Total_Temp` (288.15 K)| **Stagnation/total temperature** at the inlet        | Converts to static inflow temperature using isentropic relations once local Mach number is known. Sets thermal reference state. |")
    st.write("| `Total_Press` (101325 Pa)| **Stagnation/total pressure** at the inlet           | Combined with Total Temp → fixes free-stream density via ideal gas law. Serves as reference scale for non-dimensionalizing pressure. |")
    st.write("| `Dir_X, Dir_Y, Dir_Z` (1.0, 0.0, 0.0)| **Unit flow direction vector** pointing *into* the domain | Tells SU2 how to decompose total pressure into static + dynamic components. Determines wind direction and AoA relative to reference line. Must be ~unit length. |")

    st.markdown("### How SU2 uses these values behind the scenes")
    st.latex(r"P_{static} = \frac{P_{total}}{\left(1 + \frac{\gamma-1}{2}M^2\right)^{\frac{\gamma}{\gamma-1}}}")
    st.write("SU2 doesn't know your Mach number yet. It iterates the boundary condition to match Total_Temp, Total_Press, and Dir with the interior solution, effectively fixing your free-stream state for Reynolds number calculation, Mach convergence, and non-dimensionalization.")

    st.markdown("### Practical tips & common pitfalls")
    st.write("- **Direction vector:** If your geometry is angled, change Dir to match freestream angle, or rotate CAD so chord/axis aligns with (1,0,0).")
    st.write("- **Subsonic inlet:** Always use Total_Temp + Total_Press. SU2 computes actual mass flux. Never guess static values at inflow.")
    st.write("- **Farfield consistency:** Use identical T_total, P_total, and direction for both MARKER_INLET and MARKER_FARFIELD unless simulating a duct/nozzle gradient.")

    st.info("💡 Modern workflow tip: Regardless of shape, explicitly define your outer boundary as:\n`MARKER_FARFIELD = ( farfield, 288.15, 101325.0, 1.0, 0.0, 0.0 )`\nThis removes auto-detection ambiguity and guarantees correct reference state propagation.")


# ─── FAQ 5 ──────────────────────────────────────────────────────────────
with st.expander("Q5: Purpose of CFL_NUMBER and CFL_ADAPTATION"):
    st.write("**Short answer:** `CFL_NUMBER` sets your initial pseudo-time step size. `CFL_ADAPTATION=YES` tells SU2 to automatically ramp that value up as residuals drop, giving you early stability without manual tuning.")

    st.markdown("### How They Work Together")
    st.write("- **Early iterations (high residuals):** Low CFL acts like a numerical brake, preventing divergence near walls and turbulence layers.")
    st.write("- **Mid to late iterations:** SU2 monitors convergence. When residuals fall below `CFL_ADAPT_TOL`, it multiplies CFL by `CFL_ADAPT_FACTOR` (default 1.3 to 1.5).")
    st.write("- **Result:** You start safe with `CFL = 2`, then the solver ramps the step size automatically behind the scenes.")

    st.latex(r"\Delta t_{\text{pseudo}} = \frac{\text{CFL} \cdot h}{|\mathbf{u}| + c}")
    st.write("where $h$ is the local cell size, $|\\mathbf{u}|$ is velocity magnitude, and $c$ is speed of sound.")

    st.markdown("### Recommended SU2 Configuration")
    st.code("""CFL_NUMBER = 2.0
CFL_ADAPTATION = YES
CFL_ADAPT_TOL   = 1e-4
CFL_ADAPT_FACTOR= 1.5""", language="cfg")


# ─── FAQ 6 ──────────────────────────────────────────────────────────────
with st.expander("Q6: RMS residuals ~1e-6/1e-7 but CL is steady. Why CONVERGED=NO?"):
    st.write("**Short answer:** Your simulation has physically converged. Residuals and integrated forces measure completely different things. Chasing 1e-14 is mathematically impossible and physically meaningless for turbulent RANS CFD.")

    st.markdown("### What Each Metric Actually Measures")
    st.write("| Metric | What it measures | When it indicates readiness |")
    st.write("| :--- | :--- | :--- |")
    st.write("| RMS Residuals | PDE discretization error per iteration | Floors naturally around 1e-6 due to truncation error + turbulence coupling |")
    st.write("| CL / CD / CM | Integrated surface forces and moments | Stable within +/-0.1% over 50–100 iterations = PHYSICALLY CONVERGED |")

    st.latex(r"\mathcal{R}_{\text{floor}} \\approx \\mathcal{O}(h^2) + \\mu_{\\text{turb}} \\text{ coupling terms}")
    st.write("This floor is governed by your mesh resolution and double-precision arithmetic. It cannot be removed without switching to higher-order schemes or analytical solutions.")

    st.markdown("### Fix Your Convergence Check")
    st.write("Stop relying on raw residual thresholds. Tell SU2 to declare convergence based on monitored aerodynamic quantities:")
    st.code("""CONVERGENCE_CONDITION = MONITORED
MONITOR_VARIABLES   = (CL, CD, CM)
CONVERGENCE_TOL     = 1e-6
CONVERGENCE_ITERATIONS = 50""", language="cfg")

    st.info("💡 Bottom line: If CL and CD stabilize over ~50 iterations and your boundary layer is properly resolved (y-plus approx 1 for wall-resolved, or under 50 for wall functions), export your results. The solver is working correctly—you have hit the natural numerical floor of turbulent RANS.")

# ─── FAQ 7 ──────────────────────────────────────────────────────────────
with st.expander("Q7: Why is my lift coefficient (CL) lower when using a box farfield compared to a circular farfield for the same airfoil and conditions?"):
    st.write("Downwash Constraint: A lifting airfoil generates downwash (downward-deflected flow). In a circular farfield (free air), this downwash extends naturally.")
    st.write("In a box farfield, the top and bottom walls constrain the vertical flow, reducing the effective circulation and thus CL.")
    st.write("Wall Proximity: Even 'slip' walls constrain the streamlines. If the box is too small (e.g., 10x10 chords), the walls are close enough to significantly alter the pressure distribution around the airfoil.")
    st.write("Mesh Quality: Unstructured meshes often have poor-quality cells at the sharp corners of a box, introducing numerical diffusion that can smear the solution.")
    st.write("Recommendation:")
    st.write("For free-air results: Use a circular farfield with radius ≥ 15-20 chords")
    st.write("For wind-tunnel results: Use a box at least 25x15 chords to minimize wall effects")
    st.write("Always verify that your results converge and that the wake has room to develop")

# ─── FAQ 8 ──────────────────────────────────────────────────────────────
with st.expander("Q8: Why do I see a distinct wake ('streaming') behind the airfoil in a box farfield but not in a circular farfield?"):
    st.write("This is physically correct and expected:")
    st.write("Circular farfield (free air): The wake spreads radially in all directions and diffuses as it travels outward. By the time it reaches the farfield boundary, it has dissipated significantly and is barely visible.")
    st.write("Box farfield (wind tunnel): The top and bottom walls constrain the wake, preventing it from spreading vertically. This keeps the wake coherent and visible all the way to the outlet — exactly as you would see in a real wind tunnel.")
    st.write("This is not an error; it's the correct physics of confined vs. unconfined flow!")

# ─── FAQ 9 ──────────────────────────────────────────────────────────────    
with st.expander("Q9: When I visualize pressure in ParaView for a box farfield simulation, I see 'lumpy' or 'vortex-like' patterns in the flow field, even though the airfoil surface pressure looks smooth and correct. What causes this?"):
    st.write("Most Likely Causes:")
    st.write("1. Mesh Quality Issues (Most Common)")
    st.write("Unstructured triangular meshes can produce 'noisy' solutions, especially in regions with:")
    st.write("Poor aspect ratio cells (long, thin triangles)")
    st.write("Skewed cells near the box corners")
    st.write("Sudden changes in cell size")
    st.write("The Fix:")
    st.write("Increase mesh resolution: --mesh_size 0.005 (or smaller")
    st.write("Use structured mesh - gmshairfoil2d supports" )
    st.write("Check mesh quality in ParaView: Filters → Mesh Quality")
    st.write("2. Insufficient Numerical Dissipation")
    st.write("The JST scheme needs enough artificial viscosity to damp numerical oscillations")
    st.write("The Fix: Increase JST coefficients in your config:")
    st.write("ini")
    st.write("1")
    st.write("First value (1.0): More second-order dissipation (damps oscillations)")
    st.write("Second value (0.04): More fourth-order dissipation (smooths solution)")
    st.write("3. Turbulence Model Wake Artifacts")
    st.write("The Spalart-Allmaras model can produce oscillations in the wake region, especially with coarse meshes")
    st.write("The Fix:")
    st.write("Refine the wake mesh region")
    st.write("Or temporarily test with SOLVER= EULER (no turbulence) to see if lumps disappear")
    st.write("4. ParaView Interpolation Artifacts")
    st.write("You might be viewing Cell Data instead of Point Data, or vice versa")
    st.write("The Fix: In ParaView, try:")
    st.write("Right-click on your dataset → 'Cell Data to Point Data' (or reverse)")
    st.write("Increase 'Contour' resolution if using contour plots")
    st.write("Use 'Resample To Image' filter for smoother visualization")
    st.write("Quick Diagnostic Test:")
    st.write("Run the same case with a circular farfield. If the 'lumps' disappear, it confirms:")
    st.write("The box corners have poor mesh quality")
    st.write("The constraint is causing numerical instability")
    st.write("Professional Tip:")
    st.write("For publication-quality visualizations, always:")
    st.write("Use structured O-grid meshes (no triangular noise)")
    st.write("Apply smoothing filters in ParaView (Filters → Smooth)")
    st.write("Visualize Point Data not Cell Data")
    st.write("Use streamlines or contours rather than raw color maps")

# ─── FAQ 10 ────────────────────────────────────────────────────────────── 
with st.expander("Q10: Do 2D CFD simulations predict real aircraft performance?"):
    st.write("A: Yes, but with limitations:")
    st.write("Excellent for: Comparing airfoils, understanding flow physics, educational purposes, preliminary design")
    st.write("Good for: Predicting trends (how CL changes with AoA), small aircraft/UAV performance")
    st.write("Limited for: Absolute performance prediction of large aircraft, stall behavior, 3D effects like induced drag")
    st.write("For real-flight predictions, 2D simulations should be:")
    st.write("Validated against experimental data")
    st.write("Corrected for 3D effects (induced drag, tip losses)")
    st.write("Supplemented with 3D CFD for final design")
    st.write("Your simulations at Re=6M, Mach 0.3 are highly relevant for: Small aircraft, UAVs, model aircraft, wind tunnel models, and educational purposes.")
    st.write("This is why aerospace engineering is both an art and a science — knowing when to trust the numbers is as important as generating them.")

# ─── FAQ 11 ────────────────────────────────────────────────────────────── 
with st.expander("Q11 - What extra can you do using su2 compiled from source"):
   st.write("Compiling SU2 (Stanford University Unstructured) from source code—rather than using pre-compiled binaries. While pre-compiled versions are perfect for standard CFD simulations and design optimization, " )
   st.write("compiling from source is essential for researchers, developers, and HPC administrators who need to push the boundaries of the software.")
   st.write("Here is a breakdown of the 'extra' things you can do when you compile SU2 from source:")
   st.write("1. Modify the Core Physics and Solvers")
   st.write(" Unlike commercial solvers that rely on User-Defined Functions (UDFs) or scripting, SU2 is written in modern C++. Compiling from source allows you to directly alter the core C++ codebase to:")
   st.write("Implement Custom Governing Equations: Add entirely new physics (e.g., multi-phase flows, reacting flows with custom finite-rate chemistry, or magnetohydrodynamics) that are not in the standard release.!")
   st.write("Create Novel Boundary Conditions: Write custom C++ classes for highly specific inlet/outlet/wall conditions tailored to your exact experimental setup.")
   st.write("Develop Custom Turbulence/Transition Models: Implement and test new RANS models, LES subgrid-scale models, or transition models by modifying the solver source code directly.")
   st.write("2. Deep Customization of the Adjoint and Optimization")
   st.write("SU2 is famous for its discrete adjoint solver. Compiling from source allows you to:")
   st.write("Customize Objective Functions: While you can define many functions via the config file, source access allows you to code highly complex, non-standard objective functions or constraints directly into the adjoint driver.")
   st.write("Modify the Adjoint Formulation: If you are researching adjoint methods, you can alter how the discrete adjoint equations are linearized or solved.")
   st.write("Integrate Custom Optimizers: Hook up proprietary or highly specialized optimization algorithms (beyond the standard SLSQP, BFGS, or evolutionary algorithms) directly into the SU2 optimization driver.")
   st.write("3. Hardware-Specific Performance Tuning")
   st.write("Pre-compiled binaries are built to be broadly compatible. Compiling from source allows you to squeeze maximum performance out of your specific hardware:")
   st.write("Architecture-Specific Vectorization: Compile with flags like -march=native or -march=skylake-avx512 to enable advanced SIMD instructions specific to your CPU.")
   st.write("Custom Math Libraries: Link SU2 against highly optimized, site-specific math libraries (e.g., Intel MKL, AMD AOCL, or custom OpenBLAS builds) for faster linear algebra operations.")
   st.write("MPI Tuning: Compile against specific versions or configurations of MPI (OpenMPI, MPICH, Intel MPI) and tune the underlying communication protocols (e.g., UCX, OFI) for your specific supercomputer's interconnect (InfiniBand, Slingshot).")
   st.write("Experimental GPU Backends: If you are working with SU2's emerging GPU acceleration efforts (via frameworks like RAJA, Kokkos, or direct CUDA/HIP implementations), compiling from source is strictly required to enable and test these hardware accelerators.")
   st.write("4. Advanced External Coupling (FSI, CHT, and ML)")
   st.write("If you are using SU2 in a multi-physics environment, source compilation allows you to tightly couple it with external codes:")
   st.write("Custom FSI/CHT Interfaces: Modify the MPI-based coupling interfaces to talk to proprietary structural or thermal solvers.")
   st.write("In-Situ Machine Learning: Embed custom C++ inference engines (like TensorRT, ONNX Runtime, or custom PyTorch C++ APIs) ")
   st.write("directly into the SU2 time-stepping loop to run ML-based surrogate models or turbulence closures 'in-situ' without the overhead of Python wrappers.")
   st.write("5. Debugging, Profiling, and Instrumentation")
   st.write("When a simulation crashes or performs poorly on a massive HPC cluster, pre-compiled binaries are a black box. Source compilation allows you to:")
   st.write("Add Custom Telemetry: Insert custom print statements, file I/O, or memory-tracking metrics exactly where you need them in the solver loop.")
   st.write("Use Advanced Profilers: Compile with debug symbols (-Dbuildtype=debug) and profiling flags to use tools like Intel VTune, TAU, or Valgrind to find memory leaks and MPI bottlenecks.")
   st.write("Step-Through Debugging: Use gdb or lldb to step through the exact C++ execution path of a failing simulation.")
   st.write("6. Access to 'Bleeding-Edge' Features")
   st.write("The develop Branch: By cloning the repository and compiling, you can access the develop branch, which contains the latest features, bug fixes, and C++ standard updates (e.g., C++17/20 migrations) months before they are frozen into an official stable release.")
   st.write("Custom Dependency Versions: You can force SU2 to compile against specific, non-standard versions of dependencies like CGNS, Metis, or the Tecplot Export SDK (TECIO) to match your institution's specific software stack.")
   st.write("7. Modifying the Python API (pysu2)")
   st.write("SU2 features a Python wrapper (pysu2) that allows you to drive the C++ solver from Python. Compiling from source ensures that the C++ backend and the Python API are perfectly synchronized.") 
   st.write("More importantly, it allows you to expose new internal C++ variables, solvers, or mesh manipulation tools to Python by modifying the SWIG interface files and recompiling.")

# ─── FAQ 12 ────────────────────────────────────────────────────────────── 
with st.expander("Q12: What are the steps involved in compiling SU2 from source on Windows 11?"): 
    st.write("Step 1 - Download the SU2 Source files and store in a separate directory")
    st.write("Step 2 - Install the Microsoft C++ Build Tools (6 GB) - not the full Visual Studio IDE - which is massive")
    st.write("Step 3 - Install meson and ninja in a separate Python environment")  
    st.write("Step 4 - In the Python environment run command python meson.py setup build --buildtype=release -Dcgns=false. Note on Windows 11 disabling cgns will save a lot of trouble and mostly cgns is not required") 
    st.write("Step 5 - Providing meson build works a build subdirectory is created and you are ready to start compiling C++.")
    st.write("Step 6 - Click the Windows Start Menu and search for x64 Native Tools Command Prompt -  on my system they are under Visual Studio 2026")
    st.write("Step 7 - A Command prompt window will display - navigate to the SU2 Python environment and enter command ninja -C build" )
    st.write("Step 8 - you are more than likely to hit a number of Warnings - Don't worry about the -march=native warnings! That is a completely harmless warning.")
    st.write("-march=native is an optimization flag used by GCC/Clang compilers (common on Linux/Mac). The Microsoft compiler (cl) doesn't understand it, so it simply throws warning D9002, ignores it, and moves on." )
    st.write("Step 9 - Fix any compiler errors. In particular you may hit compile errors in Common\\src\\CConfig.cpp The Problem: The function addDoubleArrayOption expects a raw memory pointer (su2double *)." )
    st.write("However, the code is passing a std::array iterator. On Linux (GCC), iterators often secretly act like raw pointers, but the Microsoft compiler is strictly enforcing the C++ standard and refusing to convert the iterator to a pointer.")
    st.write("The Fix: We just need to tell the compiler to extract the raw pointer from the array by adding .data() to the end of the variable name.")
    st.write("Step 10 - Re-run the Ninja command, it will automatically pick up from where the command failed")
    st.write("Step 11 - When linking you may get errors LINK : fatal error LNK1104: cannot open file 'libboost_atomic-vc141-mt-x64-1_69.lib. The TecIO library (which is Tecplot's output format library) comes bundled with its own Boost 1.69 sources in boost.tar.gz")
    st.write("Step 12 - The easiest solution is to disable TecIO library which is not required if you use Paraview - So best to remove build directory and in step 6 run python meson.py setup build --buildtype=release -Dcgns=false -Dtecio=false ")
    st.write("Step 13 - Now run ninja -C build and you should find SU2_CFD.exe, SU2_DEF.exe, SU2_SOL.exe, etc. which are ready to use. Also the exe files are much smaller than the pre-compiled versions. ")
    st.write("Also the time to compile and link from start to finish was only 2 to 3 minutes on my Windows 11 system - nowhere like the half hour or more quoted in the literature.")
    st.write("If you have a modern Windows 11 system with plenty of RAM > 32GB you will find the Microsoft compiler very fast" )

    # ─── FAQ 13 ────────────────────────────────────────────────────────────── 
with st.expander("Q13: Does SU2 support GPU acceleration? What should I expect when using CUDA on Windows 11??"):
    st.write("A: Yes! The latest versions of SU2 include robust support for NVIDIA GPUs via the enable_CUDA build option. While it was once considered experimental, it is now a mature feature that can drastically reduce computation times for large-scale simulations.")
    st.write("However, if you are setting this up on Windows 11, here is what you need to know and what to expect:")
    st.write("1. How SU2 Uses the GPU")
    st.write("SU2 does not run the entire simulation on the GPU. Instead, it offloads the most computationally expensive parts—specifically the linear solvers (like FGMRES) and matrix operations ")
    st.write("(using cuBLAS and cuSPARSE) required for viscous (RANS/Navier-Stokes) and adjoint simulations. Inviscid (Euler) runs see less benefit.")
    st.write("2. The 'Mesh Size' Reality Check (Crucial!)")
    st.write("GPUs are designed for massive parallel throughput. Because data must be copied from your system RAM to the GPU's VRAM over the PCIe bus, there is a latency overhead.")
    st.write("For 2D Airfoils / Small Meshes: If your mesh is under ~200,000 cells (like typical 2D NACA or flap simulations), the CPU will actually be faster than the GPU. The overhead of transferring the data to the GPU takes longer than the time saved by computing it.")
    st.write("For 3D / Large Meshes: Once you move to 3D wings, full aircraft, or meshes with 1 million+ cells, the GPU will absolutely shine, often cutting solve times by 50% to 80% compared to a standard CPU.)")
    st.write("The Windows 11 Compilation Path: Use WSL2")
    st.write("While it is technically possible to compile SU2 with CUDA natively on Windows using MSYS2/MinGW and the Windows CUDA Toolkit, it is notoriously difficult due to path conflicts, MPI integration issues, and Meson/Ninja build quirks.")
    st.write("The highly recommended path for Windows 11 is to use WSL2 (Windows Subsystem for Linux). NVIDIA provides excellent support for GPU passthrough to WSL2. By installing Ubuntu on WSL2, you can compile SU2 using the standard Linux instructions,")
    st.write("and it will seamlessly recognize and use a Windows NVIDIA GPU.")

with st.expander("Q14: Can pre-compiled versions of SU2 simulation Shock Waves on Aerofoils?"):
    st.write("Yes — SU2 can simulate shock waves on aerofoils, including high‑Mach and transonic flows, but its accuracy depends on the turbulence model, mesh quality, and numerical settings,") 
    st.write("and pre‑compiled versions may have limitations compared to the latest development builds.")
    st.write("SU2’s capability for shock wave CFD")
    st.write("SU2 is an open‑source CFD suite that supports compressible, high‑Reynolds number flows and can solve the Navier–Stokes equations with various turbulence models.") 
    st.write("It is designed for aerodynamic analysis, including transonic and hypersonic regimes, and has been validated for shock wave–boundary layer interactions and impinging shock cases CERES.") 
    st.write(" This means it can resolve shock waves on aerofoil surfaces if the governing equations, mesh, and models are set up correctly.")
    st.write("Pre‑compiled vs. development builds")
    st.write("A pre‑compiled SU2 (e.g., from the official site or a package manager) can run the same CFD physics as the development version, provided it is built with the same numerical schemes, turbulence models, and solver settings. However:")
    st.write("Older pre‑compiled builds may lack recent bug fixes, improved shock‑capturing schemes, or updated turbulence models.")
    st.write("Feature availability can differ; for example, some newer compressible flow solvers or mesh‑adaptation tools may only be in the latest source builds.")
    st.write("If you need the most accurate shock resolution, it’s best to use the latest SU2 release or a pre‑compiled package that matches the latest code.")
    st.write("Practical considerations for shock wave simulations")
    st.write("To capture shock waves on aerofoils in SU2:")
    st.write("Use a compressible solver (e.g., SU2_CFD with compressible Navier–Stokes equations).")
    st.write("Select an appropriate turbulence model (e.g., Spalart–Allmaras, k‑ω SST) — both have been tested for shock–boundary layer interactions CERES.")
    st.write("Ensure adequate mesh resolution in shock regions and boundary layers; shock‑capturing accuracy depends heavily on cell size and aspect ratio.")
    st.write("Set correct boundary conditions (inlet Mach number, total pressure, wall conditions) and use a suitable time‑marching or steady‑state solver.")
    st.write("Validate against experimental or high‑fidelity CFD data for your Mach number and aerofoil configuration.")
    st.write("Limitations")
    st.write("At very high Mach numbers or strong shock–separation interactions, discrepancies can occur due to turbulence model limitations CERES.")
    st.write("Pre‑compiled versions may not include mesh adaptation or discrete adjoint features needed for advanced studies.")
    st.write("Shock resolution can be sensitive to numerical dissipation and flux schemes — check the SU2 documentation for recommended settings.")
    st.write("In summary: A pre‑compiled SU2 can simulate shock waves on aerofoils if it is built with the correct compressible solver, turbulence model, and mesh resolution.") 
    st.write("For the most accurate results, use the latest SU2 build or a pre‑compiled package that matches it, and validate against experimental data.")