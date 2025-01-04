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
    
    # Step 1: File Upload Section
    upload_option = st.selectbox("Choose upload method", ["Google Drive (Secret)", "Manual Upload"])
    df = None
    
    if upload_option == "Google Drive (Secret)":
        if st.button("Load from Google Drive"):
            try:
                df = fetch_csv_from_drive()
                st.success("Data loaded successfully!")
            except Exception as e:
                st.error(f"Failed to load: {e}")
    
    elif upload_option == "Manual Upload":
        uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.success("File uploaded successfully!")
    
    # Step 2: Display Data
    if df is not None:
        st.write("Data Preview:")
        st.dataframe(df)
        selected_cell_content = None
        
        # Step 3: Cell Selection or Manual Entry
        cell_action = st.radio("Choose action:", ["Click a Cell", "Enter Cell Content"])
        if cell_action == "Click a Cell":
            selected_row = st.number_input("Enter row number (1-indexed):", min_value=1, max_value=len(df), step=1) - 1
            selected_col = st.selectbox("Select column:", df.columns.tolist())
            selected_cell_content = df.iloc[selected_row][selected_col]
        elif cell_action == "Enter Cell Content":
            selected_cell_content = st.text_area("Enter content to break down:")
        
        if selected_cell_content:
            # Ensure content is treated as a string
            selected_cell_content = str(selected_cell_content)
            st.write(f"Selected Content: {selected_cell_content}")
            
            # Step 4: Process Breakdown
            breakdown_lines = selected_cell_content.split("\n")
            updated_rows = []
            for _, row in df.iterrows():
                row_data = row.to_dict()
                if str(row[selected_col]) == selected_cell_content:
                    for line in breakdown_lines:
                        new_row = row_data.copy()
                        new_row[selected_col] = line
                        updated_rows.append(new_row)
                else:
                    updated_rows.append(row_data)
            
            # Create updated DataFrame using pd.DataFrame
            updated_df = pd.DataFrame(updated_rows)
            
            st.write("Updated Data:")
            st.dataframe(updated_df)
            
            # Step 5: Download Modified File
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                updated_df.to_excel(writer, index=False)
            buffer.seek(0)
            st.download_button(
                label="Download Modified File",
                data=buffer,
                file_name="updated_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

if __name__ == "__main__":
    main()
