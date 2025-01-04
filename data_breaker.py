import streamlit as st
import pandas as pd
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def load_google_drive_sheet(sheet_id, range_name, credentials_secret):
    """Load Google Sheet data using Google Drive API."""
    creds = service_account.Credentials.from_service_account_info(st.secrets[credentials_secret])
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    return pd.DataFrame(values[1:], columns=values[0]), creds

def save_to_google_drive(file_data, filename, credentials):
    """Save file to Google Drive."""
    service = build('drive', 'v3', credentials=credentials)
    media = MediaFileUpload(filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_metadata = {"name": filename, "mimeType": "application/vnd.google-apps.spreadsheet"}
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return uploaded_file.get("id")

def main():
    st.title("Data Breaker Program")

    # Step 1: File Upload Section
    upload_option = st.selectbox("Choose upload method", ["Google Drive", "Manual Upload"])
    df = None
    google_drive_used = False
    google_drive_credentials = None

    if upload_option == "Google Drive":
        st.text("Provide Google Sheet details:")
        sheet_id = st.text_input("Google Sheet ID")
        range_name = st.text_input("Range Name (e.g., 'Sheet1')")
        credentials_secret = st.text_input("Secret Name in Streamlit", value="google_drive_secret")
        if st.button("Load from Google Drive"):
            try:
                df, google_drive_credentials = load_google_drive_sheet(sheet_id, range_name, credentials_secret)
                google_drive_used = True
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

            # Step 5: Save Modified File
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                updated_df.to_excel(writer, index=False)
            buffer.seek(0)
            filename = "updated_data.xlsx"

            if google_drive_used:
                st.info("File will be saved back to Google Drive.")
                if st.button("Save to Google Drive"):
                    try:
                        with open(filename, "wb") as f:
                            f.write(buffer.read())
                        file_id = save_to_google_drive(filename, filename, google_drive_credentials)
                        st.success(f"File saved to Google Drive! File ID: {file_id}")
                    except Exception as e:
                        st.error(f"Failed to save to Google Drive: {e}")
            else:
                st.info("File can be downloaded locally.")
                st.download_button(
                    label="Download Modified File",
                    data=buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

if __name__ == "__main__":
    main()
