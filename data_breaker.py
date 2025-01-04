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

    # Step 1: Load Data
    if st.button("Load Data from Google Drive"):
        try:
            st.session_state.df = fetch_csv_from_drive()
            st.success("Data loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load: {e}")

    # Step 2: Display Data
    if st.session_state.df is not None:
        st.write("Loaded Data:")
        # Display the current DataFrame
        st.session_state.df = pd.DataFrame(st.session_state.df)  # Ensure DataFrame integrity
        selected_row = st.selectbox("Select Row (Index):", options=st.session_state.df.index)
        selected_col = st.selectbox("Select Column:", options=st.session_state.df.columns)

        # Step 3: Split Cell
        if st.button("Split Cell"):
            try:
                selected_content = st.session_state.df.loc[selected_row, selected_col]

                # Ensure the selected cell content is a string
                selected_content = str(selected_content)
                breakdown_lines = selected_content.split("\n")

                # Create new rows based on breakdown
                new_rows = []
                for line in breakdown_lines:
                    new_row = st.session_state.df.loc[selected_row].copy()
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

            except Exception as e:
                st.error(f"Error splitting cell: {e}")

if __name__ == "__main__":
    main()
