import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import json
import os

class GoogleSheetsIntegration:
    def __init__(self):
        """Initialize Google Sheets integration with OAuth or API key."""
        # Check if credentials exist in session state
        if 'gsheets_creds' not in st.session_state:
            st.session_state.gsheets_creds = None
            st.session_state.gsheets_client = None
            
    def authenticate_with_key(self, api_key_json):
        """Authenticate using a service account key JSON."""
        try:
            # Parse the JSON key
            creds_dict = json.loads(api_key_json)
            
            # Define the scope
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # Authenticate
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            
            # Store in session state
            st.session_state.gsheets_creds = creds
            st.session_state.gsheets_client = client
            
            return True, "Authentication successful"
        except Exception as e:
            return False, f"Authentication failed: {str(e)}"
    
    def authenticate_with_oauth(self):
        """
        Placeholder for OAuth authentication.
        In a production app, implement proper OAuth flow.
        """
        st.warning("OAuth authentication not implemented in this demo. Please use API key authentication.")
        return False, "OAuth authentication not implemented"
    
    def is_authenticated(self):
        """Check if already authenticated."""
        return st.session_state.gsheets_client is not None
    
    def get_spreadsheet(self, spreadsheet_url):
        """Get a spreadsheet by URL."""
        try:
            if not self.is_authenticated():
                return None, "Not authenticated"
            
            # Extract spreadsheet ID from URL
            if "spreadsheets/d/" in spreadsheet_url:
                parts = spreadsheet_url.split("spreadsheets/d/")[1]
                spreadsheet_id = parts.split("/")[0]
            else:
                spreadsheet_id = spreadsheet_url
                
            # Open the spreadsheet
            spreadsheet = st.session_state.gsheets_client.open_by_key(spreadsheet_id)
            return spreadsheet, "Success"
        except Exception as e:
            return None, f"Error accessing spreadsheet: {str(e)}"
    
    def get_worksheet_data(self, spreadsheet, worksheet_index=0):
        """Get data from a specific worksheet."""
        try:
            # Get the worksheet
            worksheet = spreadsheet.get_worksheet(worksheet_index)
            
            # Get all values including headers
            data = worksheet.get_all_values()
            
            if not data:
                return None, "Worksheet is empty"
            
            # Convert to DataFrame
            headers = data[0]
            rows = data[1:]
            df = pd.DataFrame(rows, columns=headers)
            
            return df, "Success"
        except Exception as e:
            return None, f"Error getting worksheet data: {str(e)}"
    
    def update_row(self, spreadsheet, worksheet_index, row_index, data_dict):
        """Update a specific row in the worksheet."""
        try:
            # Get the worksheet
            worksheet = spreadsheet.get_worksheet(worksheet_index)
            
            # Get headers to ensure correct column mapping
            headers = worksheet.row_values(1)
            
            # Prepare row data in the correct order
            row_data = []
            for header in headers:
                if header in data_dict:
                    row_data.append(data_dict[header])
                else:
                    # Get existing value if not provided in update
                    existing_value = worksheet.cell(row_index + 1, headers.index(header) + 1).value
                    row_data.append(existing_value)
            
            # Update the row (row_index + 1 because row_index is 0-based but API is 1-based)
            worksheet.update_row(row_index + 1, row_data)
            
            return True, "Row updated successfully"
        except Exception as e:
            return False, f"Error updating row: {str(e)}"
    
    def add_row(self, spreadsheet, worksheet_index, data_dict):
        """Add a new row to the worksheet."""
        try:
            # Get the worksheet
            worksheet = spreadsheet.get_worksheet(worksheet_index)
            
            # Get headers to ensure correct column mapping
            headers = worksheet.row_values(1)
            
            # Prepare row data in the correct order
            row_data = []
            for header in headers:
                if header in data_dict:
                    row_data.append(data_dict[header])
                else:
                    row_data.append("")  # Empty value for missing fields
            
            # Append the row
            worksheet.append_row(row_data)
            
            return True, "Row added successfully"
        except Exception as e:
            return False, f"Error adding row: {str(e)}"
    
    def delete_row(self, spreadsheet, worksheet_index, row_index):
        """Delete a specific row from the worksheet."""
        try:
            # Get the worksheet
            worksheet = spreadsheet.get_worksheet(worksheet_index)
            
            # Delete the row (row_index + 1 because row_index is 0-based but API is 1-based)
            worksheet.delete_row(row_index + 1)
            
            return True, "Row deleted successfully"
        except Exception as e:
            return False, f"Error deleting row: {str(e)}"
