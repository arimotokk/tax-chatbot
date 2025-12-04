import os
from flask import Flask, render_template, request, jsonify, session
from anthropic import Anthropic
import chromadb
from chromadb.utils import embedding_functions
import uuid
import PyPDF2
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Get or create collection with sentence-transformers (Mac-friendly)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

try:
    collection = chroma_client.get_collection(
        name="nta_tax_docs",
        embedding_function=sentence_transformer_ef
    )
except:
    collection = None

@app.route('/')
def index():
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    if collection is None:
        return jsonify({'error': 'Knowledge base not initialized. Please run setup_db.py first.'}), 500
    
    # Retrieve conversation history from session
    if 'history' not in session:
        session['history'] = []
    
    try:
        # Query ChromaDB for relevant chunks
        results = collection.query(
            query_texts=[question],
            n_results=5
        )
        
        # Extract relevant chunks and metadata
        chunks = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        
        if not chunks:
            return jsonify({
                'answer': 'I could not find relevant information in the tax documents to answer your question.',
                'sources': [],
                'excerpts': []
            })
        
        # Build context from retrieved chunks
        context = "\n\n".join([f"[Source: {meta.get('source', 'Unknown')} - Page {meta.get('page', 'Unknown')}]\n{chunk}" 
                               for chunk, meta in zip(chunks, metadatas)])
        
        # Build conversation context
        conversation_context = ""
        if session['history']:
            conversation_context = "Previous conversation:\n"
            for turn in session['history'][-3:]:  # Last 3 turns for context
                conversation_context += f"Q: {turn['question']}\nA: {turn['answer']}\n\n"
        
        # Generate answer with Claude
        prompt = f"""You are a helpful assistant answering questions about Japanese individual income tax based on official NTA (National Tax Agency) guidelines.

{conversation_context}

Based on the following excerpts from official Japanese tax documents, answer the user's question accurately and comprehensively.

Context from tax documents:
{context}

User question: {question}

Please provide:
1. A clear, accurate answer to the question
2. Cite specific sources (document name and page number)
3. Include relevant excerpts from the source documents to support your answer

Format your response as:
ANSWER: [Your detailed answer here]

SOURCES: [List the specific sources you referenced, e.g., "2024 Income Tax Guide, Page 15"]

EXCERPTS: [Include the most relevant quoted passages that support your answer]"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer_text = response.content[0].text
        
        # Parse response
        answer_parts = answer_text.split('SOURCES:')
        answer = answer_parts[0].replace('ANSWER:', '').strip()
        
        sources_and_excerpts = answer_parts[1] if len(answer_parts) > 1 else ''
        excerpts_parts = sources_and_excerpts.split('EXCERPTS:')
        sources = excerpts_parts[0].strip()
        excerpts = excerpts_parts[1].strip() if len(excerpts_parts) > 1 else ''
        
        # FACT-CHECKING AGENT - Validate answer before showing to user
        fact_check_prompt = f"""You are a fact-checking agent. Your job is to verify if the answer provided is accurate based on the source documents.

SOURCE DOCUMENTS:
{context}

GENERATED ANSWER:
{answer}

Please verify:
1. Is the answer supported by the source documents?
2. Are there any factual errors or hallucinations?
3. Does the answer contradict information in the sources?

Respond with ONLY ONE WORD:
- "APPROVED" if the answer is accurate and supported by sources
- "REJECTED" if there are errors, hallucinations, or contradictions

After your verdict, provide a brief explanation (1-2 sentences).

Format:
VERDICT: [APPROVED or REJECTED]
REASON: [Brief explanation]"""

        fact_check_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": fact_check_prompt}]
        )
        
        fact_check_text = fact_check_response.content[0].text
        
        # Parse fact-check result
        verdict_approved = "APPROVED" in fact_check_text.upper()
        
        # Extract reason
        reason_parts = fact_check_text.split('REASON:')
        fact_check_reason = reason_parts[1].strip() if len(reason_parts) > 1 else "Validation completed"
        
        if not verdict_approved:
            # Answer rejected - inform user
            return jsonify({
                'answer': '⚠️ I could not generate a reliable answer to your question. The fact-checker detected potential inaccuracies in my response. Please try rephrasing your question or ask something more specific.',
                'sources': '',
                'excerpts': '',
                'validation_status': 'rejected',
                'validation_reason': fact_check_reason
            })
        
        # Answer approved - store in conversation history
        session['history'].append({
            'question': question,
            'answer': answer,
            'sources': sources,
            'excerpts': excerpts,
            'validation_status': 'approved'
        })
        session.modified = True
        
        return jsonify({
            'answer': answer,
            'sources': sources,
            'excerpts': excerpts,
            'retrieved_chunks': len(chunks),
            'validation_status': 'approved',
            'validation_reason': fact_check_reason
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    session['history'] = []
    session.modified = True
    return jsonify({'success': True})

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload additional PDF documents to expand the knowledge base"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400
    
    try:
        # Read PDF
        pdf_file = BytesIO(file.read())
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        documents = []
        metadatas = []
        
        # Extract text from PDF
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            if text.strip():
                # Split into chunks
                chunk_size = 1000
                overlap = 200
                
                for i in range(0, len(text), chunk_size - overlap):
                    chunk = text[i:i + chunk_size]
                    if len(chunk.strip()) > 100:
                        documents.append(chunk)
                        metadatas.append({
                            'source': file.filename,
                            'page': page_num + 1,
                            'doc_url': 'user_uploaded'
                        })
        
        if not documents:
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Add to existing collection
        if collection is None:
            return jsonify({'error': 'Knowledge base not initialized'}), 500
        
        # Get current max ID
        existing_count = collection.count()
        
        # Add new documents
        batch_size = 100
        total_added = 0
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_metas = metadatas[i:i + batch_size]
            batch_ids = [f"doc_{existing_count + j}" for j in range(i, i + len(batch_docs))]
            
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
            total_added += len(batch_docs)
        
        return jsonify({
            'success': True,
            'message': f'Successfully added {total_added} chunks from {file.filename}',
            'pages': num_pages,
            'chunks': total_added
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
