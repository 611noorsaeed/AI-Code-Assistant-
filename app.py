import streamlit as st
from langchain_client import LangChainClient
import tempfile, os
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader

st.set_page_config(page_title="AI Code Assistant", layout="wide")

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = None
if "uploaded_texts" not in st.session_state:
    st.session_state.uploaded_texts = {}  # {filename: extracted_text}

st.title("🤖 AI Code Assistant (Gemini + LangChain + Streamlit)")

# --- Sidebar Upload ---
st.sidebar.header("📂 Project Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload project files",
    accept_multiple_files=True,
    type=[
        "py", "js", "ts", "java", "cpp", "c", "html", "css", "json",
        "go", "rb", "php", "cs", "txt", "md", "docx", "pdf"
    ]
)

# --- Sidebar Mode Dropdown ---
st.sidebar.header("⚙️ Mode Selection")
mode = st.sidebar.selectbox(
    "Choose assistant mode (required)",
    [
        "General", "Code Analysis", "Code Generator", "Debugger",
        "Code Guide", "Optimization", "Explain Code",
        "Project Builder", "Documentation"
    ],
    index=0
)
st.session_state.mode = mode

# Init LangChain client
LC = LangChainClient(mode=st.session_state.mode)
st.caption(f"🟢 Assistant is running in **{mode}** mode")

# --- File Content Extractor (with LangChain loaders) ---
def extract_text(file):
    suffix = os.path.splitext(file.name)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    try:
        if suffix == ".docx":
            loader = Docx2txtLoader(tmp_path)
        elif suffix == ".pdf":
            loader = PyPDFLoader(tmp_path)
        else:
            # plain text or code file
            with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        docs = loader.load()
        return "\n".join([doc.page_content for doc in docs])
    finally:
        os.unlink(tmp_path)  # cleanup temp file

# --- Save uploaded file text in session (no auto-analysis) ---
if uploaded_files:
    for f in uploaded_files:
        if f.name not in st.session_state.uploaded_texts:
            try:
                st.session_state.uploaded_texts[f.name] = extract_text(f)
            except Exception as e:
                st.session_state.uploaded_texts[f.name] = f"⚠ Could not read {f.name}: {e}"
    st.sidebar.success(f"{len(st.session_state.uploaded_texts)} file(s) ready for analysis.")

# --- Analyze Button ---
if uploaded_files:
    if st.sidebar.button("🔍 Analyze Uploaded Files"):
        combined_texts = "\n\n".join(
            [f"📄 {name}:\n{text[:3000]}" for name, text in st.session_state.uploaded_texts.items()]
        )
        # Send to LLM without polluting chat history
        with st.chat_message("assistant"):
            with st.spinner("Analyzing uploaded files..."):
                reply = LC.chat(
                    st.session_state.messages + [{"role": "user", "content": combined_texts}]
                )
                st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# --- Chat history ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ask me to generate code, debug, review, or explain..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = LC.chat(st.session_state.messages)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
