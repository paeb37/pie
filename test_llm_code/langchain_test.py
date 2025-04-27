from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load PDFs
loader = PyPDFLoader("../files/your_document.pdf")
pages = loader.load_and_split()

# 2. Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
texts = text_splitter.split_documents(pages)

# 3. Create embeddings using Gemini
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key="YOUR_API_KEY"
)

# 4. Build Vector Store
vector_store = FAISS.from_documents(texts, embeddings)

# 5. Create QA Chain with Gemini Pro
llm = ChatGoogleGenerativeAI(model="gemini-pro")
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vector_store.as_retriever(),
    return_source_documents=True
)

# 6. Query with PDF context
response = qa_chain.invoke("Your question here")
print(response["result"])
