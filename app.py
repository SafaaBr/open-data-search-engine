import streamlit as st

st.set_page_config(
    page_title="Kaggle Dataset Search",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Intelligent Kaggle Dataset Search")

query = st.text_input(
    "Search for a dataset",
    placeholder="Example: I need a dataset for classification..."
)

if st.button("Search"):
    st.write(query)