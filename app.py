
# app.py
import streamlit as st
import openai
import re
import tempfile
import os
from docx import Document
import fitz  # PyMuPDF

# Configuration
openai.api_key = st.secrets["OPENAI_API_KEY"]
PPI_PATTERNS = {
    "FULL_NAME": r"[A-Z][a-z]+\s[A-Z][a-z]+",
    "SIN": r"\d{3}-\d{3}-\d{3}"
}

# Utilities
def load_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def load_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def strip_ppi(text):
    index = {}
    for label, pattern in PPI_PATTERNS.items():
        matches = re.findall(pattern, text)
        for i, match in enumerate(matches):
            marker = f"{{{{{label}_{i+1}}}}}"
            text = text.replace(match, marker)
            index[marker] = match
    return text, index

def reinject_ppi(text, index):
    for marker, original in index.items():
        text = text.replace(marker, original)
    return text

def send_to_gpt(instruction, redacted_text):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{instruction}\n\n{redacted_text}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("🔐 PPI-Safe Copilot Agent")
uploaded_file = st.file_uploader("Upload a Word or PDF document", type=["docx", "pdf"])
instruction = st.text_area("Enter instructions for ChatGPT")

if st.button("Process Document"):
    if uploaded_file and instruction:
        with st.spinner("Processing..."):
            file_type = uploaded_file.name.split(".")[-1]
            if file_type == "docx":
                text = load_docx(uploaded_file)
            elif file_type == "pdf":
                text = load_pdf(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            redacted, index = strip_ppi(text)
            gpt_output = send_to_gpt(instruction, redacted)
            final_text = reinject_ppi(gpt_output, index)

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            tmp.write(final_text.encode("utf-8"))
            tmp.close()

            st.success("✅ Done! Download below.")
            st.download_button("Download updated document", open(tmp.name, "rb"), file_name="Updated_Output.txt")
    else:
        st.warning("Please upload a file and enter instructions.")
