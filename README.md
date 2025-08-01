# Copilot PPI Agent – Streamlit GUI

A browser-based tool that:
- Strips PPI from Word/PDF documents
- Sends redacted text to GPT-4 for transformation
- Re-injects PPI before output
- Works securely in-browser via Streamlit Cloud

## Setup

Deploy via Streamlit Cloud: https://streamlit.io/cloud

Environment variable required:
- `OPENAI_API_KEY`

## Usage

1. Upload a document
2. Type instructions (e.g., “summarize”, “rewrite for clarity”)
3. Click “Process”
4. Download the updated file
