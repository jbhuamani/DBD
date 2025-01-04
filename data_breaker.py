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
        st.write("Click on a cell to select it:")
        selected_cell = st.experimental_data_editor(df, key="data_editor", num_rows="dynamic")

        # Detect the selected cell
        if selected_cell:
            st.session_state.selected_row = selected_cell.get("selected_row")
            st.session_state.selected_col = selected_cell.get("selected_col")

        if st.session_state.selected_row is not None and st.session_state.selected_col is not None:
            selected_row = st.session_state.selected_row
            selected_col = st.session_state.selected_col
            selected_content = df.iloc[selected_row, selected_col]
            st.write(f"Selected Content: {selected_content}")

            # Step 3: Split Cell Logic
            if st.button("Split Cell"):
                selected_content = str(selected_content)  # Ensure it's a string
                breakdown_lines = selected_content.split("\n")
                
                # Create new rows based on breakdown
                new_rows = []
                for line in breakdown_lines:
                    new_row = df.iloc[selected_row].copy()
                    new_row[selected_col] = line
                    new_rows.append(new_row)
                
                # Drop the original row and add new rows
                st.session_state.df = pd.concat(
                    [df.drop(index=selected_row), pd.DataFrame(new_rows)],
                    ignore_index=True
                )

                # Display updated DataFrame
                st.write("Updated Data:")
                st.dataframe(st.session_state.df)

                # Step 4: Download Updated File
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
