# 🎯 QUICK START - Run the Application

## ✨ Easiest Way (3 Steps)

### Step 1: Run Setup Script
**Windows (PowerShell):**
```powershell
.\setup.bat
```

**macOS/Linux (Terminal):**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies
- ✅ Install all frontend dependencies
- ✅ Display next steps

### Step 2: Start Backend (Terminal 1)
```bash
cd backend
.\.venv\Scripts\Activate.ps1      # Windows
source .venv/bin/activate           # macOS/Linux
uvicorn app.main:app --reload
```

**You should see:**
```
🚀 Starting application: AI Document Knowledge Base
📁 Database URL: sqlite:///./knowledge_base.db
✅ Database tables created successfully
👤 Admin user seeded successfully
INFO: Uvicorn running on http://0.0.0.0:8000
```

✅ Backend ready at: **http://localhost:8000**

### Step 3: Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

**You should see:**
```
  VITE v5.4.17  ready in 123 ms
  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

✅ Frontend ready at: **http://localhost:5173**

---

## 🔐 Login

Open http://localhost:5173 in your browser

**Admin Credentials:**
```
Email:    admin@company.com
Password: admin123
```

---

## ✅ Verify It Works

### ✓ Dashboard
You should see analytics dashboard with:
- Charts area (empty if no searches yet)
- Recent searches section

### ✓ Upload Document (Admin)
1. Click "Upload" tab
2. Select a PDF or TXT file
3. Enter title: "Test Document"
4. Click "Upload document"
5. Wait for success message

### ✓ Search
1. Click "Search" tab
2. Type: "test"
3. Click "Search"
4. You should see your document in results

### ✓ Search History
1. Click "History" tab
2. You should see your recent search

---

## 🆘 Having Issues?

### Backend won't start?
```bash
# Make sure virtual environment is activated
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# Try installing dependencies again
pip install -r requirements.txt
```

### Frontend won't start?
```bash
cd frontend
npm install
npm run dev
```

### Can't connect to backend?
1. Verify backend is running (Terminal 1)
2. Check backend shows "INFO: Uvicorn running on http://0.0.0.0:8000"
3. Try opening http://localhost:8000/api/v1/health in browser
4. Should show: `{"status":"ok"}`

### Port already in use?
**Backend (8000):**
```bash
uvicorn app.main:app --reload --port 8001
```

**Frontend (5173):**
```bash
npm run dev -- --port 5174
```

---

## 📊 What Each Page Does

### Dashboard
- Shows analytics and trends
- Most searched queries
- Top documents
- Recent searches

### Search
- Search your documents with AI
- Filter by source and department
- Adjust relevance score
- See snippets and scores

### History
- View your last 10 searches
- See timestamps
- Search history tracking

### Upload (Admin Only)
- Upload PDF/TXT files
- Extract and process automatically
- Generate AI embeddings
- Manage uploaded documents

---

## 📁 Files to Know

```
backend/.env           # Backend configuration (database, JWT, etc)
frontend/.env          # Frontend configuration (API URL)
backend/knowledge_base.db  # SQLite database (created automatically)
backend/.chroma/       # AI embeddings storage (created automatically)
```

---

## 🔧 Configuration

### Use PostgreSQL (Optional)
Edit `backend/.env`:
```
USE_POSTGRESQL=true
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=knowledge_base
```

Then ensure PostgreSQL is installed and database created:
```bash
createdb knowledge_base
```

Otherwise, SQLite is used automatically (no setup needed).

---

## 📚 API Documentation

**Swagger UI (Auto-generated):**
http://localhost:8000/docs

**Health Check:**
```bash
curl http://localhost:8000/api/v1/health
# Response: {"status":"ok"}
```

---

## 🎓 Example Workflow

1. **Start both servers** (Steps 1-3 above)
2. **Login** with admin@company.com / admin123
3. **Create a test document:**
   - Go to Upload
   - Create a text file with: "The vacation policy allows 20 days per year"
   - Upload with title "Vacation Policy"
4. **Search:**
   - Go to Search
   - Type: "How many vacation days?"
   - Click Search
   - See your document as result
5. **Check analytics:**
   - Go to Dashboard
   - See your search in "Most Searched" and document in "Top Documents"

---

## 🚀 Next Steps

1. **Upload more documents** to build your knowledge base
2. **Invite employees** by creating their accounts
3. **Test searches** with different queries
4. **Check analytics** to see what documents are useful
5. **Deploy to production** when ready

---

## 📖 Full Documentation

See **SETUP_GUIDE.md** for:
- Detailed setup instructions
- Comprehensive troubleshooting
- API endpoint reference
- Project structure
- Deployment guide

---

## 💡 Tips

- Start with 5-10 documents to build initial knowledge base
- Upload high-quality PDFs for best text extraction
- Test searches with natural language questions
- Archives get better with more documents
- Share search analytics with team

---

## 🎉 You're Ready!

Your AI-Powered Document Knowledge Base is now running!

**Happy documenting! 📚**
