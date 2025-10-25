# Government Feed - Architecture Documentation

## Panoramica Architetturale

Government Feed segue i principi della **Clean Architecture** con separazione netta tra domain logic, infrastructure e presentation layer.

## Principi Guida

### 1. Separazione dei Concerns
- **Core Domain**: Logica di business pura, zero dipendenze esterne
- **Infrastructure**: Implementazioni concrete (database, AI, feed parsing)
- **API Layer**: Esposizione HTTP delle funzionalità
- **Frontend**: Interfaccia utente separata dal backend

### 2. Dependency Inversion
- Le dipendenze puntano verso il centro (domain)
- Infrastructure dipende da Core, non viceversa
- Interfacce astratte nel core, implementazioni concrete in infrastructure

### 3. Testabilità
- Repository pattern per astrarre data access
- Dependency injection per sostituire componenti nei test
- Business logic isolata e testabile in isolamento

### 4. Scalabilità
- Architettura stateless per l'API
- Database relazionale per integrità dati
- Caching layer per performance
- Background workers per elaborazioni async

## Stack Tecnologico Completo

### Backend (Python 3.13)
- **FastAPI**: Framework web async con validazione automatica
- **SQLAlchemy 2.0**: ORM con supporto async
- **Pydantic**: Validazione dati e serializzazione
- **Uvicorn**: ASGI server ad alte prestazioni
- **Alembic**: Database migrations

### Frontend (React 18 + TypeScript)
- **React 18**: UI library con concurrent features
- **TypeScript**: Type safety end-to-end
- **Vite**: Build tool ultra-veloce
- **React Query**: State management e caching
- **TailwindCSS**: Utility-first CSS framework (pianificato)

### Database
- **SQLite**: Sviluppo locale
- **PostgreSQL**: Produzione
- **Redis**: Caching layer (configurato, non ancora implementato)

### AI/ML
- **Ollama**: Runtime per LLM locali
- **DeepSeek-R1 7B**: Modello principale per riassunti
- **httpx**: Client HTTP async per chiamate Ollama

### Testing
- **pytest**: Framework di testing
- **pytest-asyncio**: Supporto test async
- **pytest-cov**: Code coverage
- **pytest-mock**: Mocking framework

### Tools
- **ruff**: Linter e formatter velocissimo
- **mypy**: Static type checking
- **pnpm**: Package manager per frontend

## Struttura del Progetto

### Backend Structure
```
backend/
├── src/
│   ├── core/                    # Domain layer
│   │   ├── entities.py          # Domain models (NewsItem, Source, Category)
│   │   └── repositories/        # Abstract interfaces
│   │       ├── news_repository.py
│   │       └── source_repository.py
│   │
│   ├── infrastructure/          # Implementation layer
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # ORM models
│   │   ├── repositories/        # Concrete implementations
│   │   │   ├── news_repository.py
│   │   │   └── source_repository.py
│   │   ├── unit_of_work.py      # Transaction management
│   │   ├── feed_parser.py       # RSS/Atom parsing
│   │   ├── ai_service.py        # Ollama integration
│   │   └── settings_store.py    # Configuration persistence
│   │
│   └── api/                     # Presentation layer
│       ├── main.py              # FastAPI app + endpoints
│       ├── schemas.py           # Pydantic models
│       └── dependencies.py      # DI helpers
│
├── tests/                       # Test suite (da implementare)
└── pyproject.toml               # Dependencies e configurazione
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/              # React components (da sviluppare)
│   ├── hooks/                   # Custom React hooks
│   ├── services/                # API client
│   ├── types/                   # TypeScript types
│   └── App.tsx                  # Root component
│
├── public/                      # Static assets
├── package.json                 # Dependencies
└── vite.config.ts               # Build configuration
```

### Shared Modules
```
shared/
└── logging/                     # Centralized logging
    ├── logger.py                # Logger setup
    └── __init__.py              # Public exports
```

## Design Patterns Implementati

### 1. Repository Pattern
Astrae l'accesso ai dati dal business logic:

**Vantaggi:**
- Testabilità: repository facilmente mockabili
- Flessibilità: cambio database senza toccare business logic
- Manutenibilità: query centralizzate in un unico posto

**Interfacce definite:**
- INewsRepository: gestione NewsItem
- ISourceRepository: gestione Source

**Metodi chiave:**
- get_by_id, get_all, get_recent
- get_by_content_hash (deduplicazione)
- search, get_by_date_range
- add, update, delete

### 2. Unit of Work
Coordina multiple repository e gestisce transazioni:

**Responsabilità:**
- Lazy initialization dei repository
- Commit/rollback centralizzato
- Garantisce consistenza transazionale

**Utilizzo:**
- Ogni endpoint riceve UnitOfWork via dependency injection
- Le operazioni sono atomiche (commit o rollback completo)

### 3. Dependency Injection
FastAPI fornisce DI nativo tramite Depends:

**Pattern:**
- get_db() fornisce sessione database
- get_unit_of_work() fornisce UoW con repository

**Vantaggi:**
- Componenti loosely coupled
- Facile sostituzione per testing
- Lifecycle management automatico

### 4. Structured Logging
Logging centralizzato con formato consistente:

**Features:**
- Timestamp automatico
- Log levels (INFO, WARNING, ERROR)
- Module name per tracciabilità
- Context fields strutturati

**Formato:**
```
[2025-10-25 19:05:08] [INFO] [module.name] Message with context
```

## Database Schema

### Tabelle Principali

**Sources**
- Fonti di notizie istituzionali
- Feed URL per RSS/Atom
- Flag is_active per abilitazione
- Timestamp last_fetched per tracking

**NewsItems**
- Articoli importati dai feed
- Relazione many-to-one con Source
- content_hash per deduplicazione (SHA256)
- published_at per ordinamento cronologico
- summary per riassunto AI

**Categories** (planned)
- Categorizzazione gerarchica
- Relazione many-to-many con NewsItems
- parent_id per struttura ad albero

### Relazioni
- NewsItem → Source (many-to-one)
- NewsItem ↔ Category (many-to-many, future)

### Indici
- content_hash (UNIQUE) per deduplicazione veloce
- published_at per ordinamento
- source_id per query filtrate

## API Endpoints

### Sources Management
- GET /api/sources - Elenco tutte le fonti
- GET /api/sources/{id} - Dettaglio singola fonte
- POST /api/sources - Crea nuova fonte
- PUT /api/sources/{id} - Aggiorna fonte
- DELETE /api/sources/{id} - Elimina fonte
- POST /api/sources/{id}/process - Elabora feed manualmente

### News Access
- GET /api/news - Elenco notizie recenti (con limit)
- GET /api/news/{id} - Dettaglio singola notizia
- POST /api/news/{id}/summarize - Genera riassunto AI

### Settings
- GET /api/settings - Configurazione applicazione
- PUT /api/settings - Aggiorna configurazione
- GET /api/settings/features - Feature flags

### System
- GET / - Health check

## Flow di Elaborazione Feed

### 1. Acquisizione
- Endpoint triggered: POST /api/sources/{id}/process
- FeedParserService scarica il feed RSS/Atom
- Parsing con libreria feedparser (Python)
- Estrazione: title, content, published_at, URL

### 2. Deduplicazione
- Calcolo content_hash (SHA256 di title|content|source|date)
- Query database per hash esistente
- Skip se duplicato, altrimenti procedi

### 3. Arricchimento (AI)
- Fetch contenuto completo da URL (web scraping)
- Fallback su contenuto del feed se scraping fallisce
- Invio a Ollama per riassunto
- Truncate a 2000 caratteri per limiti modello
- Rimozione blocchi di reasoning (DeepSeek specific)

### 4. Persistenza
- Salvataggio via Repository Pattern
- Commit transazione via Unit of Work
- Update timestamp last_fetched su Source

### 5. Logging
- Tracciamento di ogni step
- Metriche: items processed, added, skipped
- Error logging per debugging

## Integrazione AI

### Ollama Setup
- Endpoint locale: http://localhost:11434
- Modello configurabile (default: deepseek-r1:7b)
- Temperatura: 0.3 (output deterministico)
- Max words configurabile (default: 200)

### Prompt Engineering
Richiesta di riassunti:
- Linguaggio italiano
- Stile chiaro e accessibile
- Focus su impatto pratico per cittadini
- Lunghezza controllata

### Ottimizzazioni
- Content truncation (2000 chars)
- HTML stripping per testo pulito
- Caching delle risposte (future)
- Timeout configurabile

## Configurazione

### Backend (settings.json)
- ai_enabled: attiva/disattiva AI
- ollama_endpoint: URL servizio Ollama
- ollama_model: modello da usare
- summary_max_words: lunghezza riassunti

### Database
- SQLite per sviluppo (file-based)
- PostgreSQL per produzione (scalabilità)
- Connection string in database.py

### Logging
- Centralizzato in shared/logging/
- Livello configurabile (INFO default)
- Output su stdout (container-friendly)

## Deployment

### Development
```
1. Backend: uvicorn backend.src.api.main:app --reload
2. Frontend: cd frontend && pnpm dev
3. Ollama: docker-compose up -d
```

### Production (Planned)
- Docker multi-stage build
- Reverse proxy (nginx/traefik)
- Database su PostgreSQL dedicato
- Redis per caching
- Background workers per feed polling

## Security Considerations

### Attuali
- Input validation via Pydantic
- SQL injection protection via ORM
- CORS configurato per frontend locale

### Future
- Rate limiting su API
- API key per accesso esterno
- JWT authentication per multi-user
- Encryption per dati sensibili

## Performance

### Ottimizzazioni Attuali
- Async I/O per API e database
- Lazy loading nei repository
- Indexing su campi chiave

### Prossimi Step
- Redis caching per query frequenti
- Connection pooling ottimizzato
- Query optimization con EXPLAIN
- CDN per static assets (frontend)

## Testing Strategy (Planned)

### Unit Tests
- Domain logic (entities, value objects)
- Repository implementations
- AI service integration

### Integration Tests
- API endpoints end-to-end
- Database transactions
- Feed parsing

### E2E Tests
- Frontend user flows
- Complete workflows (import → summarize → display)

## Monitoring & Observability (Future)

### Logging
- Structured logs già implementati
- Aggregazione con Loki/ELK (future)

### Metrics
- Response times
- Feed processing throughput
- AI inference latency
- Cache hit rates

### Alerting
- Failed feed imports
- AI service down
- Database errors

## Scalability Plan

### Orizzontale
- Stateless API: multiple instances dietro load balancer
- Background workers: pool di worker indipendenti
- Database: read replicas per query heavy loads

### Verticale
- Database tuning (indexes, query optimization)
- Caching aggressivo con Redis
- AI model quantization per memoria ridotta

## Conclusioni

L'architettura attuale di Government Feed è:
- **Solida**: Pattern consolidati e best practices
- **Manutenibile**: Separazione chiara dei layer
- **Scalabile**: Pronta per crescita futura
- **Testabile**: Design che facilita testing

Il progetto è in uno **stato maturo** per le feature core e pronto per l'espansione verso produzione con focus su:
1. Frontend completo
2. Background workers
3. Caching e performance
4. Test coverage
