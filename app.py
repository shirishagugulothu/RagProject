import streamlit as st
import tempfile
import os
from datetime import datetime
from rag_engine import RAGEngine

# Page configuration
st.set_page_config(
    page_title="📚 RAG ChatBot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    .upload-section {
        background: linear-gradient(#355C7D, #6C5B7B, #C06C84);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        text-align: center;
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 12px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 12px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 10px 0;
    }
    
    .sidebar-info {
        background: linear-gradient(#141E30, #243B55);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "document_loaded" not in st.session_state:
    st.session_state.document_loaded = False

if "document_info" not in st.session_state:
    st.session_state.document_info = {}

# Main header
st.markdown('<h1 class="main-header">📚 RAG ChatBot</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Control Panel")
    
    # Document upload section
    st.markdown('<div class="sidebar-info"><h4>📄 Upload Document</h4></div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to ask questions about"
    )
    
    if uploaded_file is not None:
        if st.button("🚀 Process Document", type="primary"):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name
                
                # Process document
                with st.spinner("Processing document..."):
                    chunks_count = st.session_state.rag_engine.load_document(tmp_file_path)
                
                # Clean up
                os.unlink(tmp_file_path)
                
                # Update session state
                st.session_state.document_loaded = True
                st.session_state.document_info = {
                    "name": uploaded_file.name,
                    "size": f"{uploaded_file.size / 1024:.1f} KB",
                    "chunks": chunks_count,
                    "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.success(f"✅ Document processed successfully! Created {chunks_count} chunks.")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
    
    # Document info
    if st.session_state.document_loaded and st.session_state.document_info:
        st.markdown("### 📊 Document Info")
        info = st.session_state.document_info
        st.markdown(f"""
        **📝 Name:** {info['name']}  
        **📏 Size:** {info['size']}  
        **🧩 Chunks:** {info['chunks']}  
        **📅 Uploaded:** {info['uploaded_at']}
        """)
    
    st.markdown("---")
    
    # Chat controls
    st.markdown("### 💬 Chat Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", help="Clear all chat history"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📥 Export Chat", help="Download chat history"):
            if st.session_state.chat_history:
                chat_text = "\n\n".join([
                    f"Q: {item['question']}\nA: {item['answer']}\n---"
                    for item in st.session_state.chat_history
                ])
                st.download_button(
                    label="💾 Download",
                    data=chat_text,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    # Reset system
    if st.button("🔄 Reset System", help="Reset everything"):
        st.session_state.rag_engine.reset()
        st.session_state.chat_history = []
        st.session_state.document_loaded = False
        st.session_state.document_info = {}
        st.rerun()
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📝 How to Use")
    st.markdown("""
    1. **Upload** a PDF document
    2. **Click** 'Process Document'
    3. **Ask** questions about the document
    4. **Export** chat history if needed
    """)

# Main content area
if not st.session_state.document_loaded:
    # Welcome screen
    st.markdown("""
    <div class="upload-section">
        <h2>🎯 Welcome to Smart Document QA!</h2>
        <p>Upload a PDF document to get started. Once uploaded, you can ask any questions about the content and get intelligent answers.</p>
        <p>👈 Use the sidebar to upload your document</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🧠 AI-Powered
        Uses advanced language models to understand and answer your questions accurately.
        """)
    
    with col2:
        st.markdown("""
        ### ⚡ Fast Retrieval
        Quickly finds relevant information from your documents using vector search.
        """)
    
    with col3:
        st.markdown("""
        ### 💬 Chat Interface
        Natural conversation interface with chat history and export features.
        """)

else:
    # Chat interface
    st.markdown("### 💬 Ask Questions About Your Document")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📜 Chat History")
        for i, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong> {chat['question']}
            </div>
            <div class="bot-message">
                <strong>AI:</strong> {chat['answer']}
            </div>
            """, unsafe_allow_html=True)
    
    # Question input
    st.markdown("---")
    
    # Create a form for enter key functionality
    with st.form(key="question_form", clear_on_submit=True):
        question = st.text_input(
            "Ask a question about your document:",
            placeholder="e.g., What is the main topic discussed in the document?",
            key="question_input"
        )
        
        col1, col2 = st.columns([6, 1])
        with col2:
            ask_button = st.form_submit_button("Get response", type="primary")
    
    if ask_button and question:
        if question.strip():
            with st.spinner("🤔 Thinking..."):
                answer = st.session_state.rag_engine.retrieve_and_answer(question)
            
            # Add to chat history
            st.session_state.chat_history.append({
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Rerun to show the new chat
            st.rerun()
        else:
            st.warning("⚠️ Please enter a valid question.")
    
    elif ask_button:
        st.warning("⚠️ Please enter a question first.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    Built with ❤️ using Streamlit • Powered by AI
</div>
""", unsafe_allow_html=True)