import streamlit as st
import pandas as pd

st.set_page_config(page_title="📊 Excel & Data File Reader", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    /* Global background */
    .main {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: #f8fafc;
        font-family: "Segoe UI", "Roboto", sans-serif;
    }
    /* Title */
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    /* File uploader */
    .stFileUploader {
        border: 2px dashed #38bdf8;
        border-radius: 12px;
        padding: 1.2rem;
        background-color: #1e293b;
    }
    /* Success and error boxes */
    .success-box {
        background: rgba(34, 197, 94, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #22c55e;
        color: #bbf7d0;
    }
    .error-box {
        background: rgba(239, 68, 68, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ef4444;
        color: #fecaca;
    }
    /* Info text and caption */
    .stCaption, .stMarkdown, .stExpander {
        color: #f1f5f9 !important;
    }
    /* Dataframe container */
    [data-testid="stDataFrame"] {
        background-color: #f8fafc;
        border-radius: 8px;
    }
    /* Divider */
    hr {
        border: 1px solid rgba(148, 163, 184, 0.3);
    }
    /* Footer */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("📊 Excel & Data File Reader")
st.markdown("#### Upload, analyze, and preview your data files instantly.")
st.markdown("<hr>", unsafe_allow_html=True)

# --- File Upload Section ---
files = st.file_uploader(
    "📂 Drag & drop or browse files (Excel, CSV, JSON, etc.)",
    type=["xlsx", "xls", "xlsm", "xlsb", "csv", "txt", "json", "xml", "ods"],
    accept_multiple_files=True
)

if files:
    st.subheader("🗂️ Uploaded Files")

    for file in files:
        ext = file.name.split(".")[-1].lower()
        df = None

        try:
            # --- File loading ---
            if ext in ["xlsx", "xls", "xlsm", "xlsb"]:
                df = pd.read_excel(file)
            elif ext == "csv":
                df = pd.read_csv(file)
            elif ext == "txt":
                df = pd.read_csv(file, delimiter="\t")
            elif ext == "json":
                df = pd.read_json(file)
            elif ext == "xml":
                df = pd.read_xml(file)
            elif ext == "ods":
                df = pd.read_excel(file, engine="odf")
            else:
                st.markdown(f"<div class='error-box'>❌ Unsupported file type: <b>{file.name}</b></div>", unsafe_allow_html=True)
                continue

            # --- Success message ---
            st.markdown(f"<div class='success-box'>✅ <b>{file.name}</b> loaded successfully!</div>", unsafe_allow_html=True)
            st.caption(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")

            # --- Data Preview ---
            with st.expander(f"🔍 Preview {file.name}", expanded=False):
                st.dataframe(df, use_container_width=True)

            st.markdown("<hr>", unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f"<div class='error-box'>❌ Error reading <b>{file.name}</b>: {e}</div>", unsafe_allow_html=True)

else:
    st.info("👆 Please upload one or more supported files to begin.")

# --- Footer ---
st.markdown("<div class='footer'>🧩 Designed with Aj in the India using Streamlit</div>", unsafe_allow_html=True)
