import streamlit as st, pandas as pd

st.title("📃EXCEL File Reader")

files = st.file_uploader("Upload Excel files:*",type=["xlsx","xls","xlsm","xlsb","CSV","txt","json","xml","ods"],accept_multiple_files=True)
if files:
    for file in files:
        ext = (file.name).split(".")[-1]
        if ext in ["xlsx","xls","xlsm","xlsb"]:
            df = pd.read_excel(file)
        elif ext == "csv":
            df = pd.read_csv(file)
        elif ext == "txt":
            df = pd.read_csv(file,delimiter="\t")
        elif ext == "json":
            df = pd.read_json(file)
        elif ext == "xml":
            df = pd.read_xml(file)
        elif ext == "ods":
            df = pd.read_excel(file,engine="odf")
        else:
            st.error(f"❌ {file.name} file type is not supported")
            continue
        if df is not None:
            st.success(f"✅ \"{file.name}\" File Loaded Successfully")
            st.dataframe(df)
        else:
            st.error(f"Problem in DF creation")