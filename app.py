import streamlit as st
import pandas as pd
from dashboard import render_dashboard
from openai_integration import OpenAIIntegration
import os

# Set page configuration
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Improve button styling */
    .stButton > button {
        border-radius: 4px;
        font-weight: 500;
    }
    
    /* Improve form styling */
    .stForm {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    
    /* Improve metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    /* Improve header styling */
    h1, h2, h3 {
        margin-bottom: 1rem;
    }
    
    /* Improve tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        padding: 0 16px;
        font-weight: 500;
    }
    
    /* Improve sidebar styling */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_data' not in st.session_state:
    st.session_state.current_data = None

if 'spreadsheet' not in st.session_state:
    st.session_state.spreadsheet = None

if 'worksheet_index' not in st.session_state:
    st.session_state.worksheet_index = 0

# Initialize OpenAI integration
openai_integration = OpenAIIntegration()

# Sidebar for OpenAI integration
with st.sidebar:
    st.header("AI Product Creator")
    
    # OpenAI API key input
    if not openai_integration.is_configured():
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            success, message = openai_integration.set_api_key(api_key)
            if success:
                st.success("API key configured successfully")
            else:
                st.error(message)
    else:
        st.success("✅ OpenAI API configured")
        if st.button("Clear API Key"):
            success, _ = openai_integration.set_api_key("")
            st.experimental_rerun()
    
    # AI Product Generator
    st.subheader("Generate New Product")
    
    if openai_integration.is_configured():
        with st.form("product_generator_form"):
            product_type = st.text_input("Product Type", "AI Software Tool")
            target_audience = st.text_input("Target Audience", "Small Business Owners")
            
            price_min = st.number_input("Min Price ($)", value=49.0, step=10.0)
            price_max = st.number_input("Max Price ($)", value=199.0, step=10.0)
            price_range = f"${price_min} - ${price_max}"
            
            features = st.text_area("Additional Features/Requirements", "")
            
            generate_button = st.form_submit_button("Generate Product")
            
            if generate_button:
                with st.spinner("Generating product..."):
                    product_data, message = openai_integration.generate_product(
                        product_type, target_audience, price_range, features
                    )
                    
                    if product_data:
                        st.session_state.generated_product = product_data
                        st.success("Product generated successfully!")
                    else:
                        st.error(message)
        
        # Display generated product
        if 'generated_product' in st.session_state:
            st.subheader("Generated Product")
            
            with st.container(border=True):
                product = st.session_state.generated_product
                st.markdown(f"### {product.get('Name', 'N/A')}")
                st.markdown(f"**Price:** ${product.get('Regular price', 'N/A')}")
                st.markdown(f"**Categories:** {product.get('Categories', 'N/A')}")
                st.markdown(f"**Short Description:** {product.get('Short description', 'N/A')}")
                
                with st.expander("Full Description"):
                    st.write(product.get('Description', 'N/A'))
                
                # Add to Google Sheets button
                if st.button("Add to Google Sheets", use_container_width=True):
                    if 'spreadsheet' in st.session_state and st.session_state.spreadsheet is not None:
                        from sheets_integration import GoogleSheetsIntegration
                        sheets = GoogleSheetsIntegration()
                        
                        success, message = sheets.add_row(
                            st.session_state.spreadsheet,
                            st.session_state.worksheet_index,
                            product
                        )
                        
                        if success:
                            st.success(message)
                            # Reload data to include the new product
                            df_new, msg = sheets.get_worksheet_data(
                                st.session_state.spreadsheet, 
                                st.session_state.worksheet_index
                            )
                            if df_new is not None:
                                st.session_state.current_data = df_new
                                st.experimental_rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please load a spreadsheet first")
        
        # Batch Product Generation
        st.subheader("Batch Product Generation")
        
        with st.form("batch_generator_form"):
            product_types = st.text_area("Product Types (one per line)", "AI Email Marketing Tool\nAI Customer Support Bot\nAI Data Analytics Platform")
            common_audience = st.text_input("Common Target Audience", "Digital Marketers")
            common_price_range = st.text_input("Common Price Range", "$99 - $299")
            common_features = st.text_area("Common Features/Requirements", "Cloud-based, API integration, User-friendly interface")
            
            num_products = len(product_types.strip().split('\n')) if product_types.strip() else 0
            
            generate_batch_button = st.form_submit_button(f"Generate {num_products} Products")
            
            if generate_batch_button and num_products > 0:
                product_type_list = product_types.strip().split('\n')
                
                with st.spinner(f"Generating {num_products} products..."):
                    batch_products = []
                    
                    for product_type in product_type_list:
                        product_data, message = openai_integration.generate_product(
                            product_type, common_audience, common_price_range, common_features
                        )
                        
                        if product_data:
                            batch_products.append(product_data)
                    
                    if batch_products:
                        st.session_state.batch_products = batch_products
                        st.success(f"Successfully generated {len(batch_products)} products!")
                    else:
                        st.error("Failed to generate products")
        
        # Display batch generated products
        if 'batch_products' in st.session_state and st.session_state.batch_products:
            st.subheader("Batch Generated Products")
            
            for i, product in enumerate(st.session_state.batch_products):
                with st.expander(f"{i+1}. {product.get('Name', 'Product')}"):
                    st.markdown(f"**Price:** ${product.get('Regular price', 'N/A')}")
                    st.markdown(f"**Categories:** {product.get('Categories', 'N/A')}")
                    st.markdown(f"**Short Description:** {product.get('Short description', 'N/A')}")
                    st.markdown(f"**Full Description:** {product.get('Description', 'N/A')}")
            
            # Add all to Google Sheets button
            if st.button("Add All to Google Sheets", use_container_width=True):
                if 'spreadsheet' in st.session_state and st.session_state.spreadsheet is not None:
                    from sheets_integration import GoogleSheetsIntegration
                    sheets = GoogleSheetsIntegration()
                    
                    success_count = 0
                    for product in st.session_state.batch_products:
                        success, _ = sheets.add_row(
                            st.session_state.spreadsheet,
                            st.session_state.worksheet_index,
                            product
                        )
                        
                        if success:
                            success_count += 1
                    
                    if success_count > 0:
                        st.success(f"Added {success_count} products to Google Sheets")
                        # Reload data to include the new products
                        df_new, msg = sheets.get_worksheet_data(
                            st.session_state.spreadsheet, 
                            st.session_state.worksheet_index
                        )
                        if df_new is not None:
                            st.session_state.current_data = df_new
                            st.experimental_rerun()
                    else:
                        st.error("Failed to add products")
                else:
                    st.error("Please load a spreadsheet first")
        
        # Description improver
        st.subheader("Improve Product Description")
        
        with st.form("description_improver_form"):
            if 'current_data' in st.session_state and st.session_state.current_data is not None:
                df = st.session_state.current_data
                product_names = df['Name'].tolist()
                selected_product = st.selectbox("Select Product", product_names)
                
                if selected_product:
                    product_index = product_names.index(selected_product)
                    current_description = df.iloc[product_index]['Description']
                    
                    st.text_area("Current Description", current_description, height=150, disabled=True)
                    
                    improve_button = st.form_submit_button("Improve Description")
                    
                    if improve_button:
                        with st.spinner("Improving description..."):
                            improved_description, message = openai_integration.improve_product_description(
                                selected_product, current_description
                            )
                            
                            if improved_description:
                                st.session_state.improved_description = improved_description
                                st.session_state.improved_product_index = product_index
                                st.success("Description improved successfully!")
                            else:
                                st.error(message)
            else:
                st.warning("Please load product data first")
                st.form_submit_button("Improve Description", disabled=True)
        
        # Display improved description
        if 'improved_description' in st.session_state:
            st.subheader("Improved Description")
            
            with st.container(border=True):
                st.write(st.session_state.improved_description)
                
                # Update in Google Sheets button
                if st.button("Update in Google Sheets", use_container_width=True):
                    if 'spreadsheet' in st.session_state and st.session_state.spreadsheet is not None:
                        from sheets_integration import GoogleSheetsIntegration
                        sheets = GoogleSheetsIntegration()
                        
                        # Get the current product data
                        df = st.session_state.current_data
                        product_index = st.session_state.improved_product_index
                        product_data = df.iloc[product_index].to_dict()
                        
                        # Update the description
                        product_data['Description'] = st.session_state.improved_description
                        
                        success, message = sheets.update_row(
                            st.session_state.spreadsheet,
                            st.session_state.worksheet_index,
                            product_index + 1,  # +1 to account for header row
                            product_data
                        )
                        
                        if success:
                            st.success(message)
                            # Update the local dataframe
                            df.at[product_index, 'Description'] = st.session_state.improved_description
                            st.session_state.current_data = df
                        else:
                            st.error(message)
                    else:
                        st.error("Please load a spreadsheet first")
    else:
        st.warning("Please configure OpenAI API key to use AI features")

# Render the main dashboard
render_dashboard()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("E-Commerce Dashboard with AI Integration")
st.sidebar.caption("© 2025 All Rights Reserved")
