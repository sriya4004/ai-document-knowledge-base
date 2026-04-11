# Azure Deployment Guide

This project deploys with:
- Backend: Azure App Service (Linux, Python 3.11)
- Frontend: Azure Static Web Apps
- Database: Azure Database for PostgreSQL

## 1) Backend -> Azure App Service

1. Create an App Service (Linux, Python 3.11).
2. Set startup command to:
   - `bash startup.sh`
3. Configure App Settings in Azure:
   - `DATABASE_URL`
   - `ALLOWED_ORIGINS`
   - `JWT_SECRET_KEY`
   - `JWT_ALGORITHM`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `CHROMA_HOST`
   - `CHROMA_PORT`
   - `CHROMA_COLLECTION_NAME`
   - `EMBEDDING_MODEL_NAME`
   - `SEED_ADMIN_EMAIL`
   - `SEED_ADMIN_PASSWORD`
   - `SEED_ADMIN_DEPARTMENT`
4. GitHub Actions workflow:
   - `.github/workflows/backend-appservice.yml`
5. Required GitHub secrets:
   - `AZURE_CREDENTIALS`
   - `AZURE_BACKEND_APP_NAME`

## 2) Frontend -> Azure Static Web Apps

1. Create a Static Web App resource in Azure.
2. Use workflow:
   - `.github/workflows/frontend-static-web-apps.yml`
3. Required GitHub secrets:
   - `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - `VITE_API_BASE_URL` (for example `https://<backend-app>.azurewebsites.net/api/v1`)

## 3) Database -> Azure Database for PostgreSQL

The backend now supports a generic SQLAlchemy URL via `DATABASE_URL`.

Example Azure PostgreSQL URL:

`postgresql+psycopg2://<user>:<password>@<server>.postgres.database.azure.com:5432/<db>?sslmode=require`

## Notes

- Local development can continue using PostgreSQL by leaving `DATABASE_URL` unset.
- In production, set `DATABASE_URL` to Azure Database for PostgreSQL.
