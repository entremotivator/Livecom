# E-Commerce Products Dashboard

A Streamlit dashboard for viewing and editing e-commerce products from Google Sheets with OpenAI integration for AI-powered product creation.

## Features

- **Google Sheets Integration**: View and edit product data directly from Google Sheets
- **Product Management**: Add, edit, and delete products with a user-friendly interface
- **Data Visualization**: Analyze product data with interactive charts and graphs
- **AI-Powered Product Creation**: Generate new product ideas and descriptions using OpenAI
- **Description Enhancement**: Improve existing product descriptions with AI assistance

## Requirements

- Python 3.7+
- Streamlit
- Google Sheets API credentials
- OpenAI API key (for AI features)

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Google Sheets API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API
4. Create credentials (Service Account Key)
5. Download the JSON key file
6. Share your Google Sheet with the email address in the service account

### OpenAI API Setup

1. Sign up for an OpenAI account at [https://openai.com](https://openai.com)
2. Generate an API key from your account dashboard
3. Use this key in the dashboard's sidebar

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (usually http://localhost:8501)
3. In the sidebar:
   - **Authenticate** using one of these methods:
     - **Upload your Google Service Account JSON key file** (recommended)
     - Paste your Google Service Account JSON key
     - Use OAuth authentication
   - Enter the URL of your spreadsheet
   - Click "Load Data" to fetch your product information
4. Use the tabs to:
   - View all products
   - Edit existing products or add new ones
   - Analyze product data with charts and visualizations
5. Use the AI Product Creator in the sidebar to:
   - Generate new product ideas
   - Improve existing product descriptions

## Google Sheets Format

The dashboard expects your Google Sheet to have the following columns:

- Name
- Description
- ID
- Short description
- Regular price
- URL Slug
- Categories
- Sale price
- Status
- record_id

## Deployment

This dashboard can be deployed to Streamlit Cloud, Heroku, or any other platform that supports Python applications.

For Streamlit Cloud:
1. Push your code to a GitHub repository
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your repository
4. Set the required environment variables (API keys)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
