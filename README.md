# Lead Management API — FastAPI

A simple, production-ready REST API for managing sales leads. Built with **Python**, **FastAPI**, and **SQLite** (via `aiosqlite`).

---

## Tech Stack

| Layer      | Choice              | Why                                                |
|------------|---------------------|----------------------------------------------------|
| Language   | Python 3.11+        | Modern, type-safe Python                           |
| Framework  | FastAPI 0.111        | Auto docs, async, Pydantic validation built-in     |
| Database   | SQLite (aiosqlite)  | Zero-setup, async-friendly, perfect for demos      |
| Validation | Pydantic v2         | Declarative, fast, integrated with FastAPI         |
| Server     | Uvicorn             | ASGI server, production-grade                      |

---

## Design Decisions

**SQLite over PostgreSQL** — the problem statement asked for a lightweight database. SQLite requires zero setup, no running server, and the database creates itself on first run. For a lead management system at this scale it's the right tool. Swapping to PostgreSQL later only requires changing two files.

**PATCH over PUT for status updates** — PUT replaces an entire resource, which would require sending all lead fields just to change one. PATCH updates only what you send. Since status updates are a specific action on a lead, PATCH is the correct choice.

**Single URL per resource** — `POST /api/leads` and `GET /api/leads` use the same URL. The HTTP method defines the action, the URL defines the resource. This is core REST design — no `/createLead` or `/getLeads` needed.

**Validation at the schema layer** — all input validation lives in Pydantic schemas, not in route functions or SQL. This means invalid requests are rejected before any business logic or database call runs, and error messages are consistent and automatic.

**UTC timestamps** — `created_at` and `updated_at` are stored in UTC, not local time. A server should never store local time since users and servers can be in different timezones. The frontend converts UTC to local time for display.

**`updated_at` via a database trigger** — instead of updating this field in Python code, a SQLite trigger handles it automatically after every UPDATE. This means it's impossible to update a lead and forget to update the timestamp.

---

## Project Structure

```
lead-management-fastapi/
├── app/
│   ├── main.py
│   ├── routers/
│   │   └── leads.py
│   ├── models/
│   │   └── lead.py
│   ├── schemas/
│   │   └── lead.py
│   └── db/
│       └── database.py
├── data/
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Create and activate a virtual environment

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server

Development (auto-reload on file changes):

```bash
uvicorn app.main:app --reload
```

Production:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

The server starts on **http://localhost:8000** by default.

> **Bonus**: FastAPI auto-generates interactive API docs at:
> - **Swagger UI**: http://localhost:8000/docs
> - **ReDoc**: http://localhost:8000/redoc

---

## API Reference

### Base URL
```
http://localhost:8000/api
```

---

### `POST /api/leads` — Create a lead

**Request body:**

| Field     | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| `name`    | string | ✅       | Full name of the lead                |
| `email`   | string | ✅       | Unique email address                 |
| `company` | string |          | Company name                         |
| `phone`   | string |          | Phone number                         |
| `source`  | string |          | Where the lead came from (e.g. `"LinkedIn"`) |
| `notes`   | string |          | Free-text notes                      |

**Example:**
```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@acmecorp.com",
    "company": "Acme Corp",
    "phone": "+1 555 000 1234",
    "source": "LinkedIn"
  }'
```

**Response `201 Created`:**
```json
{
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "Jane Smith",
    "email": "jane@acmecorp.com",
    "company": "Acme Corp",
    "phone": "+1 555 000 1234",
    "source": "LinkedIn",
    "status": "new",
    "notes": null,
    "created_at": "2024-03-15T10:00:00Z",
    "updated_at": "2024-03-15T10:00:00Z"
  }
}
```

---

### `GET /api/leads` — Fetch all leads

**Query parameters (all optional):**

| Param    | Default      | Description                                          |
|----------|--------------|------------------------------------------------------|
| `status` | —            | Filter by status (see valid values below)            |
| `sort`   | `created_at` | Sort by: `created_at`, `updated_at`, `name`, `status`|
| `order`  | `desc`       | `asc` or `desc`                                      |
| `limit`  | `50`         | Max results (1–200)                                  |
| `offset` | `0`          | Pagination offset                                    |

**Examples:**

All leads:

```bash
curl http://localhost:8000/api/leads
```

Only qualified leads:

```bash
curl "http://localhost:8000/api/leads?status=qualified"
```

Page 2 of 10 results per page:

```bash
curl "http://localhost:8000/api/leads?limit=10&offset=10"
```

**Response `200 OK`:**
```json
{
  "data": [],
  "meta": {
    "total": 42,
    "limit": 50,
    "offset": 0
  }
}
```

---

### `GET /api/leads/{id}` — Fetch a single lead

```bash
curl http://localhost:8000/api/leads/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

**Response `200 OK`:** `{ "data": { ...lead } }`  
**Response `404 Not Found`:** `{ "detail": "Lead not found." }`

---

### `PATCH /api/leads/{id}/status` — Update lead status

**Valid statuses:** `new` → `contacted` → `qualified` → `converted` or `lost`

**Request body:**

| Field    | Type   | Required | Description              |
|----------|--------|----------|--------------------------|
| `status` | string | ✅       | New status for the lead  |
| `notes`  | string |          | Update or add notes      |

**Example:**
```bash
curl -X PATCH http://localhost:8000/api/leads/f47ac10b-58cc-4372-a567-0e02b2c3d479/status \
  -H "Content-Type: application/json" \
  -d '{ "status": "contacted", "notes": "Called Monday, follow up Friday." }'
```

**Response `200 OK`:** `{ "data": { ...updated lead } }`

---

### `GET /health` — Health check

```bash
curl http://localhost:8000/health
```

Example response: `{ "status": "ok" }`

---

## Lead Status Lifecycle

```
new → contacted → qualified → converted
                           ↘ lost
```

| Status      | Meaning                                  |
|-------------|------------------------------------------|
| `new`       | Just created, not yet reached out to     |
| `contacted` | Initial outreach made                    |
| `qualified` | Confirmed interest / budget / fit        |
| `converted` | Became a customer                        |
| `lost`      | Not moving forward                       |

---

## Error Responses

FastAPI returns validation errors automatically from Pydantic:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required"
    }
  ]
}
```

Custom HTTP errors use the same `detail` key:

```json
{ "detail": "Lead not found." }
```

| HTTP Code | When it happens                        |
|-----------|----------------------------------------|
| `404`     | Lead not found                         |
| `409`     | Email already exists                   |
| `422`     | Request body failed Pydantic validation|
| `500`     | Unexpected server error                |

---

## What I Learned Building This

**Async programming** — regular Python is blocking, meaning one slow database call freezes everything. Using `async def` and `aiosqlite` means the server handles other requests while waiting on the database instead of sitting idle.

**REST design** — a single URL like `/api/leads` handles both creating and listing leads depending on the HTTP method (`POST` vs `GET`). You don't need separate URLs like `/createLead` and `/getLeads`. The method is the action, the URL is the resource.

**Pydantic** — instead of manually checking if fields are present and valid, you declare the shape of your data as a class and FastAPI rejects invalid requests automatically before your code even runs.

**SQLite** — a full relational database that lives in a single file. No installation, no running server, no config. The database creates itself on first startup.

---

## Future Scope

- **Authentication** — API key middleware to restrict access
- **Tests** — integration tests with `pytest` and `httpx`
- **PostgreSQL** — swap `aiosqlite` for `asyncpg` in two files for production scale
- **Search** — filter leads by company name or source
- **Delete endpoint** — `DELETE /api/leads/{id}`
