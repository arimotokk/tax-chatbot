# Japanese Tax Q&A Bot - Phase 1 Setup

## Quick Start

1. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your_key_here'
```

3. Download and process NTA documents (takes 2-3 minutes):
```bash
./venv/bin/python setup_db.py
```

4. Run the app:
```bash
./venv/bin/python app.py
```

5. Open browser to: http://localhost:5000

## What Phase 1 Does

- Downloads official 2024 NTA Income Tax Guide (English)
- Extracts and chunks text into ~1000 character segments
- Creates vector embeddings using ChromaDB
- Retrieves top 5 relevant chunks for each question
- Generates answers with Claude Sonnet 4.5
- Provides citations (source + page numbers)
- Includes relevant excerpts from documents
- Maintains conversation history within session

## Files Created

- `app.py` - Flask web application
- `setup_db.py` - Database initialization script
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies
- `chroma_db/` - Vector database (created after setup)

## Testing

Try these questions:
1. "What is the tax rate for residents in Japan?"
2. "How is retirement income taxed?"
3. "What deductions are available?"

The bot will retrieve relevant chunks, generate an answer, and show you the sources and excerpts.
