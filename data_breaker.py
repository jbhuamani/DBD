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
        uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "csv"])
        if uploaded_file:
            if uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
    
    # Step 2: Display Data
    if df is not None:
        st.write("Data Preview:")
        st.dataframe(df)
        
        # Step 3: Cell Selection
        cell_action = st.radio("Choose action:", ["Click a Cell", "Enter Cell Content"])
        selected_row = None
        selected_col = None
        selected_cell_content = None
        
        if cell_action == "Click a Cell":
            selected_row = st.number_input("Enter row number (1-indexed):", min_value=1, max_value=len(df), step=1) - 1
            selected_col = st.selectbox("Select column:", df.columns.tolist())
            selected_cell_content = df.iloc[selected_row][selected_col]
            st.write(f"Selected Content: {selected_cell_content}")
            
            # Step 4: Split Cell Logic
            if st.button("Split Cell"):
                # Ensure the selected cell content is treated as a string
                selected_cell_content = str(selected_cell_content)
                breakdown_lines = selected_cell_content.split("\n")
                
                # Create new rows based on breakdown
                new_rows = []
                for line in breakdown_lines:
                    new_row = df.iloc[selected_row].copy()
                    new_row[selected_col] = line
                    new_rows.append(new_row)
                
                # Drop the original row and add new rows
                df = pd.concat([df.drop(index=selected_row), pd.DataFrame(new_rows)], ignore_index=True)
                
                # Display updated DataFrame
                st.write("Updated Data:")
                st.dataframe(df)
                
                # Step 5: Download Updated File
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                buffer.seek(0)
                st.download_button(
                    label="Download Updated File",
                    data=buffer,
                    file_name="updated_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
        
        elif cell_action == "Enter Cell Content":
            selected_cell_content = st.text_area("Enter content to break down:")
            if st.button("Split Cell"):
                st.error("Manual entry not yet implemented.")

if __name__ == "__main__":
    main()
