# ✅ Complete Setup Verification Checklist

Use this checklist to verify your AI Document Knowledge Base is set up and working correctly.

## 📋 Pre-Flight Checks

### System Requirements
- [ ] Python 3.11 or higher installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm 9+ installed (`npm --version`)
- [ ] Git installed (optional, `git --version`)

### Repository
- [ ] Project folder exists at `Desktop/AI-Powered Document Knowledge Base`
- [ ] All files extracted correctly
- [ ] Permissions correct (no read-only errors)

---

## 🔧 Backend Setup

### Virtual Environment
- [ ] Virtual environment created: `backend/.venv` folder exists
- [ ] Virtual environment activated successfully
  - Windows PowerShell: `.\.venv\Scripts\Activate.ps1` works
  - Windows CMD: `.venv\Scripts\activate.bat` works
  - macOS/Linux: `source .venv/bin/activate` works

### Dependencies
- [ ] `pip install -r requirements.txt` completed successfully
- [ ] No installation errors or warnings
- [ ] Key packages installed:
  - [ ] fastapi
  - [ ] uvicorn
  - [ ] sqlalchemy
  - [ ] chromadb
  - [ ] sentence-transformers
  - [ ] python-jose
  - [ ] passlib

### Configuration
- [ ] `backend/.env` file exists
- [ ] `.env` contains required variables:
  - [ ] `APP_ENV=development`
  - [ ] `USE_POSTGRESQL=false`
  - [ ] `SEED_ADMIN_EMAIL=admin@company.com`
  - [ ] `SEED_ADMIN_PASSWORD=admin123`

### Database
- [ ] Can start backend without database errors
- [ ] `knowledge_base.db` created in `backend/` folder (after first start)
- [ ] No "database connection failed" errors

---

## 🌐 Frontend Setup

### Dependencies
- [ ] `npm install` completed successfully in `frontend/` folder
- [ ] No installation errors
- [ ] `frontend/node_modules` folder created
- [ ] `package.json` has correct dependencies:
  - [ ] react
  - [ ] react-dom
  - [ ] react-router-dom
  - [ ] axios
  - [ ] react-hot-toast
  - [ ] tailwindcss

### Configuration
- [ ] `frontend/.env` file exists
- [ ] `frontend/.env` contains:
  - [ ] `VITE_API_BASE_URL=http://localhost:8000/api/v1`

---

## 🚀 Running the Application

### Backend Server
- [ ] Backend starts with `uvicorn app.main:app --reload`
- [ ] No errors in console output
- [ ] Server listens on `http://localhost:8000`
- [ ] Startup logs show:
  - [ ] `🚀 Starting application: AI Document Knowledge Base`
  - [ ] `📁 Database URL: sqlite:///./knowledge_base.db`
  - [ ] `✅ Database tables created successfully`
  - [ ] `👤 Admin user seeded successfully`
  - [ ] `INFO: Uvicorn running on http://0.0.0.0:8000`

### Frontend Server
- [ ] Frontend starts with `npm run dev`
- [ ] No errors in console output
- [ ] Server listens on `http://localhost:5173`
- [ ] Output shows: `Local: http://localhost:5173/`
- [ ] Vite compilation successful

---

## 🌍 Browser Testing

### Access Application
- [ ] Open http://localhost:5173 in browser
- [ ] Page loads without errors
- [ ] No blank screen or 404 errors
- [ ] Login form displays correctly

### API Connectivity
- [ ] Open http://localhost:8000/docs in browser
- [ ] Swagger API documentation loads
- [ ] Can see endpoints list
- [ ] Health check endpoint shows: `{"status":"ok"}`

---

## 🔐 Authentication

### Login
- [ ] Click "Sign in" button (or already at login page)
- [ ] Enter email: `admin@company.com`
- [ ] Enter password: `admin123`
- [ ] Click "Sign in" button
- [ ] No "Invalid email or password" error
- [ ] Redirected to Dashboard

### Session
- [ ] Logged in user visible in sidebar (admin / general department)
- [ ] Can see navigation tabs: Dashboard, Search, History, Upload
- [ ] "Upload" tab visible (admin-only feature)
- [ ] Can click "Logout" button

---

## 📊 Dashboard Page

### Page Loads
- [ ] Dashboard tab opens without errors
- [ ] Page title shows: "Dashboard"
- [ ] Layout looks clean (sidebar on left, content on right)

### Components Visible
- [ ] "Most searched queries" card displays (may be empty or with data)
- [ ] "Top documents" card displays (may be empty or with data)
- [ ] "Recent searches" card displays (may be empty)
- [ ] Charts render without errors (may be blank if no data)

### Performance
- [ ] Page loads in < 3 seconds
- [ ] Skeleton loaders appear while loading
- [ ] No "Unable to load dashboard data" error message

---

## 🔍 Search Page

### Page Loads
- [ ] Search tab opens without errors
- [ ] "Semantic Search" page displays
- [ ] Search bar with input field visible

### Search Functionality
- [ ] Can type in search box
- [ ] Can adjust "Top results" slider (1-5)
- [ ] Filter fields visible:
  - [ ] Filter by source
  - [ ] Filter by department
  - [ ] Min relevance score
- [ ] "Search" button is clickable

### Search Results (if documents uploaded)
- [ ] Results display with document title
- [ ] Score shown (0.000 - 1.000)
- [ ] Content snippet visible
- [ ] Clicking card doesn't break anything

---

## 📤 Upload Page (Admin)

### Page Access
- [ ] Upload tab visible (admin-only)
- [ ] Can click on Upload tab
- [ ] Upload page loads correctly

### Upload Form
- [ ] Title input field visible
- [ ] Category dropdown/input visible
- [ ] Source input field visible
- [ ] File input visible with "Select file" button
- [ ] "Upload document" button visible

### File Upload
- [ ] Can select a PDF or TXT file
- [ ] File size and name display
- [ ] Click "Upload document" button
- [ ] See loading spinner
- [ ] Success message appears: "Document uploaded"
- [ ] No error messages

### Document Management
- [ ] Uploaded document appears in table
- [ ] Document row shows: Title, Category, Source
- [ ] Can edit fields in document row
- [ ] "Save" button saves changes
- [ ] "Delete" button removes document
- [ ] Success messages show for save/delete

---

## 📜 History Page

### Page Loads
- [ ] History tab opens without errors
- [ ] "Search History" page displays
- [ ] Page description visible

### History Display
- [ ] Recent searches list shows entries (if you've searched)
- [ ] Each entry shows query text
- [ ] Each entry shows timestamp
- [ ] Oldest entries are at bottom
- [ ] Limited to recent searches (not hundreds)

### No Data State
- [ ] If no searches yet, shows empty state
- [ ] Empty state shows icon and message
- [ ] Message indicates: "No recent searches"

---

## 🔌 API Endpoints (Optional Testing)

### Authentication
- [ ] `POST http://localhost:8000/api/v1/auth/login`
  - Body: `{"email":"admin@company.com","password":"admin123"}`
  - Response: `{"access_token":"...", "token_type":"bearer"}`
  - [ ] Can get valid token

### Documents
- [ ] `GET http://localhost:8000/api/v1/documents/`
  - Header: `Authorization: Bearer <token>`
  - Response: `[...]` (list of documents, may be empty)
  - [ ] Returns 200 OK

### Search
- [ ] `POST http://localhost:8000/api/v1/query/`
  - Body: `{"question":"test","top_k":5}`
  - Response: `{"answer":"...","sources":[...]}`
  - [ ] Returns 200 OK

### Health
- [ ] `GET http://localhost:8000/api/v1/health`
  - Response: `{"status":"ok"}`
  - [ ] Returns 200 OK

---

## 🎯 End-to-End Workflow

### Complete User Journey
- [ ] Login successfully
- [ ] See dashboard (analytics tab)
- [ ] Go to Upload tab
- [ ] Upload a test PDF or TXT file
- [ ] See "Document uploaded" success message
- [ ] Go to Search tab
- [ ] Search for keyword from document
- [ ] See document in search results
- [ ] Go to History tab
- [ ] See your search in history
- [ ] Go back to Dashboard
- [ ] See search in "Most searched" chart
- [ ] See document in "Top documents" chart
- [ ] Logout successfully

---

## 🆘 Troubleshooting & Fixes

### Issue: "Cannot connect to backend"
- [ ] Backend server running on correct port (8000)?
- [ ] Check browser console for actual error (F12)
- [ ] Verify https://localhost:8000/api/v1/health returns OK
- [ ] Check CORS configuration in backend/.env

### Issue: "Database error"
- [ ] Delete `backend/knowledge_base.db` (it will be recreated)
- [ ] Restart backend server
- [ ] Check backend logs for specific error

### Issue: "Module not found" errors
- [ ] Run `pip install --upgrade pip` (backend)
- [ ] Run `pip install -r requirements.txt` again (backend)
- [ ] Run `npm install` again (frontend)

### Issue: "Port already in use"
- [ ] Backend: Use `--port 8001` instead
- [ ] Frontend: Use `--port 5174` instead
- [ ] Or kill existing process using port

### Issue: Slow to respond or forever loading
- [ ] First embedding model load takes time (may take 5 minutes)
- [ ] Wait for console to show completion
- [ ] Subsequent searches should be fast

---

## 📝 Notes & Comments

### What was done:
```
1. Fixed database connection logic
2. Added comprehensive logging
3. Enhanced error handling
4. Created .env configuration
5. Added frontend/backend integration
6. Set up proper CORS
7. Created setup scripts
8. Written comprehensive documentation
```

### Verified working:
```
✓ Authentication & JWT tokens
✓ Document upload & processing
✓ Semantic search with embeddings
✓ Search history tracking
✓ Dashboard analytics
✓ Role-based access control
✓ Department-based filtering
✓ UI responsiveness
✓ Error handling & messages
✓ API integration
```

---

## 🎉 Success Criteria

Your setup is **COMPLETE and WORKING** when:
1. ✅ Backend starts with no errors
2. ✅ Frontend builds with no errors
3. ✅ Can login with admin credentials
4. ✅ Dashboard displays without errors
5. ✅ Can upload a document
6. ✅ Can search documents and get results
7. ✅ Search history tracks queries
8. ✅ Analytics display correctly
9. ✅ No console errors (check F12)
10. ✅ All tables/charts render properly

---

## 📞 Getting Help

If something doesn't work:
1. Check **SETUP_GUIDE.md** troubleshooting section
2. Review backend console logs (look for red text)
3. Open browser F12 Dev Tools → Console tab (look for red errors)
4. Check Network tab for failed API requests
5. Read error messages carefully (they usually explain the issue)

---

**When all checks are DONE ✓, your system is fully operational!**
