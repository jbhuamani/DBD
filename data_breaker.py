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
    if "selected_row" not in st.session_state:
        st.session_state.selected_row = None
    if "selected_col" not in st.session_state:
        st.session_state.selected_col = None

    # Step 1: Load Data from Google Drive
    if st.button("Load Data from Google Drive"):
        try:
            st.session_state.df = fetch_csv_from_drive()
            st.success("Data loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load data: {e}")

    # Step 2: Display Data
    if st.session_state.df is not None:
        st.write("Loaded Data:")
        st.write("Click on a cell and then click 'Split Cell' to update the data.")

        # Display the DataFrame as a table
        for i, row in st.session_state.df.iterrows():
            with st.container():
                cols = st.columns(len(row))
                for j, value in enumerate(row):
                    if st.button(str(value), key=f"cell_{i}_{j}"):
                        st.session_state.selected_row = i
                        st.session_state.selected_col = j
                        st.success(f"Selected Cell: Row {i + 1}, Column {row.index[j]}")

        # Step 3: Split Cell Logic
        if st.button("Split Cell"):
            if st.session_state.selected_row is None or st.session_state.selected_col is None:
                st.warning("Please select a cell before splitting.")
            else:
                # Get selected cell details
                row_idx = st.session_state.selected_row
                col_idx = st.session_state.selected_col
                col_name = st.session_state.df.columns[col_idx]
                selected_content = st.session_state.df.iloc[row_idx, col_idx]

                # Ensure the content is treated as a string
                selected_content = str(selected_content)
                breakdown_lines = selected_content.split("\n")

                # Create new rows based on breakdown
                new_rows = []
                for line in breakdown_lines:
                    new_row = st.session_state.df.iloc[row_idx].copy()
                    new_row[col_name] = line
                    new_rows.append(new_row)

                # Update the DataFrame
                st.session_state.df = pd.concat(
                    [st.session_state.df.drop(index=row_idx), pd.DataFrame(new_rows)],
                    ignore_index=True,
                )

                # Reset selection
                st.session_state.selected_row = None
                st.session_state.selected_col = None

                st.success("Cell split successfully! Updated data:")
                st.dataframe(st.session_state.df)

if __name__ == "__main__":
    main()
