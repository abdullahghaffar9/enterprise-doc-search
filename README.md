# AI Document Q&A System (RAG)

A production-ready Retrieval-Augmented Generation (RAG) system for intelligent document analysis and question-answering.

## 🏗️ Architecture

```
project-root/
├── backend/              # Python FastAPI backend
│   ├── app/             # Application code
│   ├── scripts/         # Database utilities
│   ├── tests/           # Unit tests
│   ├── requirements.txt # Python dependencies
│   ├── .env            # Environment variables
│   └── reset_db.py     # Database reset script
│
├── frontend/            # React + Vite frontend
│   ├── src/            # React components
│   ├── public/         # Static assets
│   ├── package.json    # Node dependencies
│   └── vite.config.ts  # Vite configuration
│
├── docs/               # Documentation
│   ├── DEBUGGING_GUIDE.md
│   ├── FIXES_SUMMARY.md
│   ├── QUICK_REFERENCE.md
│   └── REFACTOR_ANALYSIS_AND_PLAN.md
│
├── scripts/            # Utility scripts
│   ├── setup.sh       # Setup for Unix/Linux/Mac
│   └── setup.bat      # Setup for Windows
│
├── start_app.py        # One-click launcher for both services
├── .env.example        # Environment template
└── README.md          # This file
```

## 🚀 Quick Start

### Option 1: One-Click Launch (Recommended)
```bash
python start_app.py
```

### Option 2: Manual Launch

**Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend (in a new terminal):**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## ⚙️ Configuration

1. **Copy environment template:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `backend/.env` with your credentials:**
   ```env
   PINECONE_API_KEY=your-api-key
   PINECONE_INDEX_NAME=your-index
   GROQ_API_KEY=your-groq-key
   ```

## 📚 Tech Stack

**Backend:**
- FastAPI (web framework)
- Pinecone (vector database)
- FastEmbed (lightweight embeddings)
- Groq/OpenAI (LLM)

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- Vite (build tool)

## 🔧 Development

### Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Run Tests

```bash
cd backend
pytest tests/
```

### Build for Production

**Frontend:**
```bash
cd frontend
npm run build
```

## 📖 Documentation

- **[DEBUGGING_GUIDE.md](docs/DEBUGGING_GUIDE.md)** - Technical troubleshooting
- **[FIXES_SUMMARY.md](docs/FIXES_SUMMARY.md)** - Architecture improvements
- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Quick command reference
- **[REFACTOR_ANALYSIS_AND_PLAN.md](docs/REFACTOR_ANALYSIS_AND_PLAN.md)** - Future improvements

## 🏅 Key Features

✅ **PDF Upload & Processing**
- Support for text-based PDFs
- Automatic chunking and preprocessing
- Metadata extraction

✅ **Vector Search**
- FastEmbed for efficient embeddings
- Pinecone for vector storage
- Similarity-based document retrieval

✅ **Question Answering**
- RAG-based answer generation
- Multiple LLM providers (Groq, OpenAI)
- Source document citation

✅ **Production Ready**
- Environment-based configuration
- Comprehensive error handling
- Clean architecture with separation of concerns
- Logging and monitoring

## 🐛 Troubleshooting

**Network Error on PDF Upload?**
→ See [DEBUGGING_GUIDE.md](docs/DEBUGGING_GUIDE.md) for solutions

**Import Errors?**
→ Ensure all dependencies are installed: `pip install -r backend/requirements.txt`

**Port Already in Use?**
→ Change port: `--port 8001` (backend) or edit `vite.config.ts` (frontend)

## 📝 Environment Variables

Create `backend/.env` with:

```env
# Pinecone (Vector Database)
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=your-index
PINECONE_REGION=us-east-1

# Groq (LLM Provider)
GROQ_API_KEY=your-key
GROQ_MODEL=llama3-8b-8192

# Optional: OpenAI
OPENAI_API_KEY=your-key

# Optional: HuggingFace
HUGGINGFACE_API_KEY=your-key

# Server
PORT=8000
ENVIRONMENT=development

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🤝 Contributing

1. Create a feature branch
2. Make changes with clean, well-documented code
3. Run tests
4. Submit PR

## 📄 License

All rights reserved.

## 📞 Support

For issues, refer to documentation in `docs/` folder or check DEBUGGING_GUIDE.md for common problems.

---

**Last Updated:** February 5, 2026  
**Status:** ✅ Production Ready
