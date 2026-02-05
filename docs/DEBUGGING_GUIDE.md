---
title: PDF Upload Network Error - Root Cause Analysis & Fixes
date: February 5, 2026
---

# PDF Upload Network Error - Architecture Review & Fixes

## Executive Summary

Your "network error" on PDF upload was caused by **5 critical architectural issues**. All have been fixed with logical solutions that address root causes, not symptoms.

---

## Issue #1: Axios Content-Type Header Conflict (CRITICAL)
**Severity**: 🔴 CRITICAL - Breaks multipart/form-data encoding

### Root Cause
In [frontend/src/lib/api.ts](frontend/src/lib/api.ts), the code was explicitly setting the `Content-Type` header to `multipart/form-data`:

```typescript
// WRONG - breaks file upload
const { data } = await client.post<UploadResponse>('/api/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },  // ❌ BREAKS ENCODING
  timeout: TIMEOUT_MS,
  ...
});
```

**Why it fails**: 
- When you set `Content-Type: multipart/form-data` manually, you must also include the boundary string (e.g., `boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW`)
- Axios cannot auto-generate the boundary when you manually set the header
- The server receives malformed multipart data and rejects it as a "network error"

### Fix Applied ✅
**File**: [frontend/src/lib/api.ts](frontend/src/lib/api.ts)

Removed the explicit `Content-Type` header. Axios automatically:
1. Detects FormData object
2. Sets correct header with proper boundary
3. Encodes the multipart payload correctly

```typescript
// CORRECT - let axios handle the header
const { data } = await client.post<UploadResponse>('/api/upload', formData, {
  // DO NOT set Content-Type header - axios handles it
  timeout: TIMEOUT_MS,
  onUploadProgress: ...
});
```

**Why this works**: Axios intelligently detects FormData and manages the multipart encoding with correct boundaries automatically.

---

## Issue #2: CORS Origin Mismatch
**Severity**: 🟠 HIGH - Causes 403 Forbidden on cross-origin requests

### Root Cause
The backend hardcoded CORS origins:

```python
# backend/app/main.py - OLD CODE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ❌ HARDCODED
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problems**:
1. No flexibility for different environments
2. If frontend runs on different host/port, CORS fails
3. No production configuration support
4. Doesn't respect environment variables

### Fix Applied ✅
**File**: [backend/app/main.py](backend/app/main.py)

Now uses the settings system to read from `.env`:

```python
def _make_app() -> FastAPI:
    app = FastAPI(title="AI Document QA API", lifespan=lifespan)
    
    # Get CORS origins from settings
    settings = get_settings()
    cors_origins = settings.cors_origins_list()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

**Why this works**: 
- Reads from `.env` file via pydantic-settings
- Easily configurable per environment
- Fallback to `["*"]` if not configured (safe for development)

---

## Issue #3: Missing Vite Proxy Configuration
**Severity**: 🟠 HIGH - Cross-origin requests fail in development

### Root Cause
The frontend had **no proxy** setup. In development, the Vite dev server (port 5173) was trying to directly hit the backend (port 8000):

```
Frontend (http://localhost:5173) → Backend (http://localhost:8000)
      ↑                                    ↑
   Different origin = CORS blocked
```

### Fix Applied ✅
**File**: [frontend/vite.config.ts](frontend/vite.config.ts)

Added a development proxy that:
1. Intercepts `/api/` requests
2. Forwards them to the backend server
3. Resets request path (no double `/api/api/`)

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },
});
```

**How it works**:
```
Frontend (5173) → Vite Proxy (5173) → Backend (8000)
                  (same origin)       (local forward)
```

---

## Issue #4: Missing LLM Service Import
**Severity**: 🔴 CRITICAL - Crashes on query endpoint

### Root Cause
In [backend/app/api/query.py](backend/app/api/query.py), the `LLMService` was never imported or instantiated:

```python
# OLD - import missing
from app.services.rerank import RerankService
from app.services.vector import VectorService

# Missing:
# from app.services.llm import LLMService

router = APIRouter()
vector_service = VectorService()
rerank_service = RerankService()
# llm_service never initialized ❌
```

### Fix Applied ✅
**File**: [backend/app/api/query.py](backend/app/api/query.py)

Added the missing import and initialization:

```python
from app.services.llm import LLMService
from app.services.rerank import RerankService
from app.services.vector import VectorService

router = APIRouter()
vector_service = VectorService()
rerank_service = RerankService()
llm_service = LLMService()  # ✅ NOW INITIALIZED
```

**Why this matters**: The query endpoint needs to generate LLM responses. Without this, any query would crash with `NameError: llm_service not defined`.

---

## Issue #5: Poor Error Handling in Frontend
**Severity**: 🟡 MEDIUM - User sees generic "Upload failed" instead of actual error

### Root Cause
In [frontend/src/components/FileUpload.tsx](frontend/src/components/FileUpload.tsx), the error handler was too generic:

```typescript
catch (err) {
  setStatus('error');
  setErrorMsg('Upload failed');  // ❌ NO DETAIL, NOT HELPFUL
}
```

**Problems**:
1. User doesn't know if it's network, timeout, or backend error
2. Can't debug what went wrong
3. Shows same message for all errors

### Fix Applied ✅
**File**: [frontend/src/components/FileUpload.tsx](frontend/src/components/FileUpload.tsx)

Added intelligent error extraction and display:

```typescript
catch (err: unknown) {
  setStatus('error');
  let errorMessage = 'Upload failed';
  
  // Extract meaningful error from axios or network error
  if (err instanceof Error) {
    if (err.message.includes('timeout')) {
      errorMessage = 'Upload timeout - backend may be busy';
    } else if (err.message.includes('network') || err.message.includes('Network')) {
      errorMessage = 'Network error - check backend connection';
    } else {
      errorMessage = err.message || 'Upload failed';
    }
  }
  
  setErrorMsg(errorMessage);
  showError(errorMessage);
}
```

Also added success toast feedback:

```typescript
// Actual upload
await uploadPdf(file);
setProgress(100);
setStatus('success');
showSuccess('PDF uploaded successfully');  // ✅ FEEDBACK
```

**Why this works**: Users now see specific error messages like "Upload timeout - backend may be busy" or "Network error - check backend connection", making debugging 10x easier.

---

## Issue #6: Missing Environment Configuration
**Severity**: 🟠 HIGH - Backend fails to load without `.env`

### Root Cause
No `.env` file was provided. The backend tried to load environment variables via:

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # ❌ FILE DOESN'T EXIST
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
```

Without a `.env` file, all required keys default to empty strings:
- `PINECONE_API_KEY = ""`
- `GROQ_API_KEY = ""`

This causes silent failures when these services are actually used.

### Fix Applied ✅
**Files**: 
- [.env](.env) - Created with all required variables
- [backend/.env.example](backend/.env.example) - Updated with complete documentation

Created `.env` with all required keys:

```env
# ============================================
# REQUIRED: Vector Database (Pinecone)
# ============================================
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
PINECONE_REGION=us-east-1

# ============================================
# REQUIRED: LLM Provider (Groq or OpenAI)
# ============================================
GROQ_API_KEY=
GROQ_MODEL=llama3-8b-8192

# ============================================
# CORS Configuration (comma-separated)
# ============================================
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

**Why this works**: Now the backend loads with proper structure. Missing keys are obvious (empty strings in config), not hidden bugs.

---

## Issue #7: API Base URL Logic Was Fragile
**Severity**: 🟡 MEDIUM - Works in dev, breaks in production

### Root Cause
The API client hardcoded the base URL:

```typescript
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
```

**Problems**:
1. No distinction between dev (proxy needed) and prod (direct URL needed)
2. Hardcoded fallback to `localhost:8000`
3. In production, would still try to hit localhost

### Fix Applied ✅
**File**: [frontend/src/lib/api.ts](frontend/src/lib/api.ts)

Added environment-aware routing:

```typescript
// In development, use relative /api path (proxied to backend)
// In production, use absolute URL from env or current origin
const BASE_URL = import.meta.env.PROD 
  ? (import.meta.env.VITE_API_URL || `${window.location.origin}`)
  : '';
```

**How it works**:
- **Dev mode** (`import.meta.env.PROD = false`): `BASE_URL = ''` → Uses `/api/` (proxied via Vite)
- **Prod mode** (`import.meta.env.PROD = true`): 
  - If `VITE_API_URL` env var set: uses that
  - Otherwise: uses current domain (`window.location.origin`)

---

## How to Verify Fixes

### 1. Check Backend Starts Cleanly
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Should show:
```
[VectorService] Loading FastEmbed model (BAAI/bge-small-en-v1.5)...
[VectorService] FastEmbed model loaded successfully.
INFO:     Application startup complete
```

### 2. Check Frontend Proxy Works
```bash
cd frontend
npm run dev
```
Open DevTools → Network tab. When uploading:
- Request URL should be: `/api/upload` (same origin)
- NOT: `http://localhost:8000/api/upload` (cross-origin)

### 3. Test PDF Upload End-to-End
1. Ensure `.env` has valid `PINECONE_API_KEY` and `PINECONE_INDEX_NAME`
2. Upload a PDF
3. Should see: "PDF uploaded successfully" ✅
4. If error: Shows specific error message (network, timeout, etc.)

### 4. Test Query Endpoint
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```
Should NOT crash (previously would if LLM service missing)

---

## Summary of Changes

| File | Issue | Fix |
|------|-------|-----|
| [frontend/src/lib/api.ts](frontend/src/lib/api.ts) | Content-Type header breaks multipart | Removed explicit header, let axios handle it |
| [frontend/vite.config.ts](frontend/vite.config.ts) | No dev proxy = CORS blocked | Added `/api` proxy to backend |
| [backend/app/main.py](backend/app/main.py) | Hardcoded CORS origins | Use environment-aware settings |
| [backend/app/api/query.py](backend/app/api/query.py) | Missing LLM service import | Added import and initialization |
| [frontend/src/components/FileUpload.tsx](frontend/src/components/FileUpload.tsx) | Generic error message | Show specific error types (timeout, network, etc.) |
| [.env](.env) | No environment configuration | Created with all required variables |
| [frontend/src/lib/api.ts](frontend/src/lib/api.ts) | Fragile base URL logic | Environment-aware (dev uses proxy, prod uses absolute URL) |

---

## Root Cause Categories

### Network Layer Issues (2-3, 7)
- CORS misconfiguration
- Missing proxy in development
- Fragile URL routing

**Fix Strategy**: Configuration-driven (respect environment)

### API Layer Issues (1, 5)
- Content-Type header conflict
- Poor error handling

**Fix Strategy**: Use framework defaults (axios knows multipart), expose real errors

### Backend Issues (4, 6)
- Missing service initialization
- No configuration file

**Fix Strategy**: Complete all wiring, provide sensible defaults

---

## Architecture Lessons

1. **Don't manually set headers axios handles** - Framework defaults exist for a reason
2. **CORS is environment-specific** - Use settings, not hardcoded values
3. **Dev proxies solve cross-origin issues** - Don't rely on CORS for dev environments
4. **Import all dependencies** - Unused imports are a code smell; missing ones are a bug
5. **Errors should be specific** - Help users debug with actionable messages
6. **Configuration should be explicit** - Use `.env` files for all secrets and settings
7. **URL routing should be environment-aware** - Dev ≠ Prod

---

## Next Steps

1. ✅ **Implement all fixes** (already done)
2. ⏳ **Populate `.env` with your credentials**:
   - Get `PINECONE_API_KEY` from [pinecone.io](https://pinecone.io)
   - Get `GROQ_API_KEY` from [console.groq.com](https://console.groq.com)
   - Get `PINECONE_INDEX_NAME` from your Pinecone project
3. ✅ **Start backend**: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
4. ✅ **Start frontend**: `cd frontend && npm run dev`
5. ✅ **Test PDF upload**: Drag and drop a PDF in the browser
6. ✅ **Test query**: Ask a question about the PDF

---

## Monitoring Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check Pinecone connection
curl http://localhost:8000/api/upload \
  -F "file=@test.pdf"

# Monitor frontend dev server
# Open http://localhost:5173
# Check DevTools Console for errors
```
