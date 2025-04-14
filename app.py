import streamlit as st
import fitz  # PyMuPDF
from vertexai.preview.generative_models import GenerativeModel
import vertexai

# --- Google Vertex AI Init ---
PROJECT_ID = "nyayainlp"
vertexai.init(project=PROJECT_ID, location="us-central1")
model = GenerativeModel("gemini-2.0-flash-001")
# MODEL_ID="gemini-2.0-flash-001"
# PROJECT_ID="YOUR_PROJECT_ID"

# --- Extract Text from PDFs ---
@st.cache_data(show_spinner=False)
def extract_documents():
    pdf_paths = {
        "Bharatiya Nyaya Sanhita": "Bharatiya Nyaya Sanhita.pdf",
        "Bharatiya Nagarik Suraksha Sanhita": "Bharatiya Nagarik Suraksha Sanhita.pdf",
        "Bharatiya Sakshya Adhiniyam": "Bharatiya Sakshya Adhiniyam.pdf",
    }
    documents = {}
    for law, path in pdf_paths.items():
        try:
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            documents[law] = text
        except Exception as e:
            documents[law] = f"⚠️ Could not load {law}: {e}"
    return documents

# --- Load Documents ---
documents = extract_documents()

# --- UI ---
st.set_page_config("NyayAI - Legal Assistant")
st.title("⚖️ NyayAI")
st.markdown("Ask legal questions or search for specific sections in BNS, BNSS, or Sakshya Adhiniyam.")

# Law dropdown
law = st.selectbox("📘 Choose Law", list(documents.keys()))
doc_text = documents[law]

# Search bar
search_query = st.text_input("🔍 Search Section or Keyword", placeholder="e.g., Section 420 or Arrest")

# Search results
if search_query:
    results = []
    for para in doc_text.split("\n"):
        if search_query.lower() in para.lower():
            results.append(para.strip())
    if results:
        st.subheader("📄 Matching Sections")
        for i, result in enumerate(results[:5]):  # Limit to 5 results
            with st.expander(f"Match {i+1}"):
                st.write(result)
                if st.button(f"Ask Gemini about this", key=f"gemini_{i}"):
                    with st.spinner("Asking Gemini..."):
                        prompt = (
                            f"You are a legal AI assistant. Based on the following section from {law}, explain it in simple terms:\n\n"
                            f"{result}"
                        )
                        try:
                            response = model.generate_content(prompt)
                            st.success("🧠 Gemini says:")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"Error generating response: {e}")
    else:
        st.warning("No matching content found.")

# Ask general legal question
st.markdown("---")
st.subheader("💬 Ask a Legal Question")
question = st.text_input("🧾 Your Question", placeholder="e.g., What is Section 420 in BNS?")
if st.button("Get Answer"):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Consulting legal wisdom..."):
            context = doc_text[:12000]
            prompt = (
                f"You are a legal AI assistant. Refer to the following excerpt from {law}:\n\n"
                f"{context}\n\n"
                f"Now answer this question based on it:\n\n{question}"
            )
            try:
                response = model.generate_content(prompt)
                st.success("🧠 Gemini says:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error generating response: {e}")

st.markdown("---")
st.subheader("📖 Read More")
st.write(doc_text)

st.markdown("---")
st.write("Built with ❤️ by [Arpit Saxena](https://www.linkedin.com/in/iarpitsaxena/)")

st.markdown("---")
st.write("Disclaimer: This is a prototype and not a substitute for professional legal advice. Always consult a qualified lawyer before making any legal decisions.")


