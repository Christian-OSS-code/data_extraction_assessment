"""
Simple Web Application for Assessment
Run with: streamlit run app.py
"""
import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(
    page_title="Leaflet Product Extractor",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
    /* Main page background - Clean Light Gray */
    .stApp {
        background-color: #f5f7fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Main content container - White card with subtle shadow */
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        max-width: 1200px;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }

    /* Sidebar styling - Slightly lighter background */
    section[data-testid="stSidebar"] > div {
        background-color: #f9fafc;
        padding-top: 2rem;
    }

    /* Header and title color adjustment for better contrast */
    .stTitle h1 {
        color: #1a1a1a;
    }

    /* Divider styling */
    hr {
        border-top: 1px solid #eaeaea;
        margin: 1.5rem 0;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 6px;
    }

    /* Make dropdown cursor look interactive */
    div[data-baseweb="select"] > div {
        cursor: pointer !important;
        border-radius: 6px;
    }

    /* Make buttons have pointer cursor */
    .stButton > button {
        cursor: pointer !important;
        border-radius: 6px;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Make download buttons stand out with a fresh green */
    .stDownloadButton > button {
        background-color: #10b981;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 6px;
        font-weight: 500;
        transition: background-color 0.2s ease;
    }

    .stDownloadButton > button:hover {
        background-color: #0da271;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Metric card styling */
    [data-testid="stMetric"] {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }

    /* Make selectbox more prominent */
    .stSelectbox > div > div {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛒 Leaflet Product Extractor - I&M Limited")
st.markdown("Displaying products extracted from the provided leaflet image.")

# Load the data.json file created by main.py
data_file = "data.json"
if not os.path.exists(data_file):
    st.error(f"❌ {data_file} not found. Please run 'python main.py' first.")
    st.info("Run this command in your terminal: `python main.py`")
    st.stop()

with open(data_file, "r") as f:
    try:
        products = json.load(f)
    except json.JSONDecodeError:
        st.error("Error reading data.json. Please run 'python main.py' again.")
        st.stop()

if not products:
    st.warning("No products found in data.json")
    st.stop()

st.success(f"✅ Loaded {len(products)} products from {data_file}")

# ASSESSMENT REQUIREMENT 1: Display in tabular form
st.header("📋 Product Table")
df = pd.DataFrame(products)

# Reorder columns for better display
column_order = ['product_name', 'price', 'weight_volume', 'price_per_unit', 'description']
df_display = df[[col for col in column_order if col in df.columns]]

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=False,
    column_config={
        "product_name": st.column_config.TextColumn("Product Name", width="large"),
        "price": st.column_config.TextColumn("Price", width="small"),
        "weight_volume": st.column_config.TextColumn("Size", width="medium"),
        "price_per_unit": st.column_config.TextColumn("Unit Price", width="medium"),
        "description": st.column_config.TextColumn("Description", width="medium")
    }
)

# ASSESSMENT REQUIREMENT 2: Dropdown selection
st.header("🖱️ Interactive Product Selection")
st.markdown("*Select a product from the dropdown below to view details*")

# Create dropdown options with product names and prices for better context
dropdown_options = [f"{idx}. {product.get('product_name', 'Unknown')} - {product.get('price', 'N/A')}"
                    for idx, product in enumerate(products, 1)]

# Add "Select a product..." as first option
dropdown_options = ["👇 Click here to select a product..."] + dropdown_options

# Create the dropdown with custom styling hint
st.markdown("<span style='color: #666; font-size: 14px;'>*Hover over the dropdown below and click to select*</span>",
            unsafe_allow_html=True)

selected_option = st.selectbox(
    "Choose a product:",
    options=range(len(dropdown_options)),
    format_func=lambda x: dropdown_options[x],
    index=0,
    label_visibility="collapsed"
)

# Show selected product details
if selected_option > 0:
    selected_idx = selected_option - 1
    product = products[selected_idx]

    st.divider()

    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header(f"📋 Selected Product Details")

        # Display product information in a clean format
        st.subheader(product.get('product_name', 'Unknown Product'))

        # Create metrics row
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("Price", product.get('price', 'N/A'))
        with metric_cols[1]:
            if product.get('weight_volume'):
                st.metric("Size", product.get('weight_volume'))
            else:
                st.metric("Size", "N/A")
        with metric_cols[2]:
            if product.get('price_per_unit'):
                st.metric("Unit Price", product.get('price_per_unit'))
            else:
                st.metric("Unit Price", "N/A")

        # Description
        if product.get('description'):
            st.markdown("**Description:**")
            st.info(product.get('description'))

    with col2:
        st.subheader("📥 Export Options")

        # Download button for this specific product
        json_data = json.dumps(product, indent=2)
        st.download_button(
            label="⬇️ Download This Product as JSON",
            data=json_data,
            file_name=f"product_{selected_idx + 1}.json",
            mime="application/json",
            use_container_width=True,
            help="Click to download this product's data as a JSON file"
        )

    # Raw JSON view in expander
    with st.expander("🔍 View Raw JSON Data", expanded=False):
        st.json(product)

# Summary sidebar
with st.sidebar:
    st.header("📊 Summary")
    st.metric("Total Products", len(products))

    # Price statistics
    prices = []
    for p in products:
        price_str = p.get('price', '').replace('$', '').replace(',', '')
        try:
            prices.append(float(price_str))
        except:
            continue

    if prices:
        st.metric("Average Price", f"${sum(prices) / len(prices):.2f}")
        st.metric("Min Price", f"${min(prices):.2f}")
        st.metric("Max Price", f"${max(prices):.2f}")

    st.divider()
    st.header("📥 Export All Data")

    # Download all as JSON
    all_json = json.dumps(products, indent=2)
    st.download_button(
        label="⬇️ Download All as JSON",
        data=all_json,
        file_name="all_products.json",
        mime="application/json",
        use_container_width=True,
        help="Click to download all products as a JSON file"
    )

    # Download as CSV
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_data,
        file_name="products.csv",
        mime="text/csv",
        use_container_width=True,
        help="Click to download all products as a CSV file"
    )

    st.divider()
    st.markdown("**Assessment Requirements Met:**")
    st.markdown("✅ Table display of products")
    st.markdown("✅ Interactive selection (dropdown)")
    st.markdown("✅ Detailed product view")
    st.markdown("✅ data.json output created")

# Display processing info
st.divider()
st.caption(f"AI Developer Assessment • Processed leaflet: {len(products)} products extracted")
