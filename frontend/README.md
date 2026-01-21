# Bear's Den Pro Mode - React Frontend

This is the Next.js/React frontend for Bear's Den, providing a more professional UI compared to the Streamlit version.

## Prerequisites

- **Node.js 18+**: Download from https://nodejs.org/
- **Python 3.10+**: For running the FastAPI backend

## Quick Start

### 1. Install Node.js dependencies

```bash
cd frontend
npm install
```

### 2. Start the FastAPI backend (in a separate terminal)

```bash
# From the project root
cd ..
pip install fastapi uvicorn python-jose[cryptography]
uvicorn api.main:app --reload --port 8000
```

### 3. Start the Next.js frontend

```bash
# From the frontend folder
npm run dev
```

### 4. Open in browser

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard
│   ├── login/page.tsx     # Login page
│   ├── heroes/page.tsx    # Hero Tracker
│   └── settings/page.tsx  # Settings
├── components/            # Reusable React components
│   ├── Sidebar.tsx
│   ├── PageLayout.tsx
│   ├── Expander.tsx       # Collapsible sections
│   └── HeroCard.tsx       # Hero display card
├── lib/                   # Utilities
│   ├── api.ts            # API client
│   └── auth.tsx          # Auth context
└── tailwind.config.js    # Tailwind with Warm Dark theme
```

## Color Theme (Warm Dark)

The theme uses a warm dark palette that maintains Bear's Den identity:

- **Background**: `#18181b` (zinc-900)
- **Surface**: `#27272a` (zinc-800)
- **Accent**: `#f59e0b` (amber-500)
- **Primary**: `#3b82f6` (blue-500)

Hero classes are color-coded:
- Infantry: Red
- Lancer: Green
- Marksman: Blue

## Running Both Modes

You can run both Streamlit (Game Mode) and React (Pro Mode) simultaneously:

| Mode | Port | Command |
|------|------|---------|
| Game Mode (Streamlit) | 8501 | `streamlit run app.py` |
| Pro Mode API | 8000 | `uvicorn api.main:app --reload` |
| Pro Mode Frontend | 3000 | `npm run dev` (in frontend/) |

## Development Notes

- The frontend shares the same database as Streamlit
- JWT tokens are used for authentication (stored in localStorage)
- All API calls go through `/api/*` endpoints
- Images are served as base64 from the API
