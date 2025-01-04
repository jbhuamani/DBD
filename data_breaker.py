import streamlit as st
import pandas as pd
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build

def load_google_drive_sheet(sheet_id, range_name, credentials_secret):
    """Load Google Sheet data using Google Drive API."""
    creds = service_account.Credentials.from_service_account_info(st.secrets[credentials_secret])
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    return pd.DataFrame(values[1:], columns=values[0])

def main():
    st.title("Data Breaker Program (DBD)")
    
    # Step 1: File Upload Section
    upload_option = st.selectbox("Choose upload method", ["Google Drive", "Manual Upload"])
    df = None
    
    if upload_option == "Google Drive":
        st.text("Provide Google Sheet details:")
        sheet_id = st.text_input("Google Sheet ID")
        range_name = st.text_input("Range Name (e.g., 'Sheet1')")
        credentials_secret = st.text_input("Secret Name in Streamlit", value="google_drive_secret")
        if st.button("Load from Google Drive"):
            try:
                df = load_google_drive_sheet(sheet_id, range_name, credentials_secret)
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
            st.write(f"Selected Content: {selected_cell_content}")
            
            # Step 4: Process Breakdown
            breakdown_lines = selected_cell_content.split("\n")
            updated_df = pd.DataFrame()
            for _, row in df.iterrows():
                row_data = row.to_dict()
                if row[selected_col] == selected_cell_content:
                    for line in breakdown_lines:
                        new_row = row_data.copy()
                        new_row[selected_col] = line
                        updated_df = updated_df.append(new_row, ignore_index=True)
                else:
                    updated_df = updated_df.append(row, ignore_index=True)
            
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
