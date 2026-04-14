# 🚀 AI-Powered Document Knowledge Base - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Running the Application](#running-the-application)
5. [Testing the Application](#testing-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Project Structure](#project-structure)

---

## Prerequisites

### Required Software
- **Python 3.11+** - For backend
- **Node.js 18+** & **npm 9+** - For frontend
- **Git** - For version control

### Recommended Tools
- **VS Code** with Python & Thunder Client extensions
- **Postman** - For API testing
- **PostgreSQL 13+** (Optional) - For production use

---

## Backend Setup

### Step 1: Create Python Virtual Environment

```bash
cd backend
python -m venv .venv
```

**Activate Virtual Environment:**
- Windows PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- Windows CMD:
  ```cmd
  .venv\Scripts\activate.bat
  ```
- macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment

The `.env` file is already configured with SQLite (default). To use PostgreSQL:

1. **For SQLite (Default - No setup needed):**
   - The `.env` already uses SQLite
   - Database will be created at `backend/knowledge_base.db`

2. **For PostgreSQL (Optional):**
   - Install PostgreSQL on your system
   - Create a database: `createdb knowledge_base`
   - Update `.env`:
     ```
     USE_POSTGRESQL=true
     POSTGRES_USER=postgres
     POSTGRES_PASSWORD=your_password
     POSTGRES_HOST=localhost
     POSTGRES_PORT=5432
     POSTGRES_DB=knowledge_base
     ```

### Step 4: Verify Backend Configuration

Check that `.env` contains:
```
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000
USE_POSTGRESQL=false
CHROMA_PERSIST_DIRECTORY=./.chroma
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

---

## Frontend Setup

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Verify Environment Configuration

Check `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Running the Application

### Backend Server

From `backend` directory (with virtual environment activated):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Frontend Development Server

From `frontend` directory:

```bash
npm run dev
```

**Expected Output:**
```
  VITE v5.4.17  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

---

## Testing the Application

### 1. Access the Application

Open your browser and navigate to: **http://localhost:5173**

### 2. Login

Use the default admin credentials:
- **Email:** admin@company.com
- **Password:** admin123

You should see the Dashboard after successful login.

### 3. Dashboard

The dashboard displays:
- 📊 **Most Searched Queries** - Bar chart of top 5 queries
- 📄 **Top Documents** - Most referenced documents
- 🔍 **Recent Searches** - Your last 10 searches

### 4. Upload Documents (Admin Only)

Navigate to **Upload** tab (visible only for admins):

- **Upload a PDF/TXT file:**
  1. Enter a title (e.g., "Company Policy 2024")
  2. Select category (e.g., "policy")
  3. Click "Upload document"
  4. Wait for processing and embeddings creation

- **Manage Uploaded Documents:**
  - Edit title, category, or source
  - Click "Save" to update
  - Click "Delete" to remove

### 5. Search Documents

Navigate to **Search** tab:

- **Basic Search:**
  1. Enter your question: "What is the vacation policy?"
  2. Adjust "Top results" (1-5)
  3. Click "Search"

- **Advanced Filtering:**
  - Filter by source (e.g., "policy", "wiki")
  - Filter by department (e.g., "hr", "finance")
  - Set minimum relevance score (0.0-1.0)

### 6. View Search History

Navigate to **History** tab to see your previous 10 searches with timestamps.

---

## API Endpoints Reference

All endpoints require authentication with JWT Bearer token.

### Authentication
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info

### Documents
- `POST /api/v1/documents/upload` - Upload PDF/TXT (admin only)
- `GET /api/v1/documents/` - List all documents
- `PUT /api/v1/documents/{id}` - Update document (admin only)
- `DELETE /api/v1/documents/{id}` - Delete document (admin only)

### Search & Query
- `POST /api/v1/query/` - Semantic search
- `GET /api/v1/query/history` - Get search history
- `GET /api/v1/query/analytics` - Get dashboard analytics

### Health
- `GET /api/v1/health` - Health check

---

## Troubleshooting

### Issue: "Unable to connect to backend"

**Solution:**
1. Verify backend is running on http://localhost:8000
2. Check CORS settings in `.env`: `ALLOWED_ORIGINS=http://localhost:5173`
3. Check browser console for actual error message

### Issue: "Module not found" or import errors

**Backend:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Frontend:**
```bash
npm install
npm cache clean --force
rm -rf node_modules
npm install
```

### Issue: Database connection error

**For SQLite:**
- Delete `backend/knowledge_base.db` and restart - it will be recreated

**For PostgreSQL:**
- Verify PostgreSQL is running: `psql --version`
- Check connection: `psql -U postgres -d knowledge_base`
- Update `.env` with correct credentials

### Issue: Embeddings not generated for documents

**Solution:**
1. Verify ChromaDB is accessible at `http://localhost:8001` (if using HTTP)
2. Check `backend/.chroma` directory exists
3. Check backend logs for embedding model download progress
4. Re-upload the document

### Issue: "No recent searches" on Dashboard

**Solution:**
- Dashboard shows searches from the current user only
- Regular employees see only their searches
- Admin sees all users' searches (if viewing as admin)

### Issue: Port 8000 or 5173 already in use

**For Backend (8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

**For Frontend (5173):**
```bash
# Use different port
npm run dev -- --port 5174
```

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Configuration & settings
│   │   │   └── security.py        # JWT & password utilities
│   │   ├── db/
│   │   │   └── session.py         # Database connection
│   │   ├── models/
│   │   │   ├── user.py            # User model
│   │   │   ├── document.py        # Document model
│   │   │   ├── chunk.py           # Document chunks
│   │   │   └── search_history.py  # Search history
│   │   ├── routers/
│   │   │   ├── auth.py            # Auth endpoints
│   │   │   ├── documents.py       # Document endpoints
│   │   │   ├── query.py           # Search endpoints
│   │   │   └── health.py          # Health check
│   │   ├── schemas/
│   │   │   ├── auth.py            # Auth Pydantic models
│   │   │   ├── document.py        # Document models
│   │   │   └── query.py           # Query models
│   │   ├── services/
│   │   │   ├── embeddings.py      # Embedding generation
│   │   │   ├── retrieval.py       # Semantic search
│   │   │   ├── ingestion.py       # Document processing
│   │   │   └── seed.py            # Seed default admin
│   │   ├── dependencies/
│   │   │   └── auth.py            # Auth dependencies
│   │   └── main.py                # FastAPI application
│   ├── .env                       # Environment variables
│   ├── requirements.txt           # Python dependencies
│   └── .venv/                     # Virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.tsx         # Main layout with sidebar
│   │   │   ├── SearchBar.tsx      # Search input component
│   │   │   ├── SearchResults.tsx  # Results display
│   │   │   ├── auth/
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   └── ui/
│   │   │       ├── Button.tsx
│   │   │       ├── Card.tsx
│   │   │       ├── Input.tsx
│   │   │       ├── EmptyState.tsx
│   │   │       └── Skeleton.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx      # Login form
│   │   │   ├── DashboardPage.tsx  # Dashboard & analytics
│   │   │   ├── SearchPage.tsx     # Search interface
│   │   │   ├── HistoryPage.tsx    # Search history
│   │   │   ├── UploadPage.tsx     # Document upload (admin)
│   │   │   └── DocumentsPage.tsx  # Document list
│   │   ├── services/
│   │   │   ├── apiClient.ts       # Axios configuration
│   │   │   ├── authService.ts     # Auth API calls
│   │   │   ├── documentService.ts  # Document API calls
│   │   │   └── searchService.ts   # Search API calls
│   │   ├── context/
│   │   │   └── AuthContext.tsx    # Auth state management
│   │   ├── types/
│   │   │   └── index.ts           # TypeScript types
│   │   ├── utils/
│   │   │   └── auth.ts            # Token management
│   │   ├── App.tsx                # Root component
│   │   ├── main.tsx               # React entry point
│   │   └── styles.css             # Global styles
│   ├── .env                       # Frontend env vars
│   ├── package.json               # Dependencies
│   ├── tsconfig.json              # TypeScript config
│   ├── vite.config.ts             # Vite config
│   └── tailwind.config.js         # Tailwind CSS config
│
├── README.md                      # Project README
└── docker-compose.yml             # Docker Compose setup
```

---

## Features Implemented

✅ **Authentication**
- JWT token-based auth
- Admin & employee roles
- Department-based access control

✅ **Document Management**
- Upload PDF/TXT files
- Extract & store text content
- Generate semantic embeddings
- Full-text search on chunks

✅ **Semantic Search**
- AI-powered document retrieval
- Relevance scoring
- Department filtering
- Top K results

✅ **Dashboard Analytics**
- Most searched queries
- Top referenced documents
- Recent search history
- Usage trends

✅ **Modern UI**
- Responsive design with Tailwind CSS
- Loading states & animations
- Toast notifications
- Empty states
- Skeleton loaders

---

## Next Steps

1. **Deploy to Production:**
   - Use PostgreSQL for production database
   - Set up environment variables securely
   - Use production-grade server (gunicorn)
   - Configure HTTPS

2. **Add Features:**
   - Export search results to PDF
   - Advanced filters & faceted search
   - Document versioning
   - Access control per document
   - Document tagging/annotations

3. **Performance:**
   - Implement caching
   - Batch document processing
   - Optimize embedding generation
   - Add query caching

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review backend logs: Check console output when server starts
3. Check browser console: Press F12 in browser
4. Check network tab: Look at actual API responses

---

