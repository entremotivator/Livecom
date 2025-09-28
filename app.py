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
            
            product = st.session_state.generated_product
            st.write(f"**Name:** {product.get('Name', 'N/A')}")
            st.write(f"**Short Description:** {product.get('Short description', 'N/A')}")
            st.write(f"**Price:** ${product.get('Regular price', 'N/A')}")
            st.write(f"**Categories:** {product.get('Categories', 'N/A')}")
            
            with st.expander("Full Description"):
                st.write(product.get('Description', 'N/A'))
            
            # Add to Google Sheets button
            if st.button("Add to Google Sheets"):
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
            st.write(st.session_state.improved_description)
            
            # Update in Google Sheets button
            if st.button("Update in Google Sheets"):
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
