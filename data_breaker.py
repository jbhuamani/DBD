import streamlit as st
import pandas as pd
import requests
from io import BytesIO

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
    if "selected_cell" not in st.session_state:
        st.session_state.selected_cell = None

    # Step 1: File Upload Section
    if st.button("Load Data from Google Drive"):
        try:
            st.session_state.df = fetch_csv_from_drive()
            st.success("Data loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load: {e}")

    # Step 2: Display Data
    if st.session_state.df is not None:
        st.write("Loaded Data:")
        edited_df = st.data_editor(st.session_state.df, key="data_editor", use_container_width=True)
        st.session_state.df = edited_df  # Update DataFrame after editing

        # Step 3: Split Cell
        if st.button("Split Cell"):
            # Check if a single cell is selected
            selected_data = st.session_state.get("data_editor")
            if not selected_data or "selected_cell" not in selected_data:
                st.warning("Please select a cell to split.")
            else:
                # Retrieve selected cell's row and column
                selected_row = selected_data["selected_cell"]["row"]
                selected_col = selected_data["selected_cell"]["col"]
                selected_content = st.session_state.df.iloc[selected_row, selected_col]

                # Ensure the selected cell content is a string
                selected_content = str(selected_content)
                breakdown_lines = selected_content.split("\n")

                # Create new rows based on breakdown
                new_rows = []
                for line in breakdown_lines:
                    new_row = st.session_state.df.iloc[selected_row].copy()
                    new_row[selected_col] = line
                    new_rows.append(new_row)

                # Drop the original row and add new rows
                st.session_state.df = pd.concat(
                    [st.session_state.df.drop(index=selected_row), pd.DataFrame(new_rows)],
                    ignore_index=True,
                )

                # Display updated DataFrame
                st.success("Cell split successfully! Updated data:")
                st.dataframe(st.session_state.df, use_container_width=True)

if __name__ == "__main__":
    main()
