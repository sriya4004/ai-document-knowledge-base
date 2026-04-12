# 🚀 AI-Powered Document Knowledge Base

**Production-ready full-stack knowledge base with role-based access, semantic search, and analytics.**

Runs locally without Docker by default using SQLite + local Chroma persistence.

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Node.js](https://img.shields.io/badge/Node.js-18+-green)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 🎯 Features

### Authentication & Security
- ✅ JWT token-based authentication
- ✅ Role-based access control (Admin, Employee)
- ✅ Department-level access isolation
- ✅ Bcrypt password hashing
- ✅ Default admin seeding

### Document Management
- ✅ Admin-only document upload
- ✅ PDF & TXT file support
- ✅ Automatic text extraction & chunking
- ✅ Semantic embedding generation
- ✅ Document versioning & updates
- ✅ Bulk operations support

### Search & Retrieval
- ✅ AI-powered semantic search
- ✅ Department-filtered results
- ✅ Relevance scoring
- ✅ Top-K result retrieval
- ✅ Source snippet preview
- ✅ Advanced filtering

### Analytics & Tracking
- ✅ Search history tracking
- ✅ Dashboard analytics
- ✅ Most searched queries chart
- ✅ Top documents chart
- ✅ Usage trends

### User Interface
- ✅ Modern SaaS-style design
- ✅ Responsive layout with sidebar
- ✅ Real-time loading states
- ✅ Toast notifications
- ✅ Empty states
- ✅ Dark mode support ready

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** SQLite (local) / PostgreSQL (production)
- **Vector DB:** ChromaDB
- **Auth:** JWT + bcrypt
- **Embeddings:** Sentence Transformers
- **ORM:** SQLAlchemy

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **State Management:** React Context API
- **UI Components:** Custom + Lucide Icons

---

## 📋 Quick Start

### Automatic Setup

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend starts at: **http://localhost:8000**

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend available at: **http://localhost:5173**

### Login Credentials
```
Email:    admin@company.com
Password: admin123
```

---

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── core/              # Configuration & security
│   │   ├── db/                # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routers/           # API endpoints
│   │   ├── schemas/           # Pydantic models
│   │   ├── services/          # Business logic
│   │   ├── dependencies/      # Auth & dependencies
│   │   └── main.py            # FastAPI app
│   ├── .env                   # Configuration
│   ├── requirements.txt       # Dependencies
│   └── .venv/                 # Virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── context/           # React context
│   │   ├── types/             # TypeScript types
│   │   ├── utils/             # Utilities
│   │   ├── App.tsx            # Root component
│   │   └── main.tsx           # Entry point
│   ├── .env                   # Configuration
│   ├── package.json           # Dependencies
│   └── tailwind.config.js     # Tailwind config
│
├── SETUP_GUIDE.md             # Detailed setup guide
├── setup.bat / setup.sh       # Quick setup scripts
└── docker-compose.yml         # Docker setup (optional)
```

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/v1/auth/login          # Get access token
GET    /api/v1/auth/me             # Get current user
```

### Documents
```
POST   /api/v1/documents/upload    # Upload PDF/TXT (admin)
GET    /api/v1/documents/          # List documents
PUT    /api/v1/documents/{id}      # Update document (admin)
DELETE /api/v1/documents/{id}      # Delete document (admin)
```

### Search
```
POST   /api/v1/query/              # Semantic search
GET    /api/v1/query/history       # Get search history
GET    /api/v1/query/analytics     # Get dashboard analytics
```

### Health
```
GET    /api/v1/health              # Health check
```

---

## 🔧 Environment Configuration

### Backend (.env)

```env
# App Settings
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Database (SQLite by default, PostgreSQL optional)
USE_POSTGRESQL=false
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=knowledge_base

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./.chroma
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# JWT
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Admin Seed
SEED_ADMIN_EMAIL=admin@company.com
SEED_ADMIN_PASSWORD=admin123
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 🧪 Testing the Application

### 1. Login
Navigate to http://localhost:5173 and login with admin credentials.

### 2. Upload Document (Admin)
- Go to **Upload** tab
- Select a PDF or TXT file
- Fill in title and category
- Click "Upload document"

### 3. Search
- Go to **Search** tab
- Enter your question: *"What is the vacation policy?"*
- Adjust top results (1-5)
- Click "Search"

### 4. View Dashboard
- Go to **Dashboard** tab
- See charts for most searched queries and top documents
- Check recent searches

### 5. View History
- Go to **History** tab
- See your last 10 searches with timestamps

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend connection failed | Verify backend running on port 8000, check `.env` CORS settings |
| Module not found errors | Run `pip install -r requirements.txt` (backend) or `npm install` (frontend) |
| Database errors | Delete `knowledge_base.db` and restart, or reconfigure `.env` for PostgreSQL |
| Port already in use | Change port: backend `--port 8001` or frontend `--port 5174` |
| Embeddings not generating | Check ChromaDB directory exists, verify model download |

See **SETUP_GUIDE.md** for detailed troubleshooting.

---

## 📊 Dashboard

The dashboard displays real-time analytics:

- **Most Searched Queries** - Top 5 frequently asked questions
- **Top Documents** - Most referenced knowledge assets
- **Recent Searches** - Your last 10 queries with timestamps

---

## 🚀 Deployment

### Production Checklist
- [ ] Set `APP_ENV=production`
- [ ] Use PostgreSQL database
- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Update `ALLOWED_ORIGINS` with production URL
- [ ] Run `npm run build` for frontend
- [ ] Use `gunicorn` for backend
- [ ] Set up HTTPS/SSL
- [ ] Configure environment variables securely

See **DEPLOY_AZURE.md** for Azure deployment.

---

## 📝 Logging

The application includes comprehensive logging:

**Backend Logs:**
```
🚀 Starting application
📁 Database URL: sqlite:///./knowledge_base.db
📦 Loading embedding model
✅ Database tables created successfully
📤 Uploading file: document.pdf
🔍 Processing query: "What is..."
```

Check backend terminal output for real-time logs.

---

## 🔒 Security

- JWT tokens expire after 60 minutes (configurable)
- Passwords hashed with bcrypt
- Department-based access control
- Admin-only endpoints protected
- CORS middleware configured
- Environment variables for secrets

---

## 📚 Documentation

- **SETUP_GUIDE.md** - Detailed setup and configuration
- **DEPLOY_AZURE.md** - Azure deployment instructions
- **API docs** - Available at `http://localhost:8000/docs` (Swagger UI)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 💡 Tips & Tricks

### Admin Features
- Admins see all documents and search analytics
- Upload and manage documents
- Track all user searches

### Employee Features
- Search company documents
- See only their department's documents
- View personal search history

### Performance Tips
- Use top_k=5 for best results
- Keep document titles descriptive
- Upload high-quality PDF/TXT files
- Monitor ChromaDB directory size

---

## 🎓 Example Workflows

### Workflow 1: Create Knowledge Base
1. Login as admin
2. Upload 5-10 key company documents
3. Wait for embeddings to generate
4. Test search with various queries

### Workflow 2: Run Audit
1. View Dashboard analytics
2. Check most searched queries
3. Identify documentation gaps
4. Upload missing documents

### Workflow 3: Department Isolation
1. Create user accounts per department
2. Upload department-specific documents
3. Users only see their department's docs
4. Analytics filtered by department

---

## 🆘 Support

For help:
1. Check **SETUP_GUIDE.md** troubleshooting section
2. Review backend logs in terminal
3. Open browser DevTools (F12) → Network tab
4. Search existing issues

---

**Built with ❤️ for better document management**

.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Backend URL: `http://127.0.0.1:8000`
Swagger: `http://127.0.0.1:8000/docs`

### 2) Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend URL: `http://localhost:5173`

## Environment Variables

### Backend (`backend/.env`)

- `DATABASE_URL` (optional; overrides local Postgres fields)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALLOWED_ORIGINS`
- `CHROMA_HOST`, `CHROMA_PORT`, `CHROMA_COLLECTION_NAME`
- `EMBEDDING_MODEL_NAME`
- `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD`, `SEED_ADMIN_DEPARTMENT`

### Frontend (`frontend/.env`)

- `VITE_API_BASE_URL=http://localhost:8000/api/v1`

## Docker (Optional)

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- ChromaDB: `localhost:8001`

## Azure Deployment

See [DEPLOY_AZURE.md](DEPLOY_AZURE.md) for:
- Backend on Azure App Service
- Frontend on Azure Static Web Apps
- Azure Database for PostgreSQL setup

## Screenshots

- Login Page: add `docs/screenshots/login.png`
- Dashboard: add `docs/screenshots/dashboard.png`
- Search: add `docs/screenshots/search.png`
- Upload: add `docs/screenshots/upload.png`
"update" 
