import streamlit as st
import pandas as pd
import camelot

# Set page configuration
st.set_page_config(page_title="Inspection Plan Analysis", layout="wide")

# Custom CSS for Tw Cen MT font and professional styling
st.markdown("""
    <style>
    @import url('https://fonts.cdnfonts.com/css/tw-cen-mt');

    html, body, [class*="css"]  {
        font-family: 'Tw Cen MT', sans-serif;
        font-size: 16px;
        color: #333;
    }

    .stApp {
        background-color: #f4f6f8;
    }

    .sidebar .sidebar-content {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }

    h1, h2, h3 {
        color: #2c3e50;
    }

    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        font-family: 'Tw Cen MT', sans-serif;
    }

    .stButton>button:hover {
        background-color: #2980b9;
    }

    table {
        border-collapse: collapse;
        width: 100%;
    }

    th, td {
        border: 1px solid #e0e0e0;
        padding: 8px;
        text-align: left;
    }

    th {
        background-color: #3498db;
        color: white;
        font-family: 'Tw Cen MT', sans-serif;
    }

    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    </style>
""", unsafe_allow_html=True)

# Function to process Excel file
def process_excel(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None

# Function to process PDF file
def process_pdf(file):
    try:
        # Extract tables from PDF using camelot
        tables = camelot.read_pdf(file, pages='all')
        if tables and tables.n > 0:
            # Assume the first table contains the relevant data
            df = tables[0].df
            return df
        else:
            st.error("No tables found in the PDF.")
            return None
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

# Function to analyze data
def analyze_data(df):
    # Ensure required columns exist
    required_columns = ['Insp Plan', 'Completed', 'Backlog', 'Lifex DAL']
    if not all(col in df.columns for col in required_columns):
        st.error("Required columns ('Insp Plan', 'Completed', 'Backlog', 'Lifex DAL') not found in the file.")
        return None

    # Convert columns to sets, handling NaN values
    insp_plan = set(df['Insp Plan'].dropna())
    completed = set(df['Completed'].dropna())
    backlog = set(df['Backlog'].dropna())
    lifex_dal = set(df['Lifex DAL'].dropna())

    # Find items in each column that are also in Lifex DAL
    insp_in_lifex = insp_plan.intersection(lifex_dal)
    completed_in_lifex = completed.intersection(lifex_dal)
    backlog_in_lifex = backlog.intersection(lifex_dal)

    # Create a row-by-row results DataFrame
    rows = []
    for item in insp_in_lifex:
        rows.append({'Category': 'Insp Plan in Lifex DAL', 'Item': item})
    for item in completed_in_lifex:
        rows.append({'Category': 'Completed in Lifex DAL', 'Item': item})
    for item in backlog_in_lifex:
        rows.append({'Category': 'Backlog in Lifex DAL', 'Item': item})
    if not rows:
        rows.append({'Category': 'No Matches', 'Item': 'None'})
    results_df = pd.DataFrame(rows)
    return results_df

# Sidebar for file upload
with st.sidebar:
    st.header("Upload File")
    uploaded_file = st.file_uploader("Choose an Excel or PDF file", type=['xlsx', 'pdf'])

# Main app content
st.title("Inspection Plan vs. Lifex DAL Analysis")
st.write("Upload an Excel or PDF file to compare 'Insp Plan', 'Completed', and 'Backlog' against 'Lifex DAL'.")

if uploaded_file is not None:
    # Determine file type and process accordingly
    file_type = uploaded_file.type
    if file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        df = process_excel(uploaded_file)
    elif file_type == 'application/pdf':
        df = process_pdf(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload an Excel (.xlsx) or PDF (.pdf) file.")
        df = None

    if df is not None:
        st.subheader("Uploaded Data Preview")
        st.dataframe(df.head())

        # Analyze the data
        results_df = analyze_data(df)
        if results_df is not None:
            st.subheader("Analysis Results")
            st.write("Each row below shows an item from 'Insp Plan', 'Completed', or 'Backlog' that is present in 'Lifex DAL':")
            st.dataframe(results_df, use_container_width=True)

            # Optional: Visualize counts
            st.subheader("Visualization")
            count_df = results_df.groupby('Category').size().reset_index(name='Count')
            st.bar_chart(count_df.set_index('Category')['Count'])
else:
    st.info("Please upload a file to begin the analysis.")