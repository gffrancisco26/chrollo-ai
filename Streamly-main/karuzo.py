import openrouter
import streamlit as st
import logging
import PyPDF2
import docx
from openai import OpenAI

# Logging
logging.basicConfig(level=logging.INFO)

# Constants
NUMBER_OF_MESSAGES_TO_DISPLAY = 20

# OpenRouter Client Initialization
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

# Streamlit Page Config
st.set_page_config(
    page_title="Karuzo - Document Chat",
    page_icon="imgs/avatar_streamly.png",
    layout="wide"
)

# Text Extraction
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return "".join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs])

def get_document_text(file):
    ext = file.name.split('.')[-1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(file)
    elif ext == 'docx':
        return extract_text_from_docx(file)
    else:
        raise ValueError("Only PDF and DOCX files are supported.")

# Chat Completion
def generate_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model="nvidia/llama-3.3-nemotron-super-49b-v1:free",
            messages=messages,
            extra_headers={"HTTP-Referer": "https://yourapp.com", "X-Title": "Karuzo Ai Document Summarizer"},
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenRouter Error: {e}")
        return "⚠️ An error occurred while processing the chat."

# Main App
def main():
    st.title("📄 Document Summarizer")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "document_context" not in st.session_state:
        st.session_state.document_context = None

    uploaded_file = st.file_uploader("Upload a PDF or Word Document", type=["pdf", "docx"])
    if uploaded_file:
        try:
            document_text = get_document_text(uploaded_file)
            st.session_state.document_context = [{"role": "system", "content": f"Document content: {document_text}"}]
            st.success("Document successfully processed. Start chatting below.")
        except Exception as e:
            st.error(f"Error reading document: {str(e)}")

    # Chat interface
    chat_input = st.chat_input("Ask about the document...")
    if chat_input and st.session_state.document_context:
        st.session_state.chat_history.append({"role": "user", "content": chat_input})
        messages = st.session_state.document_context + st.session_state.chat_history
        reply = generate_ai_response(messages)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Display conversation
    for message in st.session_state.chat_history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

if __name__ == "__main__":
    main()
