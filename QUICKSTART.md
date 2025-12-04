# 🚀 Quick Start Guide

## First Time Setup (5 minutes)

### 1. Download All Files
From outputs folder, download:
- `app_FIXED.py` → rename to `app.py`
- `setup_db_FIXED.py` → rename to `setup_db.py`  
- `index.html` → put in `templates/` folder
- `requirements_FINAL.txt` → rename to `requirements.txt`
- `README.md`
- `.gitignore`
- `run.sh` (optional convenience script)

### 2. Install Dependencies
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 3. Set API Key
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### 4. Initialize Database
```bash
./venv/bin/python setup_db.py
```
This downloads the NTA PDF and creates embeddings (takes 2-3 minutes).

### 5. Run the App
```bash
./venv/bin/python app.py
```

### 6. Open Browser
```
http://localhost:5000
```

## Testing Checklist

- [ ] Ask "What is the tax rate for residents?" → See fact-checked answer
- [ ] Click "Upload PDF" → Upload test PDF → See success message
- [ ] Ask about uploaded content → Verify it works
- [ ] Click "Clear History" → Conversation resets
- [ ] Try asking nonsense → Should get rejection or clarification

## Common Issues

### "ModuleNotFoundError"
```bash
./venv/bin/pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### "Knowledge base not initialized"
```bash
./venv/bin/python setup_db.py
```

### "Template not found"
Make sure `index.html` is in `templates/` folder:
```bash
mkdir -p templates
mv index.html templates/
```

## For Portfolio/GitHub

### Take Screenshots
1. Main interface
2. Answer with fact-check badge
3. Upload success

### Update README
Add screenshots to README.md

### Push to GitHub
```bash
git init
git add .
git commit -m "Japanese Tax Q&A Bot with RAG and fact-checking"
git remote add origin https://github.com/arimotokk/tax-chatbot.git
git push -u origin main
```

## Project Structure
```
tax-chatbot/
├── app.py                   # Main application
├── setup_db.py             # Database setup
├── requirements.txt        # Dependencies
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
├── templates/
│   └── index.html         # Web UI
├── venv/                  # Virtual env (not committed)
└── chroma_db/             # Vector DB (not committed)
```

## What Model Are You Using?
Claude Sonnet 4.5 (`claude-sonnet-4-20250514`) for both:
- Answer generation
- Fact-checking validation

## Next Steps After Setup

1. **Test thoroughly** - Ask various tax questions
2. **Take screenshots** - For README/portfolio
3. **Push to GitHub** - Make it public
4. **Add to LinkedIn** - Portfolio projects section
5. **Prepare talking points** - See PROJECT_COMPLETE.md

---

**Need help?** Check PROJECT_COMPLETE.md for detailed explanations.
