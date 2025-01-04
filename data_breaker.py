import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Set the layout to "wide" to expand the program to fit the browser window
st.set_page_config(layout="wide")

def fetch_csv_from_drive():
    """Fetch the CSV file from Google Drive using the secret link."""
    csv_url = st.secrets["google_drive"]["csv_link"]
    response = requests.get(csv_url)
    response.raise_for_status()
    return pd.read_csv(BytesIO(response.content))

def main():
    st.title("Data Breaker Program (DBD)")

    # Initialize session state for storing data
    if "df" not in st.session_state:
        st.session_state.df = None

    # Step 1: File Upload Section
    upload_option = st.selectbox("Choose upload method", ["Google Drive (Secret)", "Manual Upload"])
    
    if upload_option == "Google Drive (Secret)":
        if st.button("Load from Google Drive"):
            try:
                st.session_state.df = fetch_csv_from_drive()
                st.success("Data loaded successfully!")
            except Exception as e:
                st.error(f"Failed to load: {e}")
    
    elif upload_option == "Manual Upload":
        uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "csv"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".xlsx"):
                    st.session_state.df = pd.read_excel(uploaded_file)
                else:
                    st.session_state.df = pd.read_csv(uploaded_file)
                st.success("File uploaded successfully!")
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # Step 2: Display Data with Filtering
    if st.session_state.df is not None:
        df = st.session_state.df

        # Add 1-based indexing for display purposes
        display_df = df.copy()
        display_df.index = display_df.index + 1  # Shift the index to start from 1

        st.write("Loaded Data (Row numbers start from 1):")
        
        # Create filter options for each column
        filtered_df = display_df.copy()
        for col in display_df.columns:
            unique_values = display_df[col].dropna().unique().tolist()
            unique_values.sort()  # Sort values for better usability
            selected_value = st.selectbox(
                f"Filter by {col}:",
                options=["All"] + unique_values,
                key=f"filter_{col}"
            )
            if selected_value != "All":
                filtered_df = filtered_df[filtered_df[col] == selected_value]

        # Display the filtered DataFrame
        st.dataframe(filtered_df, use_container_width=True)

        # Option to reset the filters
        if st.button("Reset Filters"):
            st.experimental_rerun()

        # Step 3: Download Filtered Data
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            filtered_df.to_excel(writer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Download Filtered File",
            data=buffer,
            file_name="filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
