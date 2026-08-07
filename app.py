"""
app.py

Streamlit UI for the RAG Document Chatbot.
Upload a document, then ask questions about its content.
"""

import os
import tempfile

import streamlit as st

from chatbot import build_vector_store, answer_question

st.set_page_config(page_title="RAG Document Chatbot", page_icon="📄")
st.title("📄 RAG Document Chatbot")
st.write(
    "Upload a document and ask questions about it. The chatbot retrieves "
    "relevant sections of your document and uses them to ground its answers."
)

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload a .txt or .pdf document", type=["txt", "pdf"])

if uploaded_file is not None and st.button("Process document"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    with st.spinner("Reading and indexing document..."):
        st.session_state.vector_store = build_vector_store(tmp_path)

    os.remove(tmp_path)
    st.success("Document processed. You can now ask questions below.")

st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask a question about your document...")

if question:
    if st.session_state.vector_store is None:
        st.warning("Please upload and process a document first.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.spinner("Thinking..."):
            answer = answer_question(st.session_state.vector_store, question)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)
