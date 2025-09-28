import streamlit as st
import pandas as pd
import plotly.express as px
from sheets_integration import GoogleSheetsIntegration
import json

def render_dashboard():
    """Render the main dashboard interface."""
    st.title("E-Commerce Products Dashboard")
    
    # Initialize Google Sheets integration
    sheets = GoogleSheetsIntegration()
    
    # Sidebar for authentication and settings
    with st.sidebar:
        st.header("Settings")
        
        # Authentication section
        st.subheader("Google Sheets Authentication")
        
        if not sheets.is_authenticated():
            auth_method = st.radio("Authentication Method", ["JSON File Upload", "API Key", "OAuth"])
            
            if auth_method == "JSON File Upload":
                uploaded_file = st.file_uploader("Upload Service Account JSON Key", type=["json"])
                if uploaded_file is not None:
                    if st.button("Authenticate with File"):
                        with st.spinner("Authenticating..."):
                            success, message = sheets.authenticate_with_key_file(uploaded_file)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
            elif auth_method == "API Key":
                api_key_json = st.text_area("Enter Service Account JSON Key", height=150)
                if st.button("Authenticate"):
                    if api_key_json:
                        success, message = sheets.authenticate_with_key(api_key_json)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter a valid JSON key")
            else:
                if st.button("Authenticate with Google"):
                    success, message = sheets.authenticate_with_oauth()
                    if success:
                        st.success(message)
                    else:
                        st.warning(message)
        else:
            st.success("✅ Authenticated")
            if st.button("Logout"):
                st.session_state.gsheets_creds = None
                st.session_state.gsheets_client = None
                st.experimental_rerun()
        
        # Spreadsheet URL input
        st.subheader("Spreadsheet Settings")
        spreadsheet_url = st.text_input(
            "Spreadsheet URL", 
            value="https://docs.google.com/spreadsheets/d/12bMMeC3pec16r92nXh2RIuFc-RlbYR_kBMuXgrNHLaE/edit?gid=427440805#gid=427440805"
        )
        
        worksheet_index = st.number_input("Worksheet Index", min_value=0, value=0, step=1)
        
        # Load data button
        if st.button("Load Data"):
            if sheets.is_authenticated():
                with st.spinner("Loading data..."):
                    spreadsheet, message = sheets.get_spreadsheet(spreadsheet_url)
                    if spreadsheet:
                        df, msg = sheets.get_worksheet_data(spreadsheet, worksheet_index)
                        if df is not None:
                            st.session_state.spreadsheet = spreadsheet
                            st.session_state.current_data = df
                            st.session_state.worksheet_index = worksheet_index
                            st.success(f"Data loaded successfully: {len(df)} products")
                        else:
                            st.error(msg)
                    else:
                        st.error(message)
            else:
                st.warning("Please authenticate first")
    
    # Main content area
    if 'current_data' in st.session_state and st.session_state.current_data is not None:
        df = st.session_state.current_data
        
        # Dashboard tabs
        tab1, tab2, tab3 = st.tabs(["Products Overview", "Edit Products", "Analytics"])
        
        # Tab 1: Products Overview
        with tab1:
            st.header("Products Overview")
            
            # Search and filter
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("Search Products", "")
            with col2:
                if 'Categories' in df.columns:
                    categories = ['All'] + sorted(df['Categories'].unique().tolist())
                    selected_category = st.selectbox("Filter by Category", categories)
                else:
                    selected_category = 'All'
            
            # Apply filters
            filtered_df = df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['Name'].str.contains(search_term, case=False) | 
                                         filtered_df['Description'].str.contains(search_term, case=False)]
            
            if selected_category != 'All' and 'Categories' in df.columns:
                filtered_df = filtered_df[filtered_df['Categories'].str.contains(selected_category, case=False)]
            
            # Display products in a table
            st.write(f"Showing {len(filtered_df)} products")
            st.dataframe(
                filtered_df,
                column_config={
                    "Name": st.column_config.TextColumn("Product Name"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "Regular price": st.column_config.NumberColumn("Regular Price", format="$%.2f"),
                    "Sale price": st.column_config.NumberColumn("Sale Price", format="$%.2f"),
                    "Status": st.column_config.SelectboxColumn(
                        "Status", options=["Published", "Draft"]
                    ),
                },
                hide_index=True,
            )
        
        # Tab 2: Edit Products
        with tab2:
            st.header("Edit Products")
            
            # Product selection
            selected_product_index = st.selectbox(
                "Select Product to Edit",
                options=range(len(df)),
                format_func=lambda i: df.iloc[i]['Name'] if i < len(df) else "Select a product"
            )
            
            if selected_product_index is not None:
                product = df.iloc[selected_product_index]
                
                with st.form("edit_product_form"):
                    st.subheader(f"Editing: {product['Name']}")
                    
                    # Create form fields for each column
                    edited_product = {}
                    for col in df.columns:
                        # Skip record_id as it's usually auto-generated
                        if col == 'record_id':
                            edited_product[col] = product[col]
                            continue
                            
                        # Different input types based on column name/type
                        if col == 'Description':
                            edited_product[col] = st.text_area(col, product[col], height=150)
                        elif col == 'Status':
                            edited_product[col] = st.selectbox(col, ["Published", "Draft"], index=0 if product[col] == "Published" else 1)
                        elif col in ['Regular price', 'Sale price']:
                            try:
                                value = float(product[col]) if not pd.isna(product[col]) else 0.0
                            except:
                                value = 0.0
                            edited_product[col] = st.number_input(col, value=value, step=1.0)
                        else:
                            edited_product[col] = st.text_input(col, product[col])
                    
                    # Submit button
                    submitted = st.form_submit_button("Save Changes")
                    
                    if submitted:
                        if 'spreadsheet' in st.session_state:
                            success, message = sheets.update_row(
                                st.session_state.spreadsheet,
                                st.session_state.worksheet_index,
                                selected_product_index + 1,  # +1 to account for header row
                                edited_product
                            )
                            
                            if success:
                                st.success(message)
                                # Update the local dataframe
                                for col in edited_product:
                                    df.at[selected_product_index, col] = edited_product[col]
                                st.session_state.current_data = df
                            else:
                                st.error(message)
                        else:
                            st.error("Spreadsheet not loaded. Please load data first.")
            
            # Add new product section
            st.subheader("Add New Product")
            with st.form("add_product_form"):
                new_product = {}
                for col in df.columns:
                    # Skip record_id as it's usually auto-generated
                    if col == 'record_id':
                        continue
                        
                    # Different input types based on column name/type
                    if col == 'Description':
                        new_product[col] = st.text_area(f"New {col}", "", height=150)
                    elif col == 'Status':
                        new_product[col] = st.selectbox(f"New {col}", ["Published", "Draft"], index=1)  # Default to Draft
                    elif col in ['Regular price', 'Sale price']:
                        new_product[col] = st.number_input(f"New {col}", value=0.0, step=1.0)
                    else:
                        new_product[col] = st.text_input(f"New {col}", "")
                
                # Submit button
                submitted = st.form_submit_button("Add Product")
                
                if submitted:
                    if 'spreadsheet' in st.session_state:
                        success, message = sheets.add_row(
                            st.session_state.spreadsheet,
                            st.session_state.worksheet_index,
                            new_product
                        )
                        
                        if success:
                            st.success(message)
                            # Reload data to include the new product
                            df_new, msg = sheets.get_worksheet_data(st.session_state.spreadsheet, st.session_state.worksheet_index)
                            if df_new is not None:
                                st.session_state.current_data = df_new
                                st.experimental_rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Spreadsheet not loaded. Please load data first.")
        
        # Tab 3: Analytics
        with tab3:
            st.header("Product Analytics")
            
            # Price distribution
            if 'Regular price' in df.columns:
                try:
                    # Convert price columns to numeric
                    df['Regular price'] = pd.to_numeric(df['Regular price'], errors='coerce')
                    
                    st.subheader("Price Distribution")
                    fig = px.histogram(
                        df, 
                        x='Regular price',
                        nbins=20,
                        title="Product Price Distribution",
                        labels={'Regular price': 'Price ($)'},
                        color_discrete_sequence=['#3366CC']
                    )
                    st.plotly_chart(fig)
                except Exception as e:
                    st.error(f"Error creating price distribution chart: {str(e)}")
            
            # Category distribution
            if 'Categories' in df.columns:
                st.subheader("Category Distribution")
                
                # Extract all unique categories (they might be comma-separated)
                all_categories = []
                for cats in df['Categories'].dropna():
                    categories = [c.strip() for c in str(cats).split(',')]
                    all_categories.extend(categories)
                
                # Count occurrences
                category_counts = pd.Series(all_categories).value_counts().reset_index()
                category_counts.columns = ['Category', 'Count']
                
                # Create pie chart
                fig = px.pie(
                    category_counts, 
                    values='Count', 
                    names='Category',
                    title="Products by Category"
                )
                st.plotly_chart(fig)
            
            # Status distribution
            if 'Status' in df.columns:
                st.subheader("Product Status")
                status_counts = df['Status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                fig = px.bar(
                    status_counts,
                    x='Status',
                    y='Count',
                    color='Status',
                    title="Products by Status"
                )
                st.plotly_chart(fig)
    else:
        # Display instructions when no data is loaded
        st.info("👈 Please authenticate and load data from the sidebar to get started.")
        
        st.markdown("""
        ### How to use this dashboard:
        
        1. **Authenticate** with Google Sheets using one of these methods:
           - Upload your Google Service Account JSON key file
           - Paste your Google Service Account JSON key
           - Use OAuth authentication
        2. Enter your **Spreadsheet URL** in the sidebar
        3. Click **Load Data** to fetch your product information
        4. Use the tabs to:
           - View all products
           - Edit existing products or add new ones
           - Analyze product data with charts and visualizations
        5. Use the AI Product Creator in the sidebar to generate new product ideas
        """)
        
        # Show instructions for getting a service account key
        with st.expander("How to get a Google Service Account JSON Key"):
            st.markdown("""
            1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select an existing one
            3. Navigate to "APIs & Services" > "Credentials"
            4. Click "Create Credentials" and select "Service Account"
            5. Fill in the service account details and click "Create"
            6. Click on the newly created service account
            7. Go to the "Keys" tab and click "Add Key" > "Create new key"
            8. Select JSON as the key type and click "Create"
            9. The JSON key file will be downloaded to your computer
            10. Share your Google Sheet with the email address in the service account (found in the JSON file)
            """)

if __name__ == "__main__":
    render_dashboard()
