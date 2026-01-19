# SQL Copilot - Ollama Setup Guide

## 🚀 Now Using Local LLM (No API Keys Needed!)

I've switched the SQL Copilot to use **Ollama** with **Qwen2.5-Coder**, which runs completely locally on your machine. No more API limits or rate errors!

## 📋 Setup Steps

### 1. Install Ollama

Download and install Ollama from: https://ollama.com/download

**Windows**: Download the installer and run it.

### 2. Install Qwen2.5-Coder Model

Open a new terminal and run:
```bash
ollama pull qwen2.5-coder:7b
```

This will download the 7B parameter model (~4.7GB). It's optimized for code generation including SQL.

### 3. Start Ollama Server

Ollama should start automatically, but if not:
```bash
ollama serve
```

Keep this running in the background.

### 4. Install New Dependencies

```bash
cd c:\Users\abirg\.gemini\antigravity\scratch\sql_project
.\venv\Scripts\Activate.ps1
pip install ollama langchain-community
```

### 5. Test It!

```bash
python main.py interactive
```

Then try: "Show me top 5 customers"

## ✅ Advantages of Ollama

- ✅ **No API keys needed** - Everything runs locally
- ✅ **No rate limits** - Use as much as you want
- ✅ **No internet required** - Works offline
- ✅ **Free forever** - No costs
- ✅ **Privacy** - Your data never leaves your machine
- ✅ **Fast** - Local inference is quick

## 🎯 Recommended Models

### Qwen2.5-Coder:7B (Current - Recommended)
- **Size**: ~4.7GB
- **Speed**: Fast
- **Quality**: Excellent for SQL
- **Install**: `ollama pull qwen2.5-coder:7b`

### Alternative Models:

#### Smaller/Faster:
```bash
ollama pull qwen2.5-coder:3b  # Faster, less accurate
```

#### Larger/Better:
```bash
ollama pull qwen2.5-coder:14b  # Slower, more accurate
ollama pull qwen2.5-coder:32b  # Best quality, needs powerful GPU
```

#### Other Good Options:
```bash
ollama pull codellama:7b       # Meta's code model
ollama pull deepseek-coder:6.7b # Another excellent code model
```

## 🔧 Troubleshooting

### "Connection refused" error
- Make sure Ollama is running: `ollama serve`
- Check if it's listening on port 11434

### Model not found
- Pull the model first: `ollama pull qwen2.5-coder:7b`
- List installed models: `ollama list`

### Slow responses
- Use a smaller model: `qwen2.5-coder:3b`
- Or upgrade your hardware (GPU helps a lot)

### Out of memory
- Use a smaller model
- Close other applications
- Increase swap/virtual memory

## 📊 Performance Expectations

### With Qwen2.5-Coder:7B:
- **First query**: 5-15 seconds (model loading)
- **Subsequent queries**: 2-5 seconds
- **RAM usage**: ~6-8GB
- **GPU**: Optional but recommended for speed

### Hardware Requirements:
- **Minimum**: 8GB RAM, CPU only
- **Recommended**: 16GB RAM, any GPU
- **Optimal**: 32GB RAM, NVIDIA GPU with 8GB+ VRAM

## 🎨 Example Queries

Try these once Ollama is running:

1. "Show me top 10 customers by total spending"
2. "What are the most popular products?"
3. "Which products have low stock?"
4. "Show me orders from last month"
5. "What's the average rating by category?"

## 🔄 Switching Models

To use a different model, edit `.env`:
```
LLM_MODEL=codellama:7b
```

Then restart the copilot.

## 💡 Tips

1. **Keep Ollama running** in the background for faster responses
2. **First query is slow** - model needs to load into memory
3. **GPU acceleration** - Ollama automatically uses GPU if available
4. **Model stays in memory** - Subsequent queries are much faster

## 🆘 Need Help?

Check Ollama logs:
```bash
ollama list  # See installed models
ollama ps    # See running models
```

Check SQL Copilot logs:
```
logs/sql_copilot.log
```

---

**Ready to use!** Just make sure Ollama is running and the model is downloaded. 🚀
