import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
import base64
import streamlit.components.v1 as components

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
  .stFormSubmitButton > button,
  .stApp .stFormSubmitButton > button,
  .stApp [data-testid="stForm"] .stFormSubmitButton > button,
  .stApp [data-testid="stFormSubmitButton"] > button {
    background-color: #1B2A4A !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    min-height: 3.2rem !important;
    padding: 0.75rem 2.5rem !important;
    text-align: center !important;
    line-height: 1.4 !important;
    white-space: nowrap !important;
    box-sizing: border-box !important;
  }
  /* Inner elements: white text, centered */
  .stFormSubmitButton > button *,
  .stApp .stFormSubmitButton > button *,
  .stApp [data-testid="stForm"] .stFormSubmitButton > button * {
    color: #FFFFFF !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  .stDownloadButton > button *,
  .stApp .stDownloadButton > button * {
    color: #FFFFFF !important;
  }
  .stDownloadButton > button:hover,
  .stFormSubmitButton > button:hover {
    background-color: #2D4A7A !important;
  }
  /* Force submit button container full width */
  .stFormSubmitButton,
  .stApp .stFormSubmitButton,
  .stApp [data-testid="stFormSubmitButton"] {
    width: 100% !important;
    clear: both !important;
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

  /* ── Force light color-scheme globally ── */
  .stApp { color-scheme: light !important; }

  /* ── Dark text for Streamlit form/content areas only ── */
  .stApp [data-testid="stFormSubmitButton"] label,
  .stApp [data-testid="stForm"] label,
  .stApp [data-testid="stForm"] p,
  .stApp [data-testid="stForm"] span,
  .stApp .stTextInput label,
  .stApp .stSelectbox label,
  .stApp .stMultiSelect label,
  .stApp .stDateInput label,
  .stApp [data-testid="stWidgetLabel"] {
    color: #1E293B !important;
  }
  /* Subheadings (Step titles like "Upload Shopify...") */
  .stApp [data-testid="stSubheader"],
  .stApp h2, .stApp h3 {
    color: #1E293B !important;
  }
  /* Help-text / descriptions under form fields */
  .stApp [data-testid="stTooltipContent"],
  .stApp [data-testid="InputInstructions"],
  .stApp [data-testid="stWidgetLabel"] small,
  .stApp [data-testid="stWidgetLabel"] .caption {
    color: #64748B !important;
  }
  /* Field label + description pairs */
  .field-label {
    color: #1E293B !important;
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
    line-height: 1.2;
  }
  .field-desc, .stApp .field-desc, .stApp p.field-desc,
  .stApp [data-testid="stForm"] .field-desc,
  .stApp [data-testid="stMarkdownContainer"] .field-desc {
    color: #64748B !important;
    font-size: 0.73rem !important;
    margin: 0 0 0.25rem 0 !important;
    padding: 0 !important;
    line-height: 1.15 !important;
  }
  /* Remove extra spacing Streamlit adds between markdown blocks */
  .stApp [data-testid="stForm"] [data-testid="stMarkdownContainer"] {
    margin-bottom: -0.7rem;
  }
  /* Placeholder text */
  .stApp input::placeholder, .stApp textarea::placeholder {
    color: #94A3B8 !important;
  }
  /* Input fields */
  .stApp input, .stApp select, .stApp textarea,
  .stApp [data-baseweb="input"] input,
  .stApp [data-baseweb="select"] div {
    color: #1E293B !important;
    background-color: #FFFFFF !important;
    caret-color: #1E293B !important;
  }
  /* File uploader – only the label + file-name text, NOT the drop zone */
  .stApp [data-testid="stFileUploader"] label,
  .stApp [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"],
  .stApp [data-testid="stFileUploaderFileName"] {
    color: #1E293B !important;
  }
  /* File uploader drop zone – keep light text on dark bg */
  .stApp [data-testid="stFileUploaderDropzone"],
  .stApp [data-testid="stFileUploaderDropzone"] span,
  .stApp [data-testid="stFileUploaderDropzone"] small,
  .stApp [data-testid="stFileUploaderDropzone"] button {
    color: #FFFFFF !important;
  }
  /* Success / error alert text */
  .stApp [data-testid="stAlert"] p,
  .stApp [data-testid="stAlert"] span {
    color: #1E293B !important;
  }
  /* Info box text */
  .info-box, .info-box * { color: #1E293B !important; }

  /* ── Preserve white text on dark-background custom elements ── */
  .hlc-header, .hlc-header * { color: inherit; }
  .hlc-header h1 { color: #FFFFFF !important; }
  .hlc-header p  { color: #CBD5E1 !important; }
  .step-badge    { color: #FFFFFF !important; }

  /* ── Download link styled as button (works in Notion iframes) ── */
  .dl-link {
    display: inline-block;
    width: 100%;
    text-align: center;
    background-color: #1B2A4A;
    color: #FFFFFF !important;
    padding: 0.65rem 2rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95rem;
    text-decoration: none !important;
    margin-top: 0.5rem;
    transition: background-color 0.2s;
  }
  .dl-link:hover {
    background-color: #2D4A7A;
    color: #FFFFFF !important;
  }

  /* ── Footer ── */
  .hlc-footer {
    text-align: center; color: #94A3B8 !important;
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
    <p>For Your First PO: Convert Shopify inventory exports into Packiyo Purchase Order format</p>
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
            st.markdown('<p class="field-label">Purchase Order Name</p><p class="field-desc">The Name of This Purchase Order</p>', unsafe_allow_html=True)
            po_name = st.text_input(
                "Purchase Order Name",
                placeholder="e.g. ABC_PO_0001",
                label_visibility="collapsed",
            )

            st.markdown('<p class="field-label">Warehouse</p><p class="field-desc">HLC Location This PO is Headed To</p>', unsafe_allow_html=True)
            warehouse = st.selectbox(
                "Warehouse",
                WAREHOUSE_OPTIONS,
                label_visibility="collapsed",
            )

            st.markdown('<p class="field-label">Customer</p><p class="field-desc">Your Brand Name — Must Match Brand Name in Packiyo</p>', unsafe_allow_html=True)
            customer = st.text_input(
                "Customer",
                placeholder="e.g. ABC Brand",
                label_visibility="collapsed",
            )

            st.markdown('<p class="field-label">Location to Pull From</p><p class="field-desc">What Shopify Inventory Locations To Pull Inventory From</p>', unsafe_allow_html=True)
            locations_selected = st.multiselect(
                "Location to Pull From",
                valid_locations,
                label_visibility="collapsed",
            )

        with col2:
            st.markdown('<p class="field-label">Expected Arrival</p><p class="field-desc">Date PO is Expected to Arrive at Warehouse</p>', unsafe_allow_html=True)
            expected_date = st.date_input(
                "Expected Arrival",
                label_visibility="collapsed",
            )

            st.markdown('<p class="field-label">PO Tracking Number</p><p class="field-desc">Tracking Number for PO Shipment</p>', unsafe_allow_html=True)
            tracking_number = st.text_input(
                "PO Tracking Number",
                placeholder="e.g. 1000001112",
                label_visibility="collapsed",
            )

            st.markdown('<p class="field-label">PO Tracking URL</p><p class="field-desc">Link to Tracking for PO Delivery</p>', unsafe_allow_html=True)
            tracking_url = st.text_input(
                "PO Tracking URL",
                placeholder="e.g. https://track.example.com/...",
                label_visibility="collapsed",
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

            # CSV download via JS Blob (works inside Notion iframes)
            csv_str = output_df.to_csv(index=False)
            b64 = base64.b64encode(csv_str.encode()).decode()
            filename = f"{po_name.strip()}_packiyo_po.csv"

            download_html = f"""
            <html><body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
            <button id="dlBtn" style="
              display:flex; width:100%; padding:0.55rem 2rem;
              background-color:#1B2A4A; color:#FFFFFF;
              border:none; border-radius:8px; cursor:pointer;
              font-weight:600; font-size:0.95rem;
              font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
              align-items:center; justify-content:center;
              transition: background-color 0.2s;
              box-sizing:border-box;
            " onmouseover="this.style.backgroundColor='#2D4A7A'"
              onmouseout="this.style.backgroundColor='#1B2A4A'">
              Download PO CSV
            </button>
            <p style="color:#64748B;font-size:0.78rem;line-height:1.45;margin:0.8rem 0 0 0;padding:0;">
              Please review the contents of the spreadsheet to ensure they are accurate.
              Once confirming it is accurate, you can import this CSV into Packiyo via
              <strong>Inbound &rarr; Purchase Orders</strong> then clicking the
              <strong>Import CSV</strong> icon in the top right corner (below the
              "Create PO" button, the icon on the left).
            </p>
            <script>
            var b64Data = '{b64}';
            var fname = '{filename}';
            document.getElementById('dlBtn').addEventListener('click', function() {{
              var w = window.open('', '_blank');
              if (w) {{
                w.document.write(
                  '<html><head><title>Downloading ' + fname + '...</title></head>'
                  + '<body style="font-family:sans-serif;display:flex;align-items:center;'
                  + 'justify-content:center;height:100vh;margin:0;color:#64748B;">'
                  + '<p>Your download should start automatically...</p>'
                  + '<scr' + 'ipt>'
                  + 'var raw = atob("' + b64Data + '");'
                  + 'var blob = new Blob([raw], {{type:"text/csv;charset=utf-8;"}});'
                  + 'var url = URL.createObjectURL(blob);'
                  + 'var a = document.createElement("a");'
                  + 'a.href = url; a.download = "' + fname + '";'
                  + 'document.body.appendChild(a); a.click();'
                  + 'URL.revokeObjectURL(url);'
                  + 'setTimeout(function(){{ window.close(); }}, 2000);'
                  + '</scr' + 'ipt></body></html>'
                );
                w.document.close();
              }}
            }});
            </script>
            </body></html>
            """
            components.html(download_html, height=120)

# ── Footer ──
st.markdown(
    '<div class="hlc-footer">Highline Commerce &middot; Shopify → Packiyo PO Converter</div>',
    unsafe_allow_html=True,
)
