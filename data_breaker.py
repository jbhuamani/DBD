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
        st.dataframe(display_df, use_container_width=True)

        # Split All Cells in a Column
        st.write("Split All Cells in a Column Automatically")
        col_name_split_all = st.selectbox("Select a column to split all multi-line cells:", df.columns.tolist(), key="split_all")

        if col_name_split_all:
            if st.button("Split All Cells in Column"):
                # Prepare a list for new rows
                new_rows = []

                # Iterate over all rows
                for _, row in df.iterrows():
                    cell_content = str(row[col_name_split_all])  # Ensure cell content is a string
                    if "\n" in cell_content:  # Check for multiple lines
                        # Split the cell content and create a new row for each line
                        lines = cell_content.split("\n")
                        for line in lines:
                            new_row = row.copy()
                            new_row[col_name_split_all] = line
                            new_rows.append(new_row)
                    else:
                        # Keep rows with single-line cells unchanged
                        new_rows.append(row)

                # Create updated DataFrame
                st.session_state.df = pd.DataFrame(new_rows)

                # Display updated DataFrame
                st.write("Updated Data (After Splitting All Multi-Line Cells):")
                st.dataframe(st.session_state.df, use_container_width=True)

                # Download Updated File
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    st.session_state.df.to_excel(writer, index=False)
                buffer.seek(0)
                st.download_button(
                    label="Download Updated File (Split All Cells)",
                    data=buffer,
                    file_name="updated_data_split_all.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        # Advanced Splitting Option
        st.write("Advanced Splitting Option")
        col_name_advanced = st.selectbox("Select a column to split based on a string:", df.columns.tolist(), key="advanced_split")
        search_string = st.text_input("Enter the string to search for in the selected column:")
        num_splits = st.number_input("Specify the number of rows to split the cell into:", min_value=2, step=1, value=3)

        # Collect values for each section of the split
        split_values = []
        for i in range(num_splits):
            value = st.text_input(f"Enter value for split section {i + 1}:", key=f"split_value_{i}")
            split_values.append(value)

        if col_name_advanced and search_string and len(split_values) == num_splits:
            if st.button("Split Column by String"):
                # Prepare a list for new rows
                new_rows = []

                # Iterate over all rows
                for _, row in df.iterrows():
                    cell_content = str(row[col_name_advanced])  # Ensure cell content is a string
                    if search_string in cell_content:  # Check for the search string
                        # Split the cell into specified sections
                        for split_value in split_values:
                            new_row = row.copy()
                            new_row[col_name_advanced] = split_value
                            new_rows.append(new_row)
                    else:
                        # Keep rows without the search string unchanged
                        new_rows.append(row)

                # Create updated DataFrame
                st.session_state.df = pd.DataFrame(new_rows)

                # Display updated DataFrame
                st.write("Updated Data (After Advanced Splitting):")
                st.dataframe(st.session_state.df, use_container_width=True)

                # Download Updated File
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    st.session_state.df.to_excel(writer, index=False)
                buffer.seek(0)
                st.download_button(
                    label="Download Updated File (Advanced Splitting)",
                    data=buffer,
                    file_name="updated_data_advanced_split.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

if __name__ == "__main__":
    main()
