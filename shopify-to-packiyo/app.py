import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# ──────────────────────────────────────────────
#  Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Shopify → Packiyo PO Converter | Highline Commerce",
    page_icon="📦",
    layout="centered",
)

# ──────────────────────────────────────────────
#  Brand Styling (Highline Commerce)
# ──────────────────────────────────────────────
st.markdown(
    """
<style>
  /* ── Global ── */
  .stApp { background-color: #F8FAFC; }

  /* ── Header Banner ── */
  .hlc-header {
    background: linear-gradient(135deg, #1B2A4A 0%, #2D4A7A 100%);
    padding: 2.2rem 1.5rem 1.8rem;
    border-radius: 14px;
    margin-bottom: 1.6rem;
    text-align: center;
  }
  .hlc-header h1 {
    color: #FFFFFF; font-size: 1.75rem; font-weight: 700; margin: 0;
  }
  .hlc-header p {
    color: #CBD5E1; font-size: 0.92rem; margin-top: 0.4rem;
  }

  /* ── Step Badges ── */
  .step-badge {
    background-color: #1B2A4A; color: #fff;
    padding: 4px 14px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600;
    display: inline-block; margin-bottom: 0.3rem;
  }

  /* ── Buttons ── */
  .stDownloadButton > button,
  .stFormSubmitButton > button {
    background-color: #1B2A4A !important;
    color: #fff !important;
    border: none !important;
    padding: 0.55rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
  }
  .stDownloadButton > button:hover,
  .stFormSubmitButton > button:hover {
    background-color: #2D4A7A !important;
  }

  /* ── Info / Summary Box ── */
  .info-box {
    background-color: #EFF6FF;
    border-left: 4px solid #3B82F6;
    padding: 0.9rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.8rem 0 1.2rem;
    font-size: 0.92rem;
  }

  /* ── Footer ── */
  .hlc-footer {
    text-align: center; color: #94A3B8;
    font-size: 0.78rem; margin-top: 3rem;
    padding-top: 1rem; border-top: 1px solid #E2E8F0;
  }
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────
EXPECTED_HEADERS = [
    "Handle", "Title", "Option1 Name", "Option1 Value",
    "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value",
    "SKU", "HS Code", "COO", "Location", "Bin name",
    "Incoming (not editable)", "Unavailable (not editable)",
    "Committed (not editable)", "Available (not editable)",
    "On hand (current)", "On hand (new)",
]

WAREHOUSE_OPTIONS = ["Atlanta Warehouse", "Ohio Warehouse", "NYC Warehouse"]


# ──────────────────────────────────────────────
#  Helper Functions
# ──────────────────────────────────────────────
def get_valid_locations(df: pd.DataFrame) -> list[str]:
    """Return Location values that have >= 1 numeric On hand (current) row."""
    locations: list[str] = []
    for loc in df["Location"].unique():
        subset = df.loc[df["Location"] == loc, "On hand (current)"]
        if pd.to_numeric(subset, errors="coerce").notna().any():
            locations.append(loc)
    return sorted(locations)


def transform(
    df: pd.DataFrame,
    po_name: str,
    warehouse: str,
    customer: str,
    locations: list[str],
    expected_date: date,
    tracking_number: str,
    tracking_url: str,
) -> pd.DataFrame:
    """Convert Shopify inventory rows → Packiyo PO rows."""

    # 1. Keep only rows at the selected locations
    mask = df["Location"].isin(locations)
    filtered = df.loc[mask].copy()

    # 2. Convert "On hand (current)" to numeric; "not stocked" → NaN → 0
    filtered["_qty"] = (
        pd.to_numeric(filtered["On hand (current)"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    # 3. Preserve the order of first SKU appearance
    sku_order = filtered["SKU"].drop_duplicates().tolist()

    # 4. Sum quantity per SKU across selected locations
    agg = filtered.groupby("SKU", sort=False)["_qty"].sum().reset_index()
    agg["SKU"] = pd.Categorical(agg["SKU"], categories=sku_order, ordered=True)
    agg = agg.sort_values("SKU").reset_index(drop=True)

    n = len(agg)
    date_str = expected_date.strftime("%m/%d/%Y") + " 12:00:00"

    return pd.DataFrame(
        {
            "purchase_order_number": [po_name] * n,
            "status": ["Pending"] * n,
            "warehouse": [warehouse] * n,
            "customer": [customer] * n,
            "supplier": [""] * n,
            "sku": agg["SKU"].tolist(),
            "quantity": agg["_qty"].tolist(),
            "quantity_sell_ahead": [""] * n,
            "ordered_at": [""] * n,
            "expected_at": [date_str] * n,
            "tracking_number": [tracking_number] * n,
            "tracking_url": [tracking_url] * n,
        }
    )


# ══════════════════════════════════════════════
#  UI
# ══════════════════════════════════════════════

# ── Header ──
st.markdown(
    """
<div class="hlc-header">
    <h1>Shopify → Packiyo PO Converter</h1>
    <p>Convert Shopify inventory exports into Packiyo Purchase Order format</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Step 1 – Upload ──
st.markdown('<span class="step-badge">STEP 1</span>', unsafe_allow_html=True)
st.subheader("Upload Shopify Inventory CSV")

uploaded_file = st.file_uploader(
    "Drag and drop or browse for your Shopify inventory export",
    type=["csv"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
    # Read CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"Could not read the file: {exc}")
        st.stop()

    # ── Header validation ──
    actual = list(df.columns)
    missing = [h for h in EXPECTED_HEADERS if h not in actual]
    extra = [h for h in actual if h not in EXPECTED_HEADERS]

    if missing or extra:
        st.error("CSV headers do not match the expected Shopify inventory format.")
        if missing:
            st.markdown(f"**Missing columns:** {', '.join(missing)}")
        if extra:
            st.markdown(f"**Unexpected columns:** {', '.join(extra)}")
        st.stop()

    st.success(f"Headers validated — {len(df):,} rows loaded")

    # ── Valid locations ──
    valid_locations = get_valid_locations(df)
    if not valid_locations:
        st.error("No locations with numeric inventory values were found in this file.")
        st.stop()

    # ── Step 2 – PO Details ──
    st.divider()
    st.markdown('<span class="step-badge">STEP 2</span>', unsafe_allow_html=True)
    st.subheader("Purchase Order Details")

    with st.form("po_form"):
        col1, col2 = st.columns(2)

        with col1:
            po_name = st.text_input(
                "Purchase Order Name",
                placeholder="e.g. ABC_PO_0001",
                help="The Name of This Purchase Order",
            )
            warehouse = st.selectbox(
                "Warehouse",
                WAREHOUSE_OPTIONS,
                help="HLC Location This PO is Headed To",
            )
            customer = st.text_input(
                "Customer",
                placeholder="e.g. ABC Brand",
                help="Your Brand Name — Must Match Brand Name in Packiyo",
            )
            locations_selected = st.multiselect(
                "Location to Pull From",
                valid_locations,
                help="What Shopify Inventory Locations To Pull Inventory From",
            )

        with col2:
            expected_date = st.date_input(
                "Expected Arrival",
                help="Date PO is Expected to Arrive at Warehouse",
            )
            tracking_number = st.text_input(
                "PO Tracking Number",
                placeholder="e.g. 1000001112",
                help="Tracking Number for PO Shipment",
            )
            tracking_url = st.text_input(
                "PO Tracking URL",
                placeholder="e.g. https://track.example.com/...",
                help="Link to Tracking for PO Delivery",
            )

        submitted = st.form_submit_button("Generate Purchase Order CSV")

    # ── Process ──
    if submitted:
        errors = []
        if not po_name.strip():
            errors.append("Purchase Order Name is required.")
        if not customer.strip():
            errors.append("Customer is required.")
        if not locations_selected:
            errors.append("Select at least one Location to Pull From.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            output_df = transform(
                df,
                po_name.strip(),
                warehouse,
                customer.strip(),
                locations_selected,
                expected_date,
                tracking_number.strip(),
                tracking_url.strip(),
            )

            # ── Step 3 – Preview & Download ──
            st.divider()
            st.markdown(
                '<span class="step-badge">STEP 3</span>', unsafe_allow_html=True
            )
            st.subheader("Preview & Download")

            total_units = int(output_df["quantity"].sum())
            st.markdown(
                f'<div class="info-box">'
                f"<strong>{len(output_df)}</strong> unique SKUs &nbsp;·&nbsp; "
                f"<strong>{total_units:,}</strong> total units &nbsp;·&nbsp; "
                f"Warehouse: <strong>{warehouse}</strong>"
                f"</div>",
                unsafe_allow_html=True,
            )

            st.dataframe(output_df, use_container_width=True, hide_index=True)

            # CSV download
            buf = io.StringIO()
            output_df.to_csv(buf, index=False)

            st.download_button(
                label="Download PO CSV",
                data=buf.getvalue(),
                file_name=f"{po_name.strip()}_packiyo_po.csv",
                mime="text/csv",
            )

# ── Footer ──
st.markdown(
    '<div class="hlc-footer">Highline Commerce &middot; Shopify → Packiyo PO Converter</div>',
    unsafe_allow_html=True,
)
