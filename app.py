import streamlit as st
import pandas as pd

# -------------------------
# Load data
# -------------------------
# Files are in the repo root with these exact names
DF_TOP_PATH = "Top candidates catalyst.csv"
DF_ALL_PATH = "Full catalyst.csv"

df_top = pd.read_csv(DF_TOP_PATH)
df_all = pd.read_csv(DF_ALL_PATH)

# Try to harmonize column names between files
# (so we can use Max_Yield_AllR consistently)
if "Max_Yield_AllR" in df_all.columns:
    yield_col = "Max_Yield_AllR"
elif "MaxYieldAllR" in df_all.columns:
    yield_col = "MaxYieldAllR"
else:
    yield_col = None

# -------------------------
# Optional multi-criteria SmartScore (if additional columns exist)
# -------------------------
score_cols = []
if "MeOH_Selectivity" in df_all.columns:
    score_cols.append("MeOH_Selectivity")
if "CO2_Conversion" in df_all.columns:
    score_cols.append("CO2_Conversion")

if score_cols:
    # Normalize 0–1 for each metric using the full library
    for col in score_cols:
        col_min = df_all[col].min()
        col_max = df_all[col].max()
        span = col_max - col_min if col_max > col_min else 1.0
        df_all[f"{col}_norm"] = (df_all[col] - col_min) / span
        df_top[f"{col}_norm"] = (df_top[col] - col_min) / span

    # Business-oriented weighting: prioritize MeOH selectivity
    weights = {}
    if "MeOH_Selectivity_norm" in df_all.columns:
        weights["MeOH_Selectivity_norm"] = 0.6
    if "CO2_Conversion_norm" in df_all.columns:
        weights["CO2_Conversion_norm"] = 0.4

    def compute_score(df):
        score = 0.0
        for col, w in weights.items():
            if col in df.columns:
                score += w * df[col]
        return score

    df_all["SmartScore"] = compute_score(df_all)
    df_top["SmartScore"] = compute_score(df_top)
    rank_col = "SmartScore"
else:
    rank_col = yield_col

# -------------------------
# Header / Hero section
# -------------------------
st.title("SmartCat-RS: CO2-to-Methanol Catalyst Screening Platform")

st.subheader("Ratio-scan screening for supported metal catalysts")

st.markdown(
    """
This module screens supported metal catalysts for **CO2-to-methanol**,  
using ratio-scan experiments at a fixed operating window, to produce a ranked short-list.
"""
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total catalysts", len(df_all))
with col2:
    st.metric("Top candidates", len(df_top))

# Simple filter-activity indicator
n_filters = 0
# (count filters that are not "show all"; updated after filters are defined)
with col3:
    st.caption("Dataset: internal CO2-to-methanol ratio-scan results")

st.divider()

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("Filters")

# Unique lists for filters
all_bases = sorted(df_all["Base"].unique()) if "Base" in df_all.columns else []
supports = sorted(df_all["Support"].unique()) if "Support" in df_all.columns else []

# Chemically primary / promoter metals for CO2 -> MeOH
primary_bases = ["Cu", "Zn", "Zr", "Ce", "Ga", "In", "Pd"]
primary_bases = [m for m in primary_bases if m in all_bases]

# Fallback if empty
default_bases = primary_bases if len(primary_bases) > 0 else all_bases

selected_bases = st.sidebar.multiselect(
    "Base metal (primary & promoters)",
    all_bases,
    default=default_bases,
)

selected_supports = st.sidebar.multiselect("Support", supports, default=supports)

# Yield filter
if yield_col:
    min_yield = float(df_all[yield_col].min())
    max_yield = float(df_all[yield_col].max())
    selected_yield_range = st.sidebar.slider(
        f"{yield_col} range",
        min_value=min_yield,
        max_value=max_yield,
        value=(min_yield, max_yield),
    )
else:
    selected_yield_range = None

only_top = st.sidebar.checkbox("Only top candidates", value=False)

# Count active filters (for business users)
n_filters = 0
if selected_bases and len(selected_bases) < len(all_bases):
    n_filters += 1
if selected_supports and len(selected_supports) < len(supports):
    n_filters += 1
if yield_col and selected_yield_range is not None:
    if (selected_yield_range[0] > min_yield) or (selected_yield_range[1] < max_yield):
        n_filters += 1

# Update third metric with number of active filters
with col3:
    st.metric("Active filters", n_filters)

# -------------------------
# Apply filters
# -------------------------
def apply_filters(df):
    filtered = df.copy()
    if "Base" in filtered.columns:
        filtered = filtered[filtered["Base"].isin(selected_bases)]
    if "Support" in filtered.columns:
        filtered = filtered[filtered["Support"].isin(selected_supports)]
    if yield_col and selected_yield_range is not None:
        filtered = filtered[
            (filtered[yield_col] >= selected_yield_range[0]) &
            (filtered[yield_col] <= selected_yield_range[1])
        ]
    return filtered

df_all_f = apply_filters(df_all)
df_top_f = apply_filters(df_top)

# -------------------------
# Tabs
# -------------------------
tab_rec, tab_top, tab_all, tab_about = st.tabs(
    ["Recommended short-list", "Top candidates", "Full library", "Scope & caveats"]
)

# -------------------------
# Tab 1: Recommendations
# -------------------------
with tab_rec:
    st.subheader("Recommended short-list")

    metric_for_ranking = rank_col or yield_col

    if metric_for_ranking:
        st.markdown(
            f"Ranking based on **{metric_for_ranking}** within the current filters "
            "to support rapid short-listing for follow-up testing "
            "(higher value → higher rank)."
        )

        if only_top:
            df_rank = df_top_f
        else:
            df_rank = df_all_f

        if len(df_rank) == 0:
            st.warning("No catalyst matches the current filters.")
            st.caption("Try relaxing Base/Support or yield range filters.")
        else:
            df_rank = df_rank.sort_values(by=metric_for_ranking, ascending=False)
            top_n = df_rank.head(5)
            st.write("Top 5 within current filters:")
            st.dataframe(top_n)
    else:
        st.info("Showing filtered candidates (no explicit ranking column found).")
        if only_top:
            st.dataframe(df_top_f)
        else:
            st.dataframe(df_all_f.head(20))

# -------------------------
# Tab 2: Top candidates
# -------------------------
with tab_top:
    st.subheader(f"Top candidates (filtered: {len(df_top_f)})")
    if len(df_top_f) == 0:
        st.warning("No top candidate matches the current filters.")
    else:
        st.dataframe(df_top_f)

# -------------------------
# Tab 3: All candidates
# -------------------------
with tab_all:
    st.subheader(f"Full library (filtered: {len(df_all_f)})")
    if len(df_all_f) == 0:
        st.warning("No catalyst matches the current filters.")
    else:
        st.dataframe(df_all_f)

# -------------------------
# Tab 4: About
# -------------------------
with tab_about:
    st.subheader("Scope, assumptions and intended use")
    st.markdown(
        """
**Scope**

- CO2-to-methanol over heterogeneous, supported metal catalysts  
- Internal ratio-scan dataset at fixed temperature, pressure and H2/CO2  

**What this module does**

- Provides a ranked short-list of promising catalyst formulations  
- Helps prioritize candidates for lab validation and scale-up studies  

**What this module does *not* do**

- Full process design, cost estimation or commercial guarantees  
- Explicit assessment of lifetime, poison tolerance or TRL
"""
    )
