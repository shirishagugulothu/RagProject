import fitz
import textwrap
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline

class RAGEngine:
    def __init__(self):
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.generator = pipeline("text2text-generation", model="google/flan-t5-small")
        self.chunks = []
        self.index = None
        self.document_loaded = False

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def chunk_text(self, text, chunk_size=300):
        """Split text into chunks"""
        return textwrap.wrap(text, width=chunk_size)

    def create_embeddings_and_index(self, chunks):
        """Create embeddings and FAISS index"""
        embeddings = self.embed_model.encode(chunks)
        dim = embeddings[0].shape[0]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings))
        return index

    def load_document(self, pdf_path):
        """Load and process document"""
        try:
            # Extract text
            document_text = self.extract_text_from_pdf(pdf_path)
            
            if not document_text.strip():
                raise Exception("No text found in the PDF")
            
            # Create chunks
            self.chunks = self.chunk_text(document_text)
            
            if not self.chunks:
                raise Exception("Failed to create text chunks")
            
            # Create index
            self.index = self.create_embeddings_and_index(self.chunks)
            self.document_loaded = True
            
            return len(self.chunks)
            
        except Exception as e:
            self.document_loaded = False
            raise Exception(f"Failed to load document: {str(e)}")

    def retrieve_and_answer(self, query, top_k=3):
        """Retrieve relevant chunks and generate answer"""
        if not self.document_loaded:
            return "Please upload a document first."
        
        try:
            # Get query embedding
            query_embedding = self.embed_model.encode([query])
            
            # Search similar chunks
            _, indices = self.index.search(
                np.array(query_embedding).astype("float32"), 
                top_k
            )
            
            # Retrieve relevant text
            retrieved_texts = [self.chunks[i] for i in indices[0]]
            context = " ".join(retrieved_texts)
            
            # Generate answer
            prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
            result = self.generator(prompt, max_length=100, do_sample=True)
            
            return result[0]['generated_text']
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def reset(self):
        """Reset the engine"""
        self.chunks = []
        self.index = None
        self.document_loaded = False