import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import numpy as np

def render_metric_cards(df):
    """Render metric cards with key statistics."""
    # Calculate metrics
    total_products = len(df)
    
    # Calculate average price
    try:
        avg_price = pd.to_numeric(df['Regular price'], errors='coerce').mean()
    except:
        avg_price = 0
    
    # Count published products
    published_count = len(df[df['Status'] == 'Published']) if 'Status' in df.columns else 0
    
    # Count draft products
    draft_count = len(df[df['Status'] == 'Draft']) if 'Status' in df.columns else 0
    
    # Create 3 columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Products",
            value=f"{total_products}",
            delta=None,
            help="Total number of products in the catalog"
        )
    
    with col2:
        st.metric(
            label="Average Price",
            value=f"${avg_price:.2f}",
            delta=None,
            help="Average regular price across all products"
        )
    
    with col3:
        st.metric(
            label="Published Products",
            value=f"{published_count}",
            delta=f"{published_count/total_products*100:.1f}%" if total_products > 0 else "0%",
            help="Number of products with 'Published' status"
        )
    
    with col4:
        st.metric(
            label="Draft Products",
            value=f"{draft_count}",
            delta=f"{draft_count/total_products*100:.1f}%" if total_products > 0 else "0%",
            delta_color="inverse",
            help="Number of products with 'Draft' status"
        )

def render_product_cards(df, num_cards=3):
    """Render product cards in a grid layout."""
    # Filter to only published products
    published_df = df[df['Status'] == 'Published'] if 'Status' in df.columns else df
    
    # If we have products to display
    if len(published_df) > 0:
        st.subheader("Featured Products")
        
        # Select random products to feature (or take all if fewer than num_cards)
        if len(published_df) <= num_cards:
            featured_products = published_df
        else:
            featured_products = published_df.sample(num_cards)
        
        # Create columns for cards
        cols = st.columns(min(num_cards, len(featured_products)))
        
        # Display each product in a card
        for i, (_, product) in enumerate(featured_products.iterrows()):
            with cols[i]:
                with st.container(border=True):
                    # Product name as header
                    st.markdown(f"### {product['Name']}")
                    
                    # Price information
                    regular_price = float(product['Regular price']) if 'Regular price' in product and pd.notna(product['Regular price']) else 0
                    sale_price = float(product['Sale price']) if 'Sale price' in product and pd.notna(product['Sale price']) else 0
                    
                    if sale_price > 0 and sale_price < regular_price:
                        st.markdown(f"<span style='text-decoration: line-through;'>${regular_price:.2f}</span> <span style='color: red; font-weight: bold;'>${sale_price:.2f}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-weight: bold;'>${regular_price:.2f}</span>", unsafe_allow_html=True)
                    
                    # Short description
                    if 'Short description' in product and pd.notna(product['Short description']):
                        st.markdown(f"*{product['Short description']}*")
                    
                    # Categories
                    if 'Categories' in product and pd.notna(product['Categories']):
                        st.markdown(f"**Categories:** {product['Categories']}")
                    
                    # View button
                    st.button("View Details", key=f"view_{i}", use_container_width=True)

def render_sales_trend_chart():
    """Render a mock sales trend chart."""
    # Generate mock data
    dates = pd.date_range(start=datetime.now().replace(day=1), periods=30, freq='D')
    
    # Create some realistic looking sales data with weekend peaks
    base_sales = np.random.randint(5, 15, size=30)
    weekend_boost = np.array([3 if d.weekday() >= 5 else 0 for d in dates])
    trend_boost = np.linspace(0, 5, 30)  # Upward trend
    
    sales = base_sales + weekend_boost + trend_boost
    
    # Create DataFrame
    sales_df = pd.DataFrame({
        'Date': dates,
        'Sales': sales
    })
    
    # Create the chart
    fig = px.line(
        sales_df, 
        x='Date', 
        y='Sales',
        title="Sales Trend (Last 30 Days)",
        labels={'Sales': 'Units Sold', 'Date': ''},
        markers=True
    )
    
    fig.update_layout(
        xaxis=dict(
            tickformat="%b %d",
            tickangle=-45,
            tickmode='auto',
            nticks=10
        ),
        yaxis=dict(
            tickmode='auto',
            nticks=10
        ),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_category_performance_chart(df):
    """Render a category performance chart."""
    if 'Categories' not in df.columns:
        return
    
    # Extract all unique categories
    all_categories = []
    for cats in df['Categories'].dropna():
        categories = [c.strip() for c in str(cats).split(',')]
        all_categories.extend(categories)
    
    # Count occurrences
    category_counts = pd.Series(all_categories).value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    # Generate mock revenue data for each category
    np.random.seed(42)  # For reproducibility
    category_counts['Avg Price'] = np.random.uniform(50, 200, size=len(category_counts))
    category_counts['Revenue'] = category_counts['Count'] * category_counts['Avg Price']
    
    # Sort by revenue
    category_counts = category_counts.sort_values('Revenue', ascending=False)
    
    # Take top 10 categories
    top_categories = category_counts.head(10)
    
    # Create the chart
    fig = go.Figure()
    
    # Add bars for product count
    fig.add_trace(go.Bar(
        x=top_categories['Category'],
        y=top_categories['Count'],
        name='Product Count',
        marker_color='#4C78A8'
    ))
    
    # Add line for revenue
    fig.add_trace(go.Scatter(
        x=top_categories['Category'],
        y=top_categories['Revenue'],
        name='Est. Revenue ($)',
        mode='lines+markers',
        marker=dict(color='#E45756'),
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        title='Top Categories by Product Count and Estimated Revenue',
        xaxis=dict(
            title='Category',
            tickangle=-45
        ),
        yaxis=dict(
            title='Product Count',
            titlefont=dict(color='#4C78A8'),
            tickfont=dict(color='#4C78A8')
        ),
        yaxis2=dict(
            title='Est. Revenue ($)',
            titlefont=dict(color='#E45756'),
            tickfont=dict(color='#E45756'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_price_distribution_chart(df):
    """Render an enhanced price distribution chart."""
    if 'Regular price' not in df.columns:
        return
    
    try:
        # Convert price columns to numeric
        df['Regular price'] = pd.to_numeric(df['Regular price'], errors='coerce')
        
        # Create histogram with density curve
        fig = px.histogram(
            df, 
            x='Regular price',
            nbins=20,
            title="Product Price Distribution",
            labels={'Regular price': 'Price ($)', 'count': 'Number of Products'},
            color_discrete_sequence=['#3366CC'],
            marginal='box'  # Add a box plot on the margin
        )
        
        # Add mean line
        mean_price = df['Regular price'].mean()
        fig.add_vline(x=mean_price, line_dash="dash", line_color="red", 
                     annotation_text=f"Mean: ${mean_price:.2f}", 
                     annotation_position="top right")
        
        # Update layout
        fig.update_layout(
            xaxis_title="Price ($)",
            yaxis_title="Number of Products",
            bargap=0.1
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating price distribution chart: {str(e)}")

def render_status_gauge_chart(df):
    """Render a gauge chart showing product status distribution."""
    if 'Status' not in df.columns:
        return
    
    # Count status values
    status_counts = df['Status'].value_counts()
    
    # Calculate percentage published
    total = status_counts.sum()
    pct_published = status_counts.get('Published', 0) / total * 100 if total > 0 else 0
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_published,
        title={'text': "Published Products (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2E86C1"},
            'steps': [
                {'range': [0, 30], 'color': "#F1948A"},
                {'range': [30, 70], 'color': "#F7DC6F"},
                {'range': [70, 100], 'color': "#82E0AA"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=250)
    
    st.plotly_chart(fig, use_container_width=True)

def render_dashboard_overview(df):
    """Render the dashboard overview with enhanced UI elements."""
    # Title with styling
    st.markdown("""
    <style>
    .dashboard-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .dashboard-subheader {
        font-size: 1.2rem;
        color: #424242;
        margin-bottom: 2rem;
    }
    </style>
    <div class="dashboard-header">E-Commerce Dashboard</div>
    <div class="dashboard-subheader">Product Management & Analytics</div>
    """, unsafe_allow_html=True)
    
    # Render metric cards
    render_metric_cards(df)
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales trend chart
        render_sales_trend_chart()
    
    with col2:
        # Status gauge chart
        render_status_gauge_chart(df)
    
    # Product cards
    render_product_cards(df)
    
    # Category performance chart
    render_category_performance_chart(df)
    
    # Price distribution chart
    render_price_distribution_chart(df)

def render_bulk_operations_ui(df, sheets):
    """Render UI for bulk operations."""
    st.header("Bulk Operations")
    
    # Create tabs for different bulk operations
    bulk_tab1, bulk_tab2, bulk_tab3 = st.tabs(["Bulk Status Update", "Bulk Price Update", "Bulk Export/Import"])
    
    # Tab 1: Bulk Status Update
    with bulk_tab1:
        st.subheader("Update Status for Multiple Products")
        
        # Multi-select for products
        selected_products = st.multiselect(
            "Select Products to Update",
            options=df['Name'].tolist(),
            help="Hold Ctrl/Cmd to select multiple products"
        )
        
        # Status selection
        new_status = st.selectbox("New Status", ["Published", "Draft"])
        
        # Update button
        if st.button("Update Status", use_container_width=True):
            if selected_products and 'spreadsheet' in st.session_state:
                success_count = 0
                for product_name in selected_products:
                    # Find product index
                    product_index = df[df['Name'] == product_name].index[0]
                    
                    # Get product data
                    product_data = df.iloc[product_index].to_dict()
                    
                    # Update status
                    product_data['Status'] = new_status
                    
                    # Update in Google Sheets
                    success, _ = sheets.update_row(
                        st.session_state.spreadsheet,
                        st.session_state.worksheet_index,
                        product_index + 1,  # +1 to account for header row
                        product_data
                    )
                    
                    if success:
                        # Update local dataframe
                        df.at[product_index, 'Status'] = new_status
                        success_count += 1
                
                # Update session state
                st.session_state.current_data = df
                
                # Show success message
                st.success(f"Updated status for {success_count} products")
            else:
                st.error("Please select products and ensure spreadsheet is loaded")
    
    # Tab 2: Bulk Price Update
    with bulk_tab2:
        st.subheader("Update Prices for Multiple Products")
        
        # Category filter
        if 'Categories' in df.columns:
            categories = ['All'] + sorted(set([cat.strip() for cats in df['Categories'].dropna() for cat in str(cats).split(',')]))
            selected_category = st.selectbox("Filter by Category", categories)
            
            if selected_category != 'All':
                filtered_df = df[df['Categories'].str.contains(selected_category, case=False, na=False)]
            else:
                filtered_df = df
        else:
            filtered_df = df
        
        # Price update options
        update_type = st.radio("Update Type", ["Percentage Change", "Fixed Amount Change", "Set to Value"])
        
        if update_type == "Percentage Change":
            percentage = st.number_input("Percentage Change (%)", value=10.0, step=1.0)
            increase = st.radio("Direction", ["Increase", "Decrease"]) == "Increase"
            
            # Preview calculation
            st.caption("Example: $100 price would become " + 
                      f"${100 * (1 + percentage/100) if increase else 100 * (1 - percentage/100):.2f}")
            
        elif update_type == "Fixed Amount Change":
            amount = st.number_input("Amount ($)", value=5.0, step=1.0)
            increase = st.radio("Direction", ["Increase", "Decrease"]) == "Increase"
            
            # Preview calculation
            st.caption("Example: $100 price would become " + 
                      f"${100 + amount if increase else 100 - amount:.2f}")
            
        else:  # Set to Value
            new_price = st.number_input("New Price ($)", value=99.99, step=1.0)
        
        # Which price to update
        price_field = st.radio("Price Field to Update", ["Regular price", "Sale price", "Both"])
        
        # Show products that will be affected
        st.write(f"This will update {len(filtered_df)} products:")
        st.dataframe(
            filtered_df[['Name', 'Regular price', 'Sale price', 'Categories']],
            column_config={
                "Name": st.column_config.TextColumn("Product Name"),
                "Regular price": st.column_config.NumberColumn("Regular Price", format="$%.2f"),
                "Sale price": st.column_config.NumberColumn("Sale Price", format="$%.2f"),
            },
            hide_index=True,
        )
        
        # Update button
        if st.button("Update Prices", use_container_width=True):
            if len(filtered_df) > 0 and 'spreadsheet' in st.session_state:
                success_count = 0
                
                for idx, product in filtered_df.iterrows():
                    # Get product data
                    product_data = product.to_dict()
                    
                    # Update prices based on selected option
                    if price_field in ["Regular price", "Both"] and 'Regular price' in product_data:
                        try:
                            current_price = float(product_data['Regular price'])
                            
                            if update_type == "Percentage Change":
                                new_value = current_price * (1 + percentage/100) if increase else current_price * (1 - percentage/100)
                            elif update_type == "Fixed Amount Change":
                                new_value = current_price + amount if increase else current_price - amount
                            else:  # Set to Value
                                new_value = new_price
                                
                            product_data['Regular price'] = max(0, new_value)  # Ensure price is not negative
                        except:
                            pass
                    
                    if price_field in ["Sale price", "Both"] and 'Sale price' in product_data:
                        try:
                            current_price = float(product_data['Sale price']) if pd.notna(product_data['Sale price']) else 0
                            
                            if update_type == "Percentage Change":
                                new_value = current_price * (1 + percentage/100) if increase else current_price * (1 - percentage/100)
                            elif update_type == "Fixed Amount Change":
                                new_value = current_price + amount if increase else current_price - amount
                            else:  # Set to Value
                                new_value = new_price
                                
                            product_data['Sale price'] = max(0, new_value)  # Ensure price is not negative
                        except:
                            pass
                    
                    # Update in Google Sheets
                    success, _ = sheets.update_row(
                        st.session_state.spreadsheet,
                        st.session_state.worksheet_index,
                        idx + 1,  # +1 to account for header row
                        product_data
                    )
                    
                    if success:
                        # Update local dataframe
                        if price_field in ["Regular price", "Both"] and 'Regular price' in product_data:
                            df.at[idx, 'Regular price'] = product_data['Regular price']
                        
                        if price_field in ["Sale price", "Both"] and 'Sale price' in product_data:
                            df.at[idx, 'Sale price'] = product_data['Sale price']
                            
                        success_count += 1
                
                # Update session state
                st.session_state.current_data = df
                
                # Show success message
                st.success(f"Updated prices for {success_count} products")
            else:
                st.error("No products to update or spreadsheet not loaded")
    
    # Tab 3: Bulk Export/Import
    with bulk_tab3:
        st.subheader("Export/Import Product Data")
        
        # Export section
        st.write("### Export Products")
        export_format = st.radio("Export Format", ["CSV", "Excel", "JSON"])
        
        if st.button("Export All Products", use_container_width=True):
            if 'current_data' in st.session_state and st.session_state.current_data is not None:
                try:
                    # Create download button based on format
                    if export_format == "CSV":
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="products_export.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    elif export_format == "Excel":
                        # For Excel, we need to use a BytesIO object
                        import io
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Products')
                        
                        st.download_button(
                            label="Download Excel",
                            data=buffer.getvalue(),
                            file_name="products_export.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:  # JSON
                        json_data = df.to_json(orient='records')
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name="products_export.json",
                            mime="application/json",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error exporting data: {str(e)}")
            else:
                st.error("No data to export. Please load data first.")
        
        # Import section
        st.write("### Import Products")
        st.warning("⚠️ This feature will add new products to your spreadsheet. Please ensure your data is correctly formatted.")
        
        uploaded_file = st.file_uploader("Upload Product Data", type=["csv", "xlsx", "json"])
        
        if uploaded_file is not None:
            try:
                # Read the file based on its type
                if uploaded_file.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    import_df = pd.read_excel(uploaded_file)
                else:  # JSON
                    import_df = pd.read_json(uploaded_file)
                
                # Show preview of data to be imported
                st.write(f"Preview of data to be imported ({len(import_df)} products):")
                st.dataframe(import_df.head(5))
                
                # Import button
                if st.button("Import Products", use_container_width=True):
                    if 'spreadsheet' in st.session_state:
                        success_count = 0
                        
                        # Process each row
                        for _, row in import_df.iterrows():
                            product_data = row.to_dict()
                            
                            # Remove any record_id as it should be auto-generated
                            if 'record_id' in product_data:
                                del product_data['record_id']
                            
                            # Add to Google Sheets
                            success, _ = sheets.add_row(
                                st.session_state.spreadsheet,
                                st.session_state.worksheet_index,
                                product_data
                            )
                            
                            if success:
                                success_count += 1
                        
                        # Reload data to include the new products
                        if success_count > 0:
                            df_new, msg = sheets.get_worksheet_data(
                                st.session_state.spreadsheet, 
                                st.session_state.worksheet_index
                            )
                            if df_new is not None:
                                st.session_state.current_data = df_new
                                st.success(f"Successfully imported {success_count} products")
                                st.experimental_rerun()
                            else:
                                st.error(f"Error reloading data: {msg}")
                        else:
                            st.error("No products were imported")
                    else:
                        st.error("Spreadsheet not loaded. Please load data first.")
            except Exception as e:
                st.error(f"Error processing import file: {str(e)}")
