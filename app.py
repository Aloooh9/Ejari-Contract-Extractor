import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="Ejari Data Extractor", layout="wide")

def extract_rental_data(pdf_file):
    text = ""
    try:
        # Extract text from all pages
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        return {"Filename": pdf_file.name, "Error": f"Could not read PDF: {str(e)}"}

    # --- REGEX PATTERNS ---
    # Matches "Property No.(s)" or "Unit No." and grabs the clean alphanumeric string on the next line
    prop_no_match = re.search(r'(?:Property No\.\(s\).*?|Unit No(?:\.\(s\))?.*?)\s*\n\s*([A-Z0-9\-]+)', text, re.IGNORECASE)
    
    start_date_match = re.search(r'Start Date\s*\n*([\d]{2}-[\d]{2}-[\d]{4})', text)
    end_date_match = re.search(r'End Date\s*\n*([\d]{2}-[\d]{2}-[\d]{4})', text)
    contract_amount_match = re.search(r'Actual Contract Amount\s*\n*([\d,]+\.\d{2}\s*AED)', text)
    emirates_id_match = re.search(r'Emirates ID\s*\n*(\d{15})', text)

    return {
        "Filename": pdf_file.name,
        "Property/Unit No": prop_no_match.group(1) if prop_no_match else "N/A",
        "Start Date": start_date_match.group(1) if start_date_match else "N/A",
        "End Date": end_date_match.group(1) if end_date_match else "N/A",
        "Actual Contract Amount": contract_amount_match.group(1) if contract_amount_match else "N/A",
        "Emirates ID": emirates_id_match.group(1) if emirates_id_match else "N/A (Company/Not Found)"
    }

# --- Web App UI ---
st.title("📄 Ejari Contract Extractor")
st.write("Upload your rental PDF files to extract key contract details into a downloadable table.")

uploaded_files = st.file_uploader("Upload PDF Files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Extract Data"):
        with st.spinner(f"Processing {len(uploaded_files)} files..."):
            results = []
            for pdf_file in uploaded_files:
                data = extract_rental_data(pdf_file)
                results.append(data)
            
            # Convert results to a Dataframe
            df = pd.DataFrame(results)
            
            st.success("Extraction Complete!")
            st.dataframe(df, use_container_width=True)
            
            # Convert DF to CSV for download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="extracted_rental_data.csv",
                mime="text/csv",
            )
