# 🤖 SQL Copilot

> Transform natural language into SQL queries using local AI - No API keys required!

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

SQL Copilot is a production-ready application that converts natural language questions into SQL queries using **local AI models** (Ollama + Qwen2.5-Coder). Features include intelligent schema retrieval (RAG), query explanation, error correction, data visualization, and a beautiful web interface.

<img width="1890" height="945" alt="image" src="https://github.com/user-attachments/assets/532ec0f8-7cf1-45bb-88c5-f46e1c8c07cd" />


## ✨ Features

### 🎯 Core Features
- **Natural Language to SQL** - Ask questions in plain English
- **Schema-Aware RAG** - Intelligently retrieves only relevant tables (50% faster)
- **Query Validation** - Multi-layer safety checks
- **Query Explanation** - Understand what the SQL does
- **Error Correction** - Automatic SQL error fixing
- **Local AI** - Runs completely offline with Ollama

### 🎨 Web Interface
- **Modern UI** - Built with React + Material-UI
- **Dark Mode** - Professional dark theme
- **Query History** - Save and favorite queries
- **Data Visualization** - Bar, Line, and Pie charts
- **Export Results** - CSV, JSON, or clipboard
- **Performance Metrics** - Real-time execution stats
- **SQL Formatting** - Auto-beautify SQL code

### 🚀 Advanced Features
- **CLI Interface** - Full-featured command-line tool
- **RESTful API** - FastAPI backend with 8 endpoints
- **WebSocket Support** - Real-time query execution
- **Comprehensive Logging** - Debug-friendly logs
- **Sample Database** - E-commerce dataset included

---

## 📸 Screenshots

### Web Interface
<img width="1183" height="850" alt="image" src="https://github.com/user-attachments/assets/ca69a87b-003c-41cb-8e56-972a10cd5fdc" />

### Data Visualization
<img width="1152" height="927" alt="image" src="https://github.com/user-attachments/assets/3158aeed-e4c7-46af-ae0c-40e2e269357d" />
<img width="1145" height="918" alt="image" src="https://github.com/user-attachments/assets/e50423f4-d804-43e5-bded-2359c1191e07" />


### Dark Mode
<img width="1591" height="744" alt="image" src="https://github.com/user-attachments/assets/02363958-1054-4b71-afba-343584286601" />

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Ollama ([Download](https://ollama.com/download))

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/sql-copilot.git
cd sql-copilot
```

### 2. Install Ollama Models
```bash
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

### 3. Backend Setup
```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Initialize database
python main.py init

# Index schema for RAG
python main.py index-schema
```

### 4. Frontend Setup
```bash
cd frontend
npm install
```

### 5. Run Application

**Terminal 1 - Backend:**
```bash
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Open**: http://localhost:3000

---

## 📖 Usage

### Web Interface

1. **Ask a Question**
   ```
   Show me top 10 customers by total spending
   ```

2. **Review Generated SQL**
   ```sql
   SELECT c.id, c.name, SUM(o.total_amount) as total_spent
   FROM customers c
   JOIN orders o ON c.id = o.customer_id
   GROUP BY c.id, c.name
   ORDER BY total_spent DESC
   LIMIT 10;
   ```

3. **Execute & Visualize**
   - Click "Execute" to run query
   - Toggle to "Chart" view
   - Export results as CSV/JSON

### CLI Interface

```bash
# Interactive mode
python main.py interactive

# Single query
python main.py query "Show me top customers"

# View schema
python main.py schema

# Explain SQL
python main.py explain "SELECT * FROM customers"
```

### API Endpoints

```bash
# Convert NL to SQL
curl -X POST http://localhost:8000/api/v1/query/nl2sql \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me top customers"}'

# Execute SQL
curl -X POST http://localhost:8000/api/v1/query/execute \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM customers LIMIT 10"}'

# Get schema
curl http://localhost:8000/api/v1/schema
```

**API Documentation**: http://localhost:8000/docs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      React Frontend (Port 3000)     │
│  Material-UI + Monaco Editor        │
└──────────────┬──────────────────────┘
               │ HTTP/WebSocket
┌──────────────▼──────────────────────┐
│     FastAPI Backend (Port 8000)     │
│  NL2SQL │ Validator │ Explainer     │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼──┐  ┌────▼────┐
│ Ollama│  │ SQL │  │ ChromaDB│
│  LLM  │  │ DB  │  │   RAG   │
└───────┘  └─────┘  └─────────┘
```

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- Ollama - Local LLM inference
- ChromaDB - Vector database for RAG
- SQLAlchemy - Database ORM
- Pydantic - Data validation

**Frontend:**
- React 18 - UI framework
- Material-UI - Component library
- Monaco Editor - Code editor (VS Code)
- Recharts - Data visualization
- Axios - HTTP client

**AI Models:**
- Qwen2.5-Coder:7B - SQL generation
- nomic-embed-text - Embeddings for RAG

---

## 📂 Project Structure

```
sql-copilot/
├── api/                    # FastAPI backend
│   ├── main.py            # API server
│   └── __init__.py
├── config/                 # Configuration
│   └── settings.py        # Pydantic settings
├── core/                   # Core logic
│   ├── nl2sql.py          # NL to SQL converter
│   ├── validator.py       # Query validator
│   ├── explainer.py       # Query explainer
│   └── error_corrector.py # Error correction
├── database/               # Database layer
│   ├── connection.py      # DB connection
│   └── schema_manager.py  # Schema management
├── rag/                    # RAG system
│   ├── schema_indexer.py  # Vector indexing
│   └── retriever.py       # Semantic search
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js         # Main component
│   │   └── components/    # UI components
│   ├── public/
│   └── package.json
├── scripts/                # Utility scripts
│   └── create_sample_db.py
├── data/                   # Data files
│   └── ecommerce.db       # Sample database
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_PATH=data/ecommerce.db

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/sql_copilot.log

# LLM (Ollama)
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434
LLM_TEMPERATURE=0.1

# RAG
RAG_ENABLED=true
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.3
EMBEDDING_MODEL=nomic-embed-text
VECTOR_DB_PATH=data/chroma_db

# Query Settings
MAX_QUERY_TIMEOUT=30
MAX_RESULT_ROWS=1000
ENABLE_DANGEROUS_QUERIES=false
```

---

## 🎯 Performance

### Benchmarks

| Metric | Without RAG | With RAG | Improvement |
|--------|-------------|----------|-------------|
| Query Time | 4.2s | 2.1s | **50% faster** |
| Token Usage | 1200 | 450 | **62% reduction** |
| Context Size | 4305 chars | 1580 chars | **63% smaller** |
| Accuracy | 95% | 100% | **5% better** |

### Hardware Requirements

**Minimum:**
- 8GB RAM
- CPU only
- 10GB disk space

**Recommended:**
- 16GB RAM
- NVIDIA GPU (8GB+ VRAM)
- 20GB disk space

---

## 🧪 Testing

```bash
# Run tests
pytest

# Test CLI
python main.py query "Show me top 5 customers"

# Test API
curl http://localhost:8000/health
```

---

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Web Interface Guide](WEB_QUICKSTART.md)
- [Ollama Setup](OLLAMA_SETUP.md)
- [RAG Implementation](docs/rag_implementation.md)
- [API Documentation](http://localhost:8000/docs)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Troubleshooting

### Backend Issues

**Error: "Module not found"**
```bash
pip install -r requirements.txt
```

**Error: "Ollama connection refused"**
```bash
# Make sure Ollama is running
ollama serve
```

**Error: "Schema not indexed"**
```bash
python main.py index-schema
```

### Frontend Issues

**Error: "npm not found"**
- Install Node.js from https://nodejs.org/

**Error: "Network Error"**
- Ensure backend is running on port 8000
- Check CORS settings in `api/main.py`

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.com/) - Local LLM inference
- [Qwen2.5-Coder](https://github.com/QwenLM/Qwen2.5-Coder) - Code generation model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python framework
- [React](https://reactjs.org/) - UI framework
- [Material-UI](https://mui.com/) - Component library

---

## 📧 Contact

Your Name - [@wannabiryours](https://instagram.com/wannabiryours)

Project Link: [https://github.com/abirxgpt/sql-copilot](https://github.com/abirxgpt/sql-copilot)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=abirxgpt/sql-copilot&type=Date)](https://star-history.com/#abirxgpt/sql-copilot&Date)

---

**Made with ❤️ by CHRE/Abir**
