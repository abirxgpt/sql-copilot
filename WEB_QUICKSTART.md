# Web Interface Quick Start

## 🚀 Running the Web Interface

### Prerequisites
- Python 3.12+ with virtual environment activated
- Node.js 18+ and npm
- Ollama running with models installed

### Step 1: Start the Backend (FastAPI)

```bash
cd c:\Users\abirg\.gemini\antigravity\scratch\sql_project

# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Install FastAPI dependencies (if not already installed)
pip install fastapi uvicorn websockets

# Start the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Step 2: Start the Frontend (React)

Open a **new terminal** and run:

```bash
cd c:\Users\abirg\.gemini\antigravity\scratch\sql_project\frontend

# Install dependencies (first time only)
npm install

# Start the React development server
npm start
```

The web interface will open at: `http://localhost:3000`

---

## 🎯 Using the Web Interface

### 1. Ask Questions
Type natural language questions in the input box:
- "Show me top 10 customers by total spending"
- "Which products have low stock?"
- "What are the most popular products?"

### 2. Review Generated SQL
The SQL query will appear in the Monaco editor below.

### 3. Execute Query
Click "Execute" to run the query and see results in a table.

### 4. Explore Schema
Use the left sidebar to browse database tables, columns, and relationships.

---

## 📊 API Endpoints

### Query Endpoints
- `POST /api/v1/query/nl2sql` - Convert natural language to SQL
- `POST /api/v1/query/execute` - Execute SQL query
- `POST /api/v1/query/validate` - Validate SQL query
- `POST /api/v1/query/explain` - Explain SQL query

### Schema Endpoints
- `GET /api/v1/schema` - Get all tables
- `GET /api/v1/schema/{table_name}` - Get specific table details

### WebSocket
- `WS /ws/query` - Real-time query execution

### API Documentation
Visit: `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

---

## 🔧 Configuration

### Backend (.env)
```bash
# API runs on port 8000 by default
# Configure in api/main.py if needed
```

### Frontend
Create `frontend/.env`:
```
REACT_APP_API_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### Backend Issues

**Error: "Module 'fastapi' not found"**
```bash
pip install fastapi uvicorn websockets
```

**Error: "Port 8000 already in use"**
```bash
# Change port in api/main.py or kill the process using port 8000
```

**Error: "Failed to initialize API"**
- Make sure database exists: `python main.py init`
- Make sure schema is indexed: `python main.py index-schema`
- Check Ollama is running: `ollama list`

### Frontend Issues

**Error: "npm: command not found"**
- Install Node.js from: https://nodejs.org/

**Error: "Failed to compile"**
```bash
# Delete node_modules and reinstall
cd frontend
rm -rf node_modules
npm install
```

**Error: "Network Error" when querying**
- Make sure backend is running on port 8000
- Check CORS settings in api/main.py

---

## 🎨 Features

### Current Features
- ✅ Natural language to SQL conversion
- ✅ SQL editor with syntax highlighting
- ✅ Query execution and results display
- ✅ Schema browser
- ✅ Query explanation
- ✅ RAG-powered table retrieval

### Coming Soon
- [ ] Query history
- [ ] Saved queries
- [ ] Result export (CSV, JSON)
- [ ] Data visualization (charts)
- [ ] Dark mode
- [ ] Multi-database connections

---

## 📱 Screenshots

### Main Interface
```
┌─────────────────────────────────────────────┐
│  🤖 SQL Copilot                             │
│  Ask questions in natural language...       │
└─────────────────────────────────────────────┘

┌──────────┐  ┌──────────────────────────────┐
│ Schema   │  │ Ask a Question               │
│ Explorer │  │ ┌──────────────────────────┐ │
│          │  │ │ Show me top customers... │ │
│ ▼ Tables │  │ └──────────────────────────┘ │
│   customers│ │ [Convert to SQL]            │
│   orders  │  │                              │
│   products│  │ SQL Query                    │
│          │  │ ┌──────────────────────────┐ │
│          │  │ │ SELECT * FROM customers  │ │
│          │  │ │ ORDER BY total_spent DESC│ │
│          │  │ └──────────────────────────┘ │
│          │  │ [Execute] [Explain]          │
│          │  │                              │
│          │  │ Results (10 rows)            │
│          │  │ ┌──────────────────────────┐ │
│          │  │ │ ID │ Name  │ Total Spent │ │
│          │  │ │ 1  │ John  │ $5,234.00   │ │
│          │  │ └──────────────────────────┘ │
└──────────┘  └──────────────────────────────┘
```

---

## 🚀 Production Deployment

### Using Docker (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_PATH=/data/ecommerce.db
    volumes:
      - ./data:/data

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

Then run:
```bash
docker-compose up -d
```

---

## ✅ Success!

You now have a fully functional web interface for SQL Copilot! 🎉

Access it at: **http://localhost:3000**
