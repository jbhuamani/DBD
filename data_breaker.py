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

    # Step 2: Display Data
    if st.session_state.df is not None:
        df = st.session_state.df

        # Add 1-based indexing for display purposes
        display_df = df.copy()
        display_df.index = display_df.index + 1  # Shift the index to start from 1

        st.write("Loaded Data (Row numbers start from 1):")
        # Use st.dataframe to display the data interactively
        st.dataframe(display_df, use_container_width=True)

        # Step 3: Select Column for Splitting
        st.write("Select a column to split all cells with multiple lines:")
        col_name = st.selectbox("Select column:", df.columns.tolist())

        if col_name:
            # Display selected column's content
            st.write(f"Selected Column: **{col_name}**")
            
            # Step 4: Split Entire Column Logic
            if st.button("Split Column"):
                # Prepare a list for new rows
                new_rows = []

                # Iterate over all rows
                for _, row in df.iterrows():
                    cell_content = str(row[col_name])  # Ensure cell content is a string
                    if "\n" in cell_content:  # Check for multiple lines
                        # Split the cell content and create a new row for each line
                        lines = cell_content.split("\n")
                        for line in lines:
                            new_row = row.copy()
                            new_row[col_name] = line
                            new_rows.append(new_row)
                    else:
                        # Keep rows with single-line cells unchanged
                        new_rows.append(row)

                # Create updated DataFrame
                st.session_state.df = pd.DataFrame(new_rows)

                # Display updated DataFrame
                st.write("Updated Data:")
                st.dataframe(st.session_state.df, use_container_width=True)

                # Step 5: Download Updated File
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    st.session_state.df.to_excel(writer, index=False)
                buffer.seek(0)
                st.download_button(
                    label="Download Updated File",
                    data=buffer,
                    file_name="updated_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

if __name__ == "__main__":
    main()
