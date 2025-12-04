import os
import requests
from anthropic import Anthropic
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
from io import BytesIO

print("=" * 60)
print("Japanese Tax RAG Database Setup")
print("=" * 60)

# Initialize clients
print("\n[1/5] Initializing clients...")
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Download NTA PDF
pdf_url = "https://www.nta.go.jp/english/taxes/individual/pdf/incometax_2024/01.pdf"
print(f"\n[2/5] Downloading NTA 2024 Income Tax Guide...")
print(f"URL: {pdf_url}")

response = requests.get(pdf_url)
if response.status_code != 200:
    print(f"❌ Failed to download PDF. Status code: {response.status_code}")
    exit(1)

print(f"✓ Downloaded successfully ({len(response.content) / 1024 / 1024:.1f} MB)")

# Extract text from PDF
print("\n[3/5] Extracting text from PDF...")
pdf_file = BytesIO(response.content)
pdf_reader = PyPDF2.PdfReader(pdf_file)
num_pages = len(pdf_reader.pages)
print(f"Total pages: {num_pages}")

documents = []
metadatas = []

for page_num in range(num_pages):
    page = pdf_reader.pages[page_num]
    text = page.extract_text()
    
    if text.strip():
        # Split into chunks of roughly 1000 characters with overlap
        chunk_size = 1000
        overlap = 200
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if len(chunk.strip()) > 100:  # Only keep substantial chunks
                documents.append(chunk)
                metadatas.append({
                    'source': '2024 NTA Income Tax Guide',
                    'page': page_num + 1,
                    'doc_url': pdf_url
                })
    
    if (page_num + 1) % 10 == 0:
        print(f"  Processed {page_num + 1}/{num_pages} pages...")

print(f"✓ Extracted {len(documents)} text chunks")

# Create embeddings using sentence-transformers
print("\n[4/5] Creating vector embeddings with sentence-transformers...")

# Delete existing collection if it exists
try:
    chroma_client.delete_collection(name="nta_tax_docs")
    print("  Deleted existing collection")
except:
    pass

# Create sentence transformer embedding function (works on Mac)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create new collection
collection = chroma_client.create_collection(
    name="nta_tax_docs",
    embedding_function=sentence_transformer_ef,
    metadata={"description": "Japanese individual income tax documents from NTA"}
)

# Add documents in batches
batch_size = 100
for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i + batch_size]
    batch_metas = metadatas[i:i + batch_size]
    batch_ids = [f"doc_{j}" for j in range(i, i + len(batch_docs))]
    
    collection.add(
        documents=batch_docs,
        metadatas=batch_metas,
        ids=batch_ids
    )
    
    print(f"  Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")

print(f"✓ Created vector database with {len(documents)} chunks")

# Test query
print("\n[5/5] Testing database...")
test_results = collection.query(
    query_texts=["What is the tax rate for residents?"],
    n_results=3
)

if test_results['documents'][0]:
    print("✓ Database test successful!")
    print(f"  Sample result: {test_results['documents'][0][0][:100]}...")
else:
    print("❌ Database test failed - no results returned")

print("\n" + "=" * 60)
print("✅ Setup complete! You can now run: python app.py")
print("=" * 60)
