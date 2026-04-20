# 🏗️ AI Interview Preparation — Backend Architecture

> **Version:** 1.0.0  
> **Framework:** FastAPI (Python)  
> **Last Updated:** April 2026

---

## 📑 Table of Contents

1. [High-Level Architecture Overview](#1-high-level-architecture-overview)
2. [Service Breakdown](#2-service-breakdown)
3. [Production Folder Structure](#3-production-folder-structure)
4. [API Design](#4-api-design)
5. [WebSocket Architecture](#5-websocket-architecture)
6. [Authentication](#6-authentication)
7. [Database Layer — Firestore](#7-database-layer--firestore)
8. [File Storage — Supabase](#8-file-storage--supabase)
9. [AI Layer — LangChain + LangGraph](#9-ai-layer--langchain--langgraph)
10. [End-to-End Request Flow](#10-end-to-end-request-flow)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Error Handling & Scalability](#12-error-handling--scalability)

---

## 1. High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND  (React + Vite)                          │
│                        Hosted on Vercel (Static)                           │
└──────────┬──────────────────────┬───────────────────────┬───────────────────┘
           │ REST (HTTPS)         │ WebSocket (WSS)       │ REST (HTTPS)
           ▼                     ▼                        ▼
┌──────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐
│   Vercel APIs    │  │   FastAPI Server     │  │   Vercel APIs       │
│  (Serverless)    │  │   (Render)           │  │  (Serverless)       │
│  ─ lightweight   │  │  ─ core backend      │  │  ─ lightweight      │
│    REST proxy    │  │  ─ WebSocket host    │  │    REST proxy       │
└──────────────────┘  │  ─ AI processing     │  └─────────────────────┘
                      │  ─ Auth validation   │
                      └────┬─────┬─────┬─────┘
                           │     │     │
              ┌────────────┘     │     └────────────┐
              ▼                  ▼                   ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
    │   Firebase   │   │   Supabase   │   │   External APIs  │
    │  ─ Firestore │   │  ─ Storage   │   │  ─ OpenRouter    │
    │  ─ Auth      │   │    (Buckets) │   │  ─ Tavily        │
    └──────────────┘   └──────────────┘   │  ─ Code Runner   │
                                          └──────────────────┘
```

### Tech Stack Summary

| Layer              | Technology                              |
|--------------------|----------------------------------------|
| **Backend**        | FastAPI + Uvicorn (Python)             |
| **Real-Time**      | FastAPI WebSockets                     |
| **REST Gateway**   | Vercel Serverless Functions            |
| **Authentication** | Firebase Auth (ID Token Verification)  |
| **Database**       | Firebase Firestore (NoSQL)             |
| **File Storage**   | Supabase Storage (Bucket)              |
| **AI Engine**      | LangChain + LangGraph                  |
| **LLM Provider**   | OpenRouter (ChatOpenAI-compatible)     |
| **Research Tool**  | Tavily Search API                      |
| **Code Execution** | External Code Runner (Render-hosted)   |
| **Hosting**        | Render (FastAPI) + Vercel (APIs/frontend) |

---

## 2. Service Breakdown

### 2.1 FastAPI Services (Hosted on Render)

The core FastAPI application handles **all business logic, AI processing, and real-time communication**.

```
┌───────────────────────────────────────────────────┐
│                FastAPI Application                 │
│                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │   Resume    │  │  Technical  │  │  Coding   │ │
│  │   Service   │  │  Service    │  │  Service  │ │
│  └─────────────┘  └─────────────┘  └───────────┘ │
│                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │     HR      │  │    User     │  │ Feedback  │ │
│  │   Service   │  │  Service    │  │  Service  │ │
│  └─────────────┘  └─────────────┘  └───────────┘ │
│                                                    │
│  ┌─────────────┐  ┌─────────────┐                 │
│  │  LLM Core   │  │ Code Runner │                 │
│  │  (AI Layer) │  │  (External) │                 │
│  └─────────────┘  └─────────────┘                 │
└───────────────────────────────────────────────────┘
```

| Service               | Responsibility                                          |
|-----------------------|---------------------------------------------------------|
| **Resume Service**    | PDF upload → Supabase, PDF text extraction, AI resume parsing, Firestore storage |
| **Technical Service** | LangGraph-powered question generation, answer submission, batch + real-time evaluation |
| **Coding Service**    | DSA question generation, code execution against test cases, WebSocket interview flow |
| **HR Service**        | Behavioral question generation, answer submission, batch + real-time evaluation |
| **User Service**      | Profile CRUD, resume data linking, progress tracking    |
| **Feedback Service**  | Session-level feedback retrieval                        |
| **LLM Core**         | Centralized LLM wrapper (OpenRouter via ChatOpenAI)     |

### 2.2 WebSocket Services

Three real-time WebSocket endpoints run **on the same FastAPI server**:

| Endpoint            | Purpose                                   |
|--------------------|--------------------------------------------|
| `/coding/ws`       | Real-time coding interview (typing hints, run results, code-along) |
| `/technical/ws`    | Real-time technical answer evaluation      |
| `/hr/ws`           | Real-time HR answer evaluation             |

### 2.3 REST API Layer (Vercel)

Vercel serverless functions act as **lightweight REST proxies** for the frontend, forwarding requests to the Render-hosted FastAPI backend. The frontend is deployed on Vercel, and API routes serve as the entry point for HTTP calls.

---

## 3. Production Folder Structure

```
aiInterviewPreparation-backend/
│
├── .env                              # Environment variables (secrets)
├── .gitignore                        # Git exclusions
├── requirements.txt                  # Python dependencies
├── firebase-key.json                 # Firebase service account (git-ignored)
│
├── app/
│   ├── main.py                       # ⭐ FastAPI app entry point
│   │
│   ├── api/                          # 🌐 Route Layer (Controllers)
│   │   ├── __init__.py
│   │   ├── router.py                 # Central API router (mounts all sub-routers)
│   │   ├── resume.py                 # POST /resume/
│   │   ├── technical.py              # GET|POST /technical/* + WebSocket /technical/ws
│   │   ├── coding.py                 # POST /coding/* + WebSocket /coding/ws
│   │   ├── hr_router.py              # POST /hr/* + WebSocket /hr/ws
│   │   ├── user.py                   # GET|PUT /user/
│   │   └── feedback.py               # GET /feedback/{session_id}
│   │
│   ├── core/                         # ⚙️ Core Configuration & Infra
│   │   ├── __init__.py
│   │   ├── config.py                 # Pydantic Settings (env-based config)
│   │   ├── firebase.py               # Firebase Admin SDK initialization
│   │   ├── security.py               # Auth dependency (HTTP + WebSocket)
│   │   └── supabase_client.py        # Supabase client initialization
│   │
│   ├── schemas/                      # 📐 Pydantic Models (Request/Response)
│   │   ├── __init__.py
│   │   ├── user.py                   # UserCreate schema
│   │   ├── resume/
│   │   │   └── resume_schema.py      # ResumeSchema, Project, WorkExperience
│   │   ├── technical/
│   │   │   ├── technical_schema.py       # QuestionItem, QuestionSet
│   │   │   ├── technical_request_schema.py # TechnicalAnswerRequest
│   │   │   └── evaluation_schema.py      # EvaluatedQuestion, EvaluationSet
│   │   ├── coding/
│   │   │   ├── coding_schema.py          # CodingQuestion, TestCase, CodingQuestionSet
│   │   │   ├── QuestionRequest.py        # QuestionRequest (count, level)
│   │   │   ├── coding_run_schema.py      # CodingRunRequest
│   │   │   ├── coding_submit_schema.py   # CodingSubmitRequest
│   │   │   └── coding_playground_schema.py # CodingPlaygroundRequest
│   │   └── hr/
│   │       ├── hr_schema.py              # HRQuestionItem, HRQuestionSet
│   │       └── hr_evaluation_schema.py   # HREvaluationItem, HREvaluationSet
│   │
│   ├── services/                     # 🧠 Business Logic Layer
│   │   ├── __init__.py
│   │   ├── user_service.py           # User document updates (resume linkage)
│   │   ├── llm/
│   │   │   └── llm_core.py           # LLMCore wrapper (ChatOpenAI via OpenRouter)
│   │   ├── resume/
│   │   │   ├── resume_service.py         # Upload, parse, store pipeline
│   │   │   └── resume_parser_service.py  # PDF extraction + AI structured parsing
│   │   ├── technical/
│   │   │   ├── technical_service.py      # Question generation, session management
│   │   │   ├── technical_graph.py        # LangGraph: topics → research → questions
│   │   │   ├── evaluation_service.py     # Batch evaluation (all answers)
│   │   │   └── realtime_service.py       # Single-answer real-time evaluation (WS)
│   │   ├── coding/
│   │   │   ├── coding_service.py         # Set generation, submission, hints
│   │   │   ├── coding_graph.py           # LangGraph: context → research → questions
│   │   │   ├── coding_interview_graph.py # LangGraph: typing/run/suggest → hint
│   │   │   ├── coding_ws_service.py      # WebSocket handler (interview flow)
│   │   │   ├── coding_runner_service.py  # Preview execution (first 3 test cases)
│   │   │   ├── coding_evaluation_service.py # Full test case evaluation
│   │   │   ├── code_execution_service.py # HTTP client to external Code Runner
│   │   │   └── coding_playground_service.py # Playground mode execution
│   │   └── hr/
│   │       ├── hr_service.py             # Question generation, batch submission
│   │       ├── hr_graph.py               # LangGraph: resume → topics → questions
│   │       ├── hr_evaluation_service.py  # Batch HR evaluation
│   │       └── hr_service_realtime.py    # Single-answer real-time evaluation (WS)
│   │
│   ├── middleware/                    # 🔒 Middleware (reserved)
│   ├── db/                           # 💾 Database Layer (reserved)
│   ├── tools/                        # 🔧 Utilities/Tools (reserved)
│   ├── utils/                        # 🛠️ Helper Utilities (reserved)
│   └── notebooks/                    # 📓 Jupyter Notebooks (testing)
│       └── websocke_testing_notebook.ipynb
│
└── uploads/                          # 📁 Temporary file uploads (git-ignored)
```

---

## 4. API Design

### 4.1 Route Structure

All routes are registered in `app/api/router.py` via a centralized `APIRouter`:

```
ROOT: /
├── GET  /                          → Health Check (System)
│
├── /resume
│   └── POST /                      → Upload & parse resume
│
├── /technical
│   ├── GET  /questions             → Generate technical questions
│   ├── POST /answers               → Submit all technical answers
│   ├── GET  /sets                  → List interview sessions
│   ├── GET  /sets/{technical_set_id} → Open specific session
│   └── WS   /ws                    → Real-time answer evaluation
│
├── /coding
│   ├── POST /questions             → Generate coding questions
│   ├── POST /submit                → Submit solution (full eval)
│   ├── POST /run                   → Run code (first 3 test cases)
│   ├── POST /playground            → Playground execution
│   ├── GET  /sets                  → List coding sessions
│   ├── GET  /sets/{coding_set_id}  → Get session questions
│   └── WS   /ws                    → Real-time coding interview
│
├── /hr
│   ├── POST /questions             → Generate HR questions
│   ├── POST /answers               → Submit HR answers
│   └── WS   /ws                    → Real-time HR evaluation
│
├── /user
│   ├── GET  /                      → Get user profile
│   └── PUT  /                      → Update user profile
│
└── /feedback
    └── GET  /{session_id}          → Get session feedback
```

### 4.2 Request / Response Flow

#### REST API Flow

```
┌──────────┐     ┌───────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│  Client  │────▶│   Route   │────▶│ Security │────▶│  Service  │────▶│ Response │
│(Frontend)│     │ (api/*.py)│     │(Depends) │     │(services/)│     │  (JSON)  │
└──────────┘     └───────────┘     └──────────┘     └───────────┘     └──────────┘
                                        │                 │
                                        ▼                 ▼
                                   ┌─────────┐     ┌───────────┐
                                   │Firebase │     │ Firestore │
                                   │  Auth   │     │ / Supabase│
                                   └─────────┘     └───────────┘
```

#### Typical REST Response Pattern

```json
// Success — Question Generation
{
  "technical_set_id": "uuid-string",
  "questions": [
    {
      "question_no": 1,
      "question": "...",
      "answer": "..."
    }
  ]
}

// Success — Evaluation
{
  "evaluations": [...],
  "overall_score": 8,
  "overall_feedback": "..."
}

// Error
{
  "detail": "Invalid or expired token"
}
```

---

## 5. WebSocket Architecture

### 5.1 WebSocket Endpoints

| Endpoint           | File                    | Handler Service                    |
|-------------------|-------------------------|------------------------------------|
| `/technical/ws`   | `api/technical.py`      | `realtime_service.py`              |
| `/hr/ws`          | `api/hr_router.py`      | `hr_service_realtime.py`           |
| `/coding/ws`      | `api/coding.py`         | `coding_ws_service.py` → `coding_interview_graph.py` |

### 5.2 Connection Flow

```
┌──────────┐                              ┌───────────────┐
│  Client  │──── WSS connect ────────────▶│  FastAPI WS   │
│          │    ?token=<firebase_token>    │   Endpoint    │
└──────────┘                              └───────┬───────┘
                                                  │
                                          ┌───────▼───────┐
                                          │  Token Check  │
                                          │   (verify_    │
                                          │    token)     │
                                          └───────┬───────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    │ ❌ Invalid   │ ✅ Valid      │
                                    ▼             │              ▼
                           ┌──────────────┐      │    ┌──────────────┐
                           │  close(1008) │      │    │   accept()   │
                           └──────────────┘      │    │  connection  │
                                                 │    └──────┬───────┘
                                                 │           │
                                                 │    ┌──────▼───────┐
                                                 │    │  Message     │
                                                 │    │  Loop        │
                                                 │    │  (while True)│
                                                 │    └──────────────┘
```

### 5.3 Technical / HR WebSocket — Real-Time Messaging

```
CLIENT                                          SERVER
  │                                                │
  │──── { "technical_set_id": "...",  ────────────▶│
  │       "question_no": 1,                        │
  │       "answer": "..." }                        │
  │                                                │
  │                                    ┌───────────┤
  │                                    │ 1. Parse JSON
  │                                    │ 2. Update answer in Firestore
  │                                    │ 3. Find target question
  │                                    │ 4. Call LLM for evaluation
  │                                    │ 5. Store evaluation
  │                                    └───────────┤
  │                                                │
  │◀──── { "question_no": 1,         ─────────────│
  │        "user_answer": "...",                   │
  │        "feedback": "...",                      │
  │        "evaluated_at": "..." }                 │
  │                                                │
```

### 5.4 Coding WebSocket — Interview Mode

The coding WebSocket uses a **LangGraph state machine** for intelligent flow control:

```
CLIENT                                          SERVER
  │                                                │
  │──── { "type": "start",           ─────────────▶│
  │       "coding_set_id": "...",                  │── Load question from Firestore
  │       "question_no": 0 }                       │── Run explain_question (LLM)
  │                                                │
  │◀──── { "type": "explanation",    ──────────────│
  │        "message": "..." }                      │
  │                                                │
  │──── { "type": "typing",          ────────────▶ │
  │       "code": "def solve..." }                 │── coding_interview_graph.ainvoke()
  │                                                │   ├── typing_decision (check diff)
  │                                                │   └── typing_hint (LLM if needed)
  │                                                │
  │◀──── { "type": "hint",          ──────────────│   (only if code diff ≥ 8 chars)
  │        "hint": "..." }                         │
  │                                                │
  │──── { "type": "run",             ────────────▶ │
  │       "code": "..." }                          │── run_node → external code runner
  │                                                │── run_hint (LLM feedback)
  │                                                │
  │◀──── { "type": "hint",          ──────────────│
  │        "hint": "...",                          │
  │        "test_result": {...} }                  │
  │                                                │
  │──── { "type": "suggest" }        ────────────▶ │── force_hint (LLM always responds)
  │                                                │
  │◀──── { "type": "hint",          ──────────────│
  │        "hint": "..." }                         │
```

#### Coding Interview Graph State Machine

```
                    ┌─────────────────────┐
                    │   Event Router      │
                    │  (conditional entry) │
                    └──────┬──────┬───────┘
                           │      │      │
              event="typing"│     │      │event="run"
                           │      │      │
                    ┌──────▼──┐   │   ┌──▼──────────┐
                    │ typing  │   │   │  run_node   │
                    │decision │   │   │(code runner) │
                    └────┬────┘   │   └──────┬──────┘
                         │        │          │
                    ┌────▼────┐   │   ┌──────▼──────┐
                    │ typing  │   │   │  run_hint   │
                    │  hint   │   │   │  (LLM)      │
                    └────┬────┘   │   └──────┬──────┘
                         │        │          │
                         ▼        │          ▼
                       [END]      │        [END]
                                  │
                         event="suggest"
                                  │
                           ┌──────▼──────┐
                           │ force_hint  │
                           │   (LLM)     │
                           └──────┬──────┘
                                  │
                                  ▼
                                [END]
```

---

## 6. Authentication

### 6.1 Firebase Auth Integration

Authentication is handled via **Firebase Admin SDK**. The frontend obtains a Firebase ID Token and sends it with every request.

```
┌──────────┐     ┌──────────────┐     ┌───────────────┐
│  Client  │────▶│  Firebase    │────▶│  ID Token     │
│          │     │  Auth SDK    │     │  (JWT)        │
│          │     │  (Frontend)  │     │               │
└──────────┘     └──────────────┘     └───────┬───────┘
                                              │
                      Sent as                 │
                      Authorization: Bearer   │
                      or ?token= (WS)         │
                                              ▼
                                    ┌───────────────────┐
                                    │  FastAPI Backend   │
                                    │                    │
                                    │  firebase_admin    │
                                    │  .auth             │
                                    │  .verify_id_token()│
                                    │                    │
                                    │  Returns: uid      │
                                    └───────────────────┘
```

### 6.2 Token Validation in Backend

#### Firebase Initialization (`app/core/firebase.py`)

```python
# Reads FIREBASE_CREDENTIALS from .env (JSON string)
cred_dict = json.loads(settings.FIREBASE_CREDENTIALS)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()   # Firestore client

def verify_token(id_token: str):
    decoded_token = auth.verify_id_token(id_token)
    return decoded_token    # contains "uid"
```

#### HTTP Route Authentication (`app/core/security.py`)

```python
security = HTTPBearer()

def get_current_user(credentials = Depends(security)):
    token = credentials.credentials
    decoded = verify_token(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return decoded["uid"]
```

#### WebSocket Authentication (`app/core/security.py`)

```python
async def get_current_user_ws(token: str):
    decoded = verify_token(token)
    if not decoded:
        raise Exception("Invalid or expired token")
    return decoded["uid"]
```

> **Note:** WebSocket connections pass the token via **query parameter** (`?token=<id_token>`) or **Authorization header** as a fallback.

### 6.3 Auth Protection Matrix

| Endpoint           | Auth Required | Method         |
|-------------------|:-------------:|----------------|
| `GET /`           | ❌            | None           |
| `POST /resume/`   | ✅            | HTTPBearer     |
| `GET /technical/*` | ✅            | HTTPBearer     |
| `POST /technical/*`| ✅            | HTTPBearer     |
| `WS /technical/ws` | ✅            | Query Param    |
| `POST /coding/*`   | ✅            | HTTPBearer     |
| `POST /coding/playground` | ❌     | None           |
| `WS /coding/ws`    | ✅            | Query Param    |
| `POST /hr/*`       | ✅            | HTTPBearer     |
| `WS /hr/ws`        | ✅            | Query Param    |
| `GET /user/`       | ✅            | HTTPBearer     |
| `PUT /user/`       | ✅            | HTTPBearer     |
| `GET /feedback/*`  | ❌            | None           |

---

## 7. Database Layer — Firestore

### 7.1 Firestore Collection Structure

```
Firestore
│
├── users/                                    # Root: User profiles
│   └── {user_id}/                            # Document per user
│       ├── resume_id: string
│       ├── resume_data: map                  # Parsed resume (structured)
│       │   ├── name, email, phone
│       │   ├── skills: array
│       │   ├── projects: array<map>
│       │   ├── work_experience: array<map>
│       │   ├── certifications: array
│       │   └── achievements: array
│       ├── target_role, experience_level
│       ├── preferred_locations: array
│       ├── upcoming_interviews, applied_companies
│       ├── coding_progress, technical_progress, hr_progress
│       ├── strengths, weaknesses, career_goal
│       ├── created_at, updated_at
│       │
│       ├── [SUB] technical_questions/        # User's technical sessions
│       │   └── {technical_set_id}/
│       │       ├── technical_set_id: string
│       │       ├── questions: array<map>
│       │       ├── answers: map { "1": "...", "2": "..." }
│       │       ├── evaluations: array<map>
│       │       ├── overall_score: int | null
│       │       ├── status: "pending" | "in_progress" | "submitted" | "evaluated"
│       │       ├── created_at, submitted_at, evaluated_at
│       │       └── started_at
│       │
│       ├── [SUB] coding_questions/           # User's coding sessions
│       │   └── {coding_set_id}/
│       │       ├── coding_set_id: string
│       │       ├── count: int
│       │       ├── levels: array<string>
│       │       ├── questions: array<map>
│       │       │   └── { difficulty, title, function_signature,
│       │       │         problem_statement, input_format, output_format,
│       │       │         constraints, test_cases: [{input, output}] }
│       │       ├── answers: map
│       │       ├── submissions: map { "q0": {code, evaluation, submitted_at} }
│       │       ├── status: "pending" | ...
│       │       └── created_at
│       │
│       └── [SUB] hr_questions/               # User's HR sessions
│           └── {hr_set_id}/
│               ├── hr_set_id: string
│               ├── role: string
│               ├── company: string
│               ├── questions: array<map>
│               ├── answers: map
│               ├── evaluations: array<map>
│               ├── overall_score: int | null
│               ├── status: "pending" | "in_progress" | "submitted" | "evaluated"
│               ├── created_at, updated_at
│               └── submitted_at
│
├── technical_questions/                      # Master: Technical question bank
│   └── {user_id}/
│       └── [SUB] sets/
│           └── {technical_set_id}/
│               ├── technical_set_id: string
│               ├── questions: array<map>
│               ├── answers: map
│               ├── status: "pending"
│               └── created_at
```

### 7.2 Data Models (Pydantic Schemas)

#### Resume Schema

```python
class ResumeSchema(BaseModel):
    name: str
    phone: str
    email: str
    skills: List[str]
    work_experience: List[WorkExperience]   # {company, role, duration, description}
    certifications: List[str]
    achievements: List[str]
    projects: List[Project]                 # {project_name, project_stack, project_description}
```

#### Technical Question Schema

```python
class QuestionItem(BaseModel):
    question_no: int
    question: str
    answer: str

class QuestionSet(BaseModel):
    questions: List[QuestionItem]
```

#### Technical Evaluation Schema

```python
class EvaluatedQuestion(BaseModel):
    question_no: int
    question: str
    correct_answer: str
    user_answer: str
    score: int                     # 0–10
    technical_feedback: str
    motivation: str

class EvaluationSet(BaseModel):
    evaluations: List[EvaluatedQuestion]
    overall_score: int
    overall_feedback: str
```

#### Coding Question Schema

```python
class CodingQuestion(BaseModel):
    difficulty: str
    title: str
    function_signature: str
    problem_statement: str
    input_format: str
    output_format: str
    constraints: str
    test_cases: List[TestCase]     # [{input, output}]

class CodingQuestionSet(BaseModel):
    questions: List[CodingQuestion]
```

#### HR Evaluation Schema

```python
class HREvaluationItem(BaseModel):
    question_no: int
    score: int
    technical_feedback: str
    motivation: str

class HREvaluationSet(BaseModel):
    evaluations: List[HREvaluationItem]
    overall_score: int
    overall_feedback: str
```

---

## 8. File Storage — Supabase

### 8.1 Supabase Bucket Usage

```
┌──────────┐     ┌───────────────┐     ┌──────────────────┐
│  Client  │────▶│  FastAPI      │────▶│  Supabase        │
│ (Upload) │     │  /resume/     │     │  Storage Bucket  │
│          │     │               │     │  "resume"        │
└──────────┘     └───────────────┘     └──────────────────┘
```

#### Upload Flow

```
1. Client → POST /resume/ (multipart/form-data)

2. Backend:
   ├── Generate UUID → resume_id
   ├── Read file bytes
   ├── Upload to Supabase bucket "resume"
   │   Path: "{resume_id}_{filename}"
   │   Retry: 5 attempts with 3-second backoff
   │
   ├── Generate signed URL (1 hour expiry)
   │
   ├── Extract text from PDF via signed URL
   │   (PyPDF2 → text extraction)
   │
   ├── AI-parse text → structured ResumeSchema
   │   (LangChain → structured output)
   │
   ├── Store parsed data in Firestore
   │   users/{uid}.resume_data = {...}
   │   users/{uid}.resume_id = "..."
   │
   └── Create sample coding set (ID=1) for user

3. Response:
   { "resume_id": "...", "file_url": "..." }
```

#### Supabase Client Configuration (`app/core/supabase_client.py`)

```python
from supabase import create_client

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)
```

---

## 9. AI Layer — LangChain + LangGraph

### 9.1 LLM Core Configuration

The centralized LLM wrapper (`app/services/llm/llm_core.py`) provides a single instance for all AI operations:

```python
class LLMCore:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,          # e.g., "arcee-ai/trinity-large-preview:free"
            temperature=settings.LLM_TEMPERATURE,  # 0.3
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,  # OpenRouter endpoint
        )

    def chat(self, messages):                    # Direct invocation
        return self.llm.invoke(messages)

    def with_structured_output(self, schema):    # Pydantic-enforced output
        return self.llm.with_structured_output(schema)
```

> **Key Pattern:** All LLM calls use `with_structured_output(PydanticSchema)` to guarantee strongly-typed responses. This eliminates manual JSON parsing and ensures data integrity.

### 9.2 LangGraph Workflows

#### 9.2.1 Technical Question Generation Graph

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────┐
│  select_topics  │────▶│    research     │────▶│ generate_questions  │
│                 │     │   (Tavily)      │     │    (LLM)            │
└─────────────────┘     └─────────────────┘     └─────────────────────┘

State: {resume_data} → {topics} → {research_data} → {questions}
```

| Node                  | Logic                                                        |
|-----------------------|--------------------------------------------------------------|
| `select_topics`       | Extracts skills + project names from resume, randomly samples 1–4 topics |
| `research`            | Calls Tavily API in parallel for each topic, collects research content (2000 char limit per topic) |
| `generate_questions`  | Prompts LLM with research context → `QuestionSet` (10 Q&A)  |

#### 9.2.2 Coding Question Generation Graph

```
┌──────────────────┐     ┌─────────────────┐     ┌─────────────────────┐
│ extract_context  │────▶│    research     │────▶│ generate_questions  │
│                  │     │   (Tavily)      │     │    (LLM)            │
└──────────────────┘     └─────────────────┘     └─────────────────────┘

State: {resume_data, count, levels} → {tech_context} → {research_data} → {questions}
```

| Node                | Logic                                                          |
|---------------------|----------------------------------------------------------------|
| `extract_context`   | Detects programming languages (Python, Java, C++, etc.) from skills, extracts project descriptions |
| `research`          | Randomly selects 3 DSA topics (sliding window, graph DFS, DP, etc.), calls Tavily with "FAANG coding interview" queries |
| `generate_questions`| Generates ORIGINAL LeetCode-style problems with 6 test cases each, using random seed for diversity |

#### 9.2.3 HR Question Generation Graph

```
┌──────────────────┐     ┌─────────────────┐     ┌─────────────────────┐
│ extract_resume   │────▶│  select_topics  │────▶│ generate_questions  │
│                  │     │                 │     │    (LLM)            │
└──────────────────┘     └─────────────────┘     └─────────────────────┘

State: {role, company, resume_data} → {resume_context} → {topics} → {questions}
```

| Node                | Logic                                                          |
|---------------------|----------------------------------------------------------------|
| `extract_resume`    | Builds candidate context from work experience, projects, achievements |
| `select_topics`     | Randomly picks 5 HR topics (leadership, teamwork, conflict resolution, etc.) — adds dynamic topics based on resume content |
| `generate_questions`| Creates 10 personalized behavioral questions with ideal answers, tailored to target role + company |

#### 9.2.4 Coding Interview Graph (Real-Time)

```
                    ┌──────────────────┐
                    │   Event Router   │
                    └──┬─────┬─────┬──┘
                       │     │     │
            "typing"   │  "suggest"│   "run"
                       │     │     │
               ┌───────▼┐  ┌▼─────┴───┐  ┌────────┐
               │ typing │  │  force   │  │  run   │
               │decision│  │  hint    │  │  node  │
               └───┬────┘  └────┬─────┘  └───┬────┘
                   │            │             │
               ┌───▼────┐      │        ┌────▼────┐
               │ typing │      │        │  run    │
               │  hint  │      │        │  hint   │
               └───┬────┘      │        └────┬────┘
                   │           │             │
                   ▼           ▼             ▼
                 [END]       [END]         [END]

State: {question, code, previous_code, event, user_id, coding_set_id, ...}
```

| Node               | Logic                                                        |
|--------------------|--------------------------------------------------------------|
| `typing_decision`  | Checks if code diff from previous code ≥ 8 chars; if not, sets `skip=True` |
| `typing_hint`      | Calls LLM as interviewer watching typing; returns "SILENT" if no hint needed |
| `force_hint`       | Always generates a hint (triggered by user "suggest" button) |
| `run_node`         | Executes code against first 3 test cases via external Code Runner |
| `run_hint`         | Analyzes test results and provides interviewer feedback       |

### 9.3 AI Usage Summary

| Feature                     | LangChain Feature Used              | Output Schema             |
|-----------------------------|------------------------------------|---------------------------|
| Resume Parsing              | `ChatPromptTemplate` + `with_structured_output` | `ResumeSchema`       |
| Technical Q Generation      | LangGraph (3 nodes) + `with_structured_output`  | `QuestionSet`        |
| Technical Evaluation        | `with_structured_output`            | `EvaluationSet`           |
| Technical Real-Time Eval    | `with_structured_output`            | `SingleEvaluation`        |
| Coding Q Generation         | LangGraph (3 nodes) + `with_structured_output`  | `CodingQuestionSet`  |
| Coding Hints (typing/run)   | Direct `llm.chat()` invocation      | Raw text                  |
| Coding Interview Flow       | LangGraph (5 nodes, conditional)    | State dict                |
| HR Q Generation             | LangGraph (3 nodes) + `with_structured_output`  | `HRQuestionSet`      |
| HR Evaluation               | `with_structured_output`            | `HREvaluationSet`         |
| HR Real-Time Eval           | `with_structured_output`            | `HREvaluation`            |

---

## 10. End-to-End Request Flow

### 10.1 Resume Upload Flow

```
Frontend                  API                    AI                   Storage               DB
   │                       │                     │                      │                    │
   │── POST /resume/ ────▶ │                     │                      │                    │
   │   (PDF file)          │                     │                      │                    │
   │                       │── upload_with_retry ─────────────────────▶ │                    │
   │                       │                     │                      │── Store PDF        │
   │                       │◀── signed URL ──────────────────────────── │                    │
   │                       │                     │                      │                    │
   │                       │── extract_text ────▶│                      │                    │
   │                       │   (PyPDF2)          │                      │                    │
   │                       │                     │                      │                    │
   │                       │── parse_resume ────▶│                      │                    │
   │                       │                     │── LLM structured ──▶ │                    │
   │                       │◀── ResumeSchema ─── │                      │                    │
   │                       │                     │                      │                    │
   │                       │── update_user_resume_full ──────────────────────────────────── ▶│
   │                       │                     │                      │     Firestore      │
   │                       │── create_sample_coding_set ─────────────────────────────────── ▶│
   │                       │                     │                      │                    │
   │◀── {resume_id, url}── │                     │                      │                    │
```

### 10.2 Technical Interview Flow

```
Frontend              API                   AI (LangGraph)           Research             DB
   │                    │                       │                       │                   │
   │── GET /technical ─▶│                       │                       │                   │
   │   /questions        │── get resume ────────────────────────────────────────────────── ▶│
   │                    │◀── resume_data ───────────────────────────────────────────────── │
   │                    │                       │                       │                   │
   │                    │── technical_graph ───▶ │                       │                   │
   │                    │                       │── select_topics       │                   │
   │                    │                       │── research ──────────▶│                   │
   │                    │                       │◀── research_data ──── │                   │
   │                    │                       │── generate_questions  │                   │
   │                    │                       │   (LLM)              │                   │
   │                    │◀── questions ──────── │                       │                   │
   │                    │                       │                       │                   │
   │                    │── store to Firestore ──────────────────────────────────────────▶ │
   │                    │   (master + user copy) │                       │                   │
   │                    │                       │                       │                   │
   │◀── {set_id, Q} ── │                       │                       │                   │
   │                    │                       │                       │                   │
   │── WS /technical/ws▶│                       │                       │                   │
   │   {answer}         │── evaluate (LLM) ───▶ │                       │                   │
   │                    │◀── score + feedback ── │                       │                   │
   │                    │── update Firestore ──────────────────────────────────────────── ▶│
   │◀── {evaluation} ── │                       │                       │                   │
```

### 10.3 Coding Interview Flow

```
Frontend              API                   LangGraph              Code Runner           DB
   │                    │                       │                       │                   │
   │── POST /coding ──▶ │                       │                       │                   │
   │   /questions        │── coding_graph ────▶  │                       │                   │
   │                    │                       │── extract_context     │                   │
   │                    │                       │── research (Tavily)   │                   │
   │                    │                       │── generate (LLM)      │                   │
   │                    │◀── questions ──────── │                       │                   │
   │◀── {set_id,Q}  ── │                       │                       │                   │
   │                    │                       │                       │                   │
   │── WS /coding/ws ─▶│                       │                       │                   │
   │   {"type":"start"} │── explain_question ──▶│                       │                   │
   │◀── explanation ─── │                       │                       │                   │
   │                    │                       │                       │                   │
   │   {"type":"typing"}│── coding_interview_graph ▶│                   │                   │
   │                    │                       │── typing_decision     │                   │
   │                    │                       │── typing_hint (LLM)   │                   │
   │◀── hint ────────── │                       │                       │                   │
   │                    │                       │                       │                   │
   │   {"type":"run"}   │── coding_interview_graph ▶│                   │                   │
   │                    │                       │── run_node ──────────▶│                   │
   │                    │                       │◀── results ────────── │                   │
   │                    │                       │── run_hint (LLM)      │                   │
   │◀── hint+results ── │                       │                       │                   │
   │                    │                       │                       │                   │
   │── POST /coding ──▶ │                       │                       │                   │
   │   /submit           │── evaluate_code ─────────────────────────── ▶│                   │
   │                    │   (ALL test cases)    │                       │                   │
   │                    │◀── score ──────────────────────────────────── │                   │
   │                    │── save to Firestore ──────────────────────────────────────────▶  │
   │◀── {score,results}│                       │                       │                   │
```

---

## 11. Deployment Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                        PRODUCTION TOPOLOGY                          │
│                                                                     │
│   ┌─────────────────────────┐     ┌─────────────────────────────┐  │
│   │        VERCEL            │     │          RENDER              │  │
│   │                          │     │                              │  │
│   │  ┌────────────────────┐ │     │  ┌────────────────────────┐ │  │
│   │  │  React Frontend    │ │     │  │   FastAPI + Uvicorn    │ │  │
│   │  │  (Static Build)    │ │     │  │                        │ │  │
│   │  └────────────────────┘ │     │  │  • REST API endpoints  │ │  │
│   │                          │     │  │  • WebSocket endpoints │ │  │
│   │  ┌────────────────────┐ │     │  │  • AI Processing       │ │  │
│   │  │  Serverless API    │ │     │  │  • Auth Validation     │ │  │
│   │  │  Functions         │ │     │  │                        │ │  │
│   │  │  (REST proxy)      │─┼─────┼─▶│  Port: 10000 (default) │ │  │
│   │  └────────────────────┘ │     │  └────────────────────────┘ │  │
│   │                          │     │                              │  │
│   │  Auto-deploy from Git   │     │  ┌────────────────────────┐ │  │
│   │  CDN + Edge Network     │     │  │   Code Runner Service  │ │  │
│   │                          │     │  │   (Separate instance)  │ │  │
│   └─────────────────────────┘     │  └────────────────────────┘ │  │
│                                    │                              │  │
│                                    │  Auto-deploy from Git        │  │
│                                    │  Persistent server (always on)│  │
│                                    └─────────────────────────────┘  │
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐                       │
│   │    FIREBASE       │  │    SUPABASE       │                       │
│   │                   │  │                   │                       │
│   │  • Auth service   │  │  • Storage bucket │                       │
│   │  • Firestore DB   │  │    ("resume")     │                       │
│   │  • Admin SDK      │  │  • Signed URLs    │                       │
│   └──────────────────┘  └──────────────────┘                       │
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐                       │
│   │   OPENROUTER      │  │    TAVILY         │                       │
│   │                   │  │                   │                       │
│   │  • LLM inference  │  │  • Web research   │                       │
│   │  • ChatOpenAI     │  │  • Topic research │                       │
│   │    compatible     │  │                   │                       │
│   └──────────────────┘  └──────────────────┘                       │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 11.1 Render Services

| Service              | Type             | Purpose                                 |
|---------------------|------------------|------------------------------------------|
| **FastAPI Backend**  | Web Service      | Core API + WebSocket + AI processing     |
| **Code Runner**      | Web Service      | Isolated code execution (`httpx` client)  |

**Render Configuration:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- **Environment:** Python 3.11+
- **Environment Variables:** All secrets from `.env`

### 11.2 Vercel Services

| Service              | Type                  | Purpose                            |
|---------------------|----------------------|-------------------------------------|
| **Frontend**         | Static Site (Vite)   | React UI, deployed via CDN          |
| **API Functions**    | Serverless Functions | Lightweight REST proxy to Render    |

---

## 12. Error Handling & Scalability

### 12.1 Error Handling Strategy

#### HTTP Error Handling

```
┌────────────────────────────────────────────────────────┐
│                   Error Handling Layers                  │
│                                                         │
│  Layer 1: Auth Errors                                   │
│  ├── 401 Unauthorized → "Invalid or expired token"      │
│  └── Applied via Depends(get_current_user)              │
│                                                         │
│  Layer 2: Validation Errors                             │
│  ├── 422 Unprocessable Entity → Pydantic auto-validation│
│  └── Request body schema mismatch                       │
│                                                         │
│  Layer 3: Business Logic Errors                         │
│  ├── ValueError → "User not found"                      │
│  ├── ValueError → "Resume not parsed yet"               │
│  └── 404 Not Found → "Technical set not found"          │
│                                                         │
│  Layer 4: External Service Errors                       │
│  ├── Supabase upload retry (5 attempts, 3s backoff)     │
│  ├── Code Runner timeout (60s via httpx)                │
│  └── LLM invocation failures                            │
│                                                         │
│  Layer 5: Generic Exception Handler                     │
│  └── 500 Internal Server Error (catch-all)              │
└────────────────────────────────────────────────────────┘
```

#### WebSocket Error Handling

```python
# Pattern used across all 3 WS endpoints:

# 1. Auth failure → close(code=1008)
if not token:
    await websocket.close(code=1008)
    return

# 2. JSON parse error → send error response, continue loop
except json.JSONDecodeError:
    await websocket.send_json({"error": "Invalid JSON"})
    continue

# 3. Processing error → send error response, continue loop
except Exception as e:
    await websocket.send_json({"error": "Processing failed"})

# 4. Connection lost → outer try/except catches disconnect
except Exception as e:
    print("WS CLOSED:", e)
```

#### Code Execution Error Handling

```python
# Network / timeout errors
except httpx.RequestError as e:
    return {"status": "error", "error": f"Code runner connection failed: {str(e)}"}

# Unexpected server errors
if response.status_code != 200:
    return {"status": "error", "error": response.text}

# Runtime errors in user code
if exit_code != 0:
    return {"status": "failed", "error": stderr}
```

### 12.2 Scalability Considerations

```
┌────────────────────────────────────────────────────────────────┐
│                    SCALABILITY ARCHITECTURE                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  HORIZONTAL SCALING (Current)                            │  │
│  │  ├── Render: auto-scaling web services                   │  │
│  │  ├── Vercel: serverless (infinite scale)                 │  │
│  │  ├── Firestore: auto-scales reads/writes                 │  │
│  │  └── Supabase: managed storage scaling                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  PERFORMANCE PATTERNS (Implemented)                      │  │
│  │  ├── LRU cache for settings (loaded once)                │  │
│  │  ├── Async I/O throughout (FastAPI + asyncio)            │  │
│  │  ├── Parallel Tavily research (asyncio.gather)           │  │
│  │  ├── httpx.AsyncClient for code execution                │  │
│  │  ├── Firestore merge writes (no full doc overwrites)     │  │
│  │  ├── LLM structured output (no manual JSON parsing)      │  │
│  │  └── WebSocket: skip hint if code diff < 8 chars         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  RESILIENCE PATTERNS (Implemented)                       │  │
│  │  ├── Supabase upload: 5-retry with 3-second backoff      │  │
│  │  ├── Code Runner: 60-second timeout per execution        │  │
│  │  ├── WS: graceful degradation on processing errors       │  │
│  │  ├── WS: auth failure → immediate close(1008)            │  │
│  │  └── Early exit on compile errors (coding preview)       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  FUTURE SCALING RECOMMENDATIONS                          │  │
│  │  ├── Add Redis for session caching and rate limiting      │  │
│  │  ├── Move code execution to containerized sandbox         │  │
│  │  ├── Add message queue for async AI processing            │  │
│  │  ├── Implement connection pooling for Firestore           │  │
│  │  ├── Add health check endpoints for all external services │  │
│  │  └── Implement WebSocket connection limits per user       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 12.3 CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Open for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> ⚠️ **Production Recommendation:** Replace `allow_origins=["*"]` with specific frontend domains.

### 12.4 Environment Variables

| Variable                    | Purpose                                    |
|----------------------------|--------------------------------------------|
| `OPENAI_API_KEY`           | OpenRouter API key                         |
| `OPENAI_API_BASE`          | OpenRouter base URL                        |
| `LLM_MODEL`               | Model identifier                           |
| `TAVILY_API_KEY`           | Tavily search API key                      |
| `FIREBASE_CREDENTIALS`    | Firebase service account (JSON string)     |
| `SUPABASE_URL`            | Supabase project URL                       |
| `SUPABASE_SERVICE_ROLE_KEY`| Supabase service role key                 |

---

## 📎 Appendix

### A. Dependencies (`requirements.txt`)

```
fastapi              # Web framework
uvicorn              # ASGI server
pydantic             # Data validation
pydantic-settings    # Environment config
python-dotenv        # .env file loading
python-multipart     # File upload support
firebase-admin       # Firebase Auth + Firestore
supabase             # Supabase storage client
langchain            # AI framework
langchain-openai     # OpenAI/OpenRouter integration
langchain-core       # Core abstractions
langchain-community  # Community integrations
langgraph            # AI workflow graphs
PyPDF2               # PDF text extraction
requests             # HTTP client (sync)
tavily               # Web research API
```

### B. Quick Reference — Key File Paths

| Purpose                        | File Path                                        |
|-------------------------------|--------------------------------------------------|
| App Entry Point               | `app/main.py`                                    |
| Central Router                | `app/api/router.py`                              |
| Firebase Init + Token Verify  | `app/core/firebase.py`                           |
| Auth Dependencies             | `app/core/security.py`                           |
| LLM Configuration             | `app/services/llm/llm_core.py`                   |
| Technical Graph                | `app/services/technical/technical_graph.py`       |
| Coding Graph                   | `app/services/coding/coding_graph.py`            |
| Coding Interview Graph         | `app/services/coding/coding_interview_graph.py`  |
| HR Graph                       | `app/services/hr/hr_graph.py`                    |
| Code Execution Client          | `app/services/coding/code_execution_service.py`  |
| Supabase Client                | `app/core/supabase_client.py`                    |
| Settings                       | `app/core/config.py`                             |

---

> **Document generated from actual codebase analysis.**  
> **AI Interview Preparation Platform — Backend Architecture v1.0.0**
