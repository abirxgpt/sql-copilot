# Quick Start Guide

## 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## 2. Set Up API Key

1. Get your Gemini API key from: https://makersuite.google.com/app/apikey
2. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## 3. Create Sample Database

```bash
python main.py init
```

## 4. Start Using SQL Copilot!

### Interactive Mode (Recommended)
```bash
python main.py interactive
```

### Single Query
```bash
python main.py query "Show me top 10 customers by total spending"
```

### With Explanation
```bash
python main.py query "What are the most popular products?" --explain
```

### Export Results
```bash
python main.py query "SELECT * FROM customers" --export results.csv
```

### Show Schema
```bash
python main.py schema
```

### Explain SQL
```bash
python main.py explain "SELECT * FROM orders WHERE status = 'pending'"
```

## Example Queries to Try

1. "Show me top 10 customers by total spending"
2. "What are the most popular products in Electronics category?"
3. "Show me orders from last month with status 'pending'"
4. "Which products have low stock (less than 10 units)?"
5. "Show me average rating for each product category"
6. "List customers who haven't placed any orders"
7. "What's the total revenue by month?"
8. "Show me products with ratings above 4 stars"

## Troubleshooting

### API Key Error
- Make sure you've set `GEMINI_API_KEY` in `.env` file
- Verify the key is correct (no extra spaces)

### Database Not Found
- Run `python main.py init` to create the sample database

### Module Not Found
- Make sure you've activated the virtual environment
- Run `pip install -r requirements.txt`

## Logs

All operations are logged to `logs/sql_copilot.log` for debugging.
