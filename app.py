
import re
import pandas as pd
import streamlit as st

# Define domain filters
domain_filters = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "protonmail.com", "zoho.com", "icloud.com", "gmx.com"
]

# Define keyword filters
keyword_filters = ["abuse", "admin", "support", "sales", ".edu", ".gov"]
keyword_pattern = r"(?:" + "|".join(keyword_filters) + r")"

# Function to extract emails
def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(email_pattern, text)))
    emails = [email.rstrip('.') for email in emails]  # Remove trailing '.'
    return emails

# Streamlit UI
st.title("📧 Email Extractor & Filter")

uploaded_file = st.file_uploader("Upload a .txt file", type=['txt'])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    emails = extract_emails(content)

    if emails:
        df = pd.DataFrame(emails, columns=["Email"])
        duplicates_df = df[df.duplicated(keep=False)]
        df = df.drop_duplicates(keep="first")

        mask_domain = df['Email'].str.contains('|'.join(domain_filters), case=False, na=False)
        mask_keyword = df['Email'].str.contains(keyword_pattern, case=False, na=False, regex=True)

        domain_filtered_df = df[mask_domain]
        keyword_filtered_df = df[mask_keyword]
        other_domains_df = df[~(mask_domain | mask_keyword)]

        output_file = "filtered_emails.xlsx"
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            domain_filtered_df.to_excel(writer, sheet_name='domain_filters', index=False)
            keyword_filtered_df.to_excel(writer, sheet_name='keyword_filters', index=False)
            other_domains_df.to_excel(writer, sheet_name='other_domains', index=False)
            duplicates_df.to_excel(writer, sheet_name='duplicates', index=False)
            df.to_excel(writer, sheet_name='full_dataset', index=False)

        st.success(f"✅ Extraction complete! {len(emails)} emails found.")
        st.download_button("📥 Download Filtered Emails", data=open(output_file, 'rb'), file_name="filtered_emails.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    else:
        st.error("No valid emails found in the uploaded file.")
