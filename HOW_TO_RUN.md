# 🚀 How to Run SQL Copilot Web Interface

## Quick Start (3 Simple Steps)

### Step 1: Start the Backend Server

Open **PowerShell** in your project folder:

```powershell
cd C:\Users\abirg\.gemini\antigravity\scratch\sql_project

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the API server
uvicorn api.main:app --reload --port 8000
```

✅ **You should see**: "Application startup complete"
✅ **Backend running at**: http://localhost:8000

**Keep this terminal open!**

---

### Step 2: Start the Frontend

Open a **NEW PowerShell window**:

```powershell
cd C:\Users\abirg\.gemini\antigravity\scratch\sql_project\frontend

# Start React
npm start
```

✅ **Browser will open automatically** at http://localhost:3000
✅ **If not, manually open**: http://localhost:3000

**Keep this terminal open too!**

---

### Step 3: Use the Web Interface!

1. **Type a question** in the text box:
   ```
   Show me top 10 customers by total spending
   ```

2. **Click "Convert to SQL"** button

3. **Review the generated SQL** in the editor below

4. **Click "Execute"** to run the query

5. **See results** in the table!

---

## 🎯 Example Questions to Try

```
Show me top 10 customers by total spending
Which products have the highest ratings?
What are the most popular products?
Show me orders from last month
List all products with low stock
```

---

## 🛑 How to Stop

**To stop the servers**:
- Press `Ctrl+C` in both PowerShell windows

---

## 🐛 Troubleshooting

### Backend won't start?

**Error: "Port 8000 already in use"**
```powershell
# Kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

**Error: "Module not found"**
```powershell
pip install fastapi uvicorn websockets
```

### Frontend won't start?

**Error: "npm not found"**
- Install Node.js from: https://nodejs.org/

**Error: "Dependencies not installed"**
```powershell
cd frontend
npm install
```

### Can't connect to backend?

1. Make sure backend is running (check terminal 1)
2. Check http://localhost:8000/health in browser
3. Should show: `{"status":"healthy"}`

---

## 📊 What You'll See

### Main Interface

```
┌─────────────────────────────────────────┐
│  🤖 SQL Copilot                         │
│  Ask questions in natural language...   │
└─────────────────────────────────────────┘

Left Sidebar:          Main Area:
┌──────────────┐      ┌────────────────────┐
│ Database     │      │ Ask a Question     │
│ Schema       │      │ ┌────────────────┐ │
│              │      │ │ Your question  │ │
│ ▼ customers  │      │ └────────────────┘ │
│   - id       │      │ [Convert to SQL]   │
│   - name     │      │                    │
│   - email    │      │ SQL Query          │
│              │      │ ┌────────────────┐ │
│ ▼ orders     │      │ │ SELECT ...     │ │
│   - id       │      │ └────────────────┘ │
│   - customer │      │ [Execute]          │
│              │      │                    │
│ ▼ products   │      │ Results            │
│   - id       │      │ ┌────────────────┐ │
│   - name     │      │ │ Table data...  │ │
│   - price    │      │ └────────────────┘ │
└──────────────┘      └────────────────────┘
```

---

## ✅ Success Checklist

- [ ] Backend running (Terminal 1)
- [ ] Frontend running (Terminal 2)
- [ ] Browser opened to http://localhost:3000
- [ ] Can see SQL Copilot interface
- [ ] Can type questions
- [ ] Can see generated SQL
- [ ] Can execute queries
- [ ] Can see results

---

## 🎉 You're Ready!

The web interface is now running. Try asking questions in natural language and watch it generate SQL automatically!

**Need help?** Check the logs in both terminal windows for any errors.
