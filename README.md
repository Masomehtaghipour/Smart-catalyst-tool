# Smart-catalyst-tool
Data-driven catalyst screening and selection platform for comparing catalytic performance

# Smart-catalyst-tool: CO2-to-Methanol Ratio-Scan Screening

This repository contains a Streamlit web application for **data-driven screening of heterogeneous catalysts** in the CO2-to-methanol reaction.

The app provides an interactive shortlist of promising supported-metal catalysts based on internal ratio-scan experiments at a fixed operating window.

## What the app does
- Loads two curated datasets:
  - `Full catalyst.csv`: full ratio-scan library of candidate catalysts
  - `Top candidates catalyst.csv`: pre-selected top performers
- Harmonizes key performance metrics (e.g. `Max_Yield_AllR`) across datasets
- Optionally computes a **SmartScore** that combines:
  - Methanol selectivity
  - CO2 conversion
- Lets the user filter catalysts by:
  - Base metal
  - Support
  - Yield range
- Ranks candidates within the current filters and displays:
  - A recommended short-list (top N)
  - Filtered top-candidates table
  - Filtered full library

The goal is to support **rapid, explainable shortlist generation** for follow-up lab validation and scale-up studies, not to replace detailed kinetic modelling or process design.

## How to run locally

1. Clone the repository:

```bash
git clone https://github.com/Masomehtaghipour/Smart-catalyst-tool.git
cd Smart-catalyst-tool
```

2. Create and activate a virtual environment (optional but recommended).

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Deployed demo

The app is deployed on **Streamlit Community Cloud**:

> _Add your Streamlit URL here, for example:_  
> `https://smart-catalyst-tool-<username>.streamlit.app`

Anyone with this link can explore the catalyst library and apply filters directly in the browser.

## Data

- **Full catalyst.csv**  
  Internal ratio-scan dataset covering a library of supported-metal catalysts under fixed temperature, pressure and H2/CO2 ratio.

- **Top candidates catalyst.csv**  
  Subset of formulations pre-selected based on internal screening criteria.

Exact column definitions and units are documented in the original experimental dataset. The app assumes the presence of columns such as:

- `Base`, `Support`
- `Max_Yield_AllR` (or `MaxYieldAllR`)
- Optional: `MeOH_Selectivity`, `CO2_Conversion`

## Scope and limitations

- Focused on CO2-to-methanol over heterogeneous, supported catalysts
- Uses a fixed operating window (no full process optimization)
- Does **not** provide:
  - CAPEX/OPEX or full techno-economic analysis
  - Lifetime, poison tolerance or TRL assessment
  - Commercial guarantees

The tool is intended as an **R&D decision-support module** for prioritizing promising catalyst formulations for further testing.

