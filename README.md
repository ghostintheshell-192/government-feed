# Government Feed

An open-source tool that aggregates news and communications from official government and institutional sources.

## Status

Early development. Core functionality in progress.

## Tech Stack

- **Backend**: Python 3.13 + FastAPI
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **AI**: Ollama (local, privacy-first)

## Setup

```bash
# Backend
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -e ".[dev]"

# Frontend
cd frontend
pnpm install

# Services
docker-compose up -d
```

## License

MIT License - See LICENSE file
