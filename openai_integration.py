import openai
import streamlit as st
import os
import json

class OpenAIIntegration:
    def __init__(self):
        """Initialize OpenAI integration."""
        # Check if API key exists in session state
        if 'openai_api_key' not in st.session_state:
            # Try to get from environment variable
            api_key = os.environ.get('OPENAI_API_KEY', '')
            st.session_state.openai_api_key = api_key
            
            if api_key:
                openai.api_key = api_key
    
    def set_api_key(self, api_key):
        """Set the OpenAI API key."""
        try:
            st.session_state.openai_api_key = api_key
            openai.api_key = api_key
            return True, "API key set successfully"
        except Exception as e:
            return False, f"Error setting API key: {str(e)}"
    
    def is_configured(self):
        """Check if OpenAI API is configured."""
        return bool(st.session_state.openai_api_key)
    
    def generate_product(self, product_type, target_audience, price_range, features=None):
        """Generate a new product using OpenAI."""
        if not self.is_configured():
            return None, "OpenAI API key not configured"
        
        try:
            # Prepare the prompt
            prompt = f"""
            Create a detailed e-commerce product based on the following specifications:
            
            Product Type: {product_type}
            Target Audience: {target_audience}
            Price Range: {price_range}
            
            Additional Features/Requirements: {features if features else 'None specified'}
            
            Please provide the following details in JSON format:
            1. Name: A catchy product name
            2. Description: A detailed product description (2-3 paragraphs)
            3. Short description: A brief one-line description
            4. Regular price: A specific price within the given range
            5. URL Slug: SEO-friendly URL (lowercase, hyphens instead of spaces)
            6. Categories: Appropriate product categories (comma-separated)
            7. Status: "Draft"
            
            Format the response as valid JSON with these exact field names.
            """
            
            # Call OpenAI API
            client = openai.OpenAI(api_key=st.session_state.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a product creation assistant that generates detailed e-commerce product listings. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract and parse the JSON response
            result = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure it's valid JSON
            # Remove any markdown code block indicators
            result = result.replace("```json", "").replace("```", "").strip()
            
            product_data = json.loads(result)
            
            return product_data, "Product generated successfully"
        except Exception as e:
            return None, f"Error generating product: {str(e)}"
    
    def improve_product_description(self, product_name, current_description):
        """Improve an existing product description."""
        if not self.is_configured():
            return None, "OpenAI API key not configured"
        
        try:
            # Prepare the prompt
            prompt = f"""
            Improve the following product description for "{product_name}":
            
            Current Description:
            {current_description}
            
            Please provide an enhanced, more compelling product description that:
            1. Highlights key benefits and features
            2. Uses persuasive language
            3. Maintains the same general information
            4. Is SEO-friendly
            5. Is approximately the same length
            
            Return only the improved description text.
            """
            
            # Call OpenAI API
            client = openai.OpenAI(api_key=st.session_state.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a copywriting expert that improves product descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the improved description
            improved_description = response.choices[0].message.content.strip()
            
            return improved_description, "Description improved successfully"
        except Exception as e:
            return None, f"Error improving description: {str(e)}"
