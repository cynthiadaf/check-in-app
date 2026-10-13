Act as a senior full-stack engineer and generate a complete production-quality sample application.

Application Name:
Guest Check-In Manager

Technology Requirements:
- Frontend: Plain HTML, CSS and Vanilla JavaScript (no React)
- Backend: Python FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Migrations: Alembic
- Containerization: Docker and Docker Compose
- API Documentation: Swagger/OpenAPI via FastAPI
- Responsive UI optimized for:
  - Mobile phones
  - iPad/tablets
  - Desktop

Business Context:
This application is for restaurants, gyms, hotels, event venues, and similar businesses that need to record guest check-ins.

Generate the complete application source code and project structure.

--------------------------------------------------
DOMAIN MODEL
--------------------------------------------------

Rename the "Checklist" model to a more appropriate business name.

Use these two models:

1. DailyGuestRegister

Purpose:
Represents a guest register for a specific day.

Fields:
- id (UUID)
- register_date (Date, unique)
- created_at

Rules:
- One register per day
- If a guest is added and today's register does not exist, automatically create it
- Users do not manually create registers

2. GuestEntry

Fields:
- id (UUID)
- register_id (FK to DailyGuestRegister)
- guest_name (required)
- check_in_time (required)
- notes (required on creation)
- payment_method (nullable on creation)
- created_at
- updated_at

Rules:
- check_in_time must be automatically set by the server when created
- users must NOT provide check_in_time
- guest_name cannot be edited after creation
- check_in_time cannot be edited after creation
- notes can be updated
- payment_method can be updated
- payment_method may be null when created

--------------------------------------------------
PAYMENT METHODS
--------------------------------------------------

Create an enum:

- CASH
- CARD
- BANK_TRANSFER
- MOBILE_PAYMENT
- MEMBERSHIP
- NONE
- OTHER

--------------------------------------------------
API REQUIREMENTS
--------------------------------------------------

Create REST APIs for:

GET /api/registers

GET /api/registers/{date}

GET /api/guest-entries

GET /api/guest-entries?date=YYYY-MM-DD

GET /api/guest-entries/{id}

POST /api/guest-entries

PATCH /api/guest-entries/{id}

DELETE /api/guest-entries/{id}

Validation Requirements:
- guest_name required
- notes required
- check_in_time generated automatically
- return proper HTTP status codes
- include error handling

--------------------------------------------------
UI REQUIREMENTS
--------------------------------------------------

Create responsive pages:

1. Guest Entry Page

Purpose:
Create a new guest entry.

Fields:
- Guest Name
- Notes

Do NOT show:
- Check-In Time
- Date

Those fields should be generated automatically.

Submission:
POST to API.

--------------------------------------------------

2. Update Guest Entry Page

Purpose:
Update an existing guest entry.

Editable:
- Notes
- Payment Method

Read only:
- Guest Name
- Check-In Time

--------------------------------------------------

3. Guest Register Page

Purpose:
View all guest entries.

Requirements:
- Responsive table
- Filter by date
- Search by guest name
- Sort by newest first
- Display:
  - Guest Name
  - Check-In Time
  - Notes
  - Payment Method
- View details button
- Edit button

--------------------------------------------------

4. Dashboard Page

Show:
- Today's guest count
- Total guests for selected date
- Most common payment method

--------------------------------------------------
DATABASE
--------------------------------------------------

Use PostgreSQL.

Create:
- SQLAlchemy models
- Pydantic schemas
- CRUD layer
- Service layer
- Repository pattern

--------------------------------------------------
PROJECT STRUCTURE
--------------------------------------------------

Generate a clean project structure such as:

backend/
    app/
        api/
        core/
        db/
        models/
        repositories/
        services/
        schemas/
        main.py
    alembic/
    Dockerfile
    requirements.txt

frontend/
    css/
    js/
    pages/
    index.html
    Dockerfile

docker-compose.yml

--------------------------------------------------
DOCKER REQUIREMENTS
--------------------------------------------------

Generate:

1. Backend Dockerfile
2. Frontend Dockerfile
3. docker-compose.yml

Requirements:
- PostgreSQL container
- FastAPI container
- Frontend container
- Persistent Postgres volume
- Environment variables
- Startup instructions

Ports:
- Frontend: 3000
- Backend: 8000
- Postgres: 5432

--------------------------------------------------
GITIGNORE
--------------------------------------------------

Update .gitignore entries covering:

Python:
- __pycache__/
- .pytest_cache/
- .venv/
- *.pyc
- .env

FastAPI:
- local database files
- coverage files
- build artifacts

--------------------------------------------------
IMPLEMENTATION SAFETY REQUIREMENTS
--------------------------------------------------

The generated application must start successfully with `docker compose up --build`
and must also restart successfully when the existing PostgreSQL volume is retained.

Alembic and Docker requirements:
- The backend Dockerfile must set `WORKDIR /app` and `PYTHONPATH=/app` so that
  `alembic` can import the `app` package when launched from `/app`.
- `alembic.ini` must contain either the complete standard Alembic logging sections
  (`[loggers]`, `[handlers]`, `[formatters]`, etc.) or `alembic/env.py` must not call
  `logging.config.fileConfig()`. Do not reference a missing `formatters` section.
- Use an async Alembic environment compatible with the
  `postgresql+asyncpg://` URL and ensure the migration imports the SQLAlchemy models
  before assigning `target_metadata`.
- The initial migration must be safe on a fresh database and on a database where
  migration startup was interrupted. Create the PostgreSQL enum exactly once:
  define the enum with `postgresql.ENUM(..., name="payment_method")`, call
  `.create(op.get_bind(), checkfirst=True)` before creating tables, and use a
  separate `postgresql.ENUM(..., name="payment_method", create_type=False)` for
  the table column. Never allow table creation to issue a second `CREATE TYPE`.
- Migration `upgrade()` and `downgrade()` must be ordered and reversible. Do not
  mark a migration as complete until all tables, indexes, and enum dependencies
  have been created successfully.
- Do not use `Base.metadata.create_all()` during application startup; schema changes
  must be managed only by Alembic.
- Keep the database service healthcheck and backend `depends_on` health condition so
  migrations run only after PostgreSQL accepts connections.

Before finalizing generated code, verify all of the following:
- Run a fresh-database migration test.
- Run a restart test with the existing PostgreSQL volume and confirm that
  `alembic upgrade head` is a no-op after the first successful migration.
- Confirm the backend reaches `/health` after migrations complete.
- Review generated migration code for duplicate PostgreSQL enum creation and for
  imports that fail when the `alembic` executable is used.

Frontend:
- node_modules/
- dist/
- build/

General:
- .DS_Store
- Thumbs.db
- IDE files
- VSCode files except recommended settings

Docker:
- docker volumes
- logs

--------------------------------------------------
CODE QUALITY
--------------------------------------------------

Requirements:
- Type hints everywhere
- Docstrings
- Clean architecture
- Repository pattern
- Dependency injection
- Error handling
- Input validation
- Responsive CSS
- Mobile-first design
- Comments where useful

--------------------------------------------------
TESTING
--------------------------------------------------

Generate:
- pytest setup
- sample API tests
- test database configuration

--------------------------------------------------
COPILOT TRAINING REQUIREMENTS
--------------------------------------------------

While generating the solution:


1. Explain the generated code architecture.
2. Update README.md md with information about the application

3. Generate all Docker files and local deployment instructions.

4. Provide step-by-step commands to:
   - Run migrations
   - Start Docker Compose
   - Access frontend
   - Access API docs

Produce all code, files, folder structure and documentation needed to run the application locally.

--------------------------------------------------
ADDITIONAL SCOPE AND IMPLEMENTATION DECISIONS
--------------------------------------------------

Authentication and tenancy:
- Authentication and authorization are out of scope.
- This is a single-tenant demonstration application.
- Do not add login, user, role, organization, or permission tables.
- Keep the architecture sufficiently modular that authentication and authorization
  can be added later without redesigning the domain layer.

Versions and dependency policy:
- Use the most recent stable, mutually compatible versions of Python,
  FastAPI, SQLAlchemy 2.x, Pydantic 2.x, Alembic, PostgreSQL, and other
  dependencies available when the application is generated.
- Pin dependency versions in requirements files so the application is
  reproducible.
- Use the latest stable PostgreSQL image available when the application is
  generated, unless a dependency requires a specific supported version.

Date and time rules:
- Store all database timestamps as timezone-aware UTC timestamps.
- The backend server uses UTC.
- The frontend must render timestamps in the UK timezone using
  Europe/London, including daylight-saving behavior.
- API dates use YYYY-MM-DD.
- API timestamps use ISO 8601 format with timezone information.
- Do not display seconds in the frontend; display hours and minutes only.
- The frontend must not reinterpret or silently strip timezone information.

Guest creation rules:
- POST /api/guest-entries always creates an entry in the register for the
  current application date in UTC.
- Clients must not submit a register date or register_id when creating an entry.
- Clients must not submit id, check_in_time, created_at, or updated_at.
- The service creates the current day's register automatically when necessary.
- Register creation must remain safe when concurrent requests attempt to create
  the same day's register.

Dashboard API:
- Add GET /api/dashboard?date=YYYY-MM-DD.
- The endpoint must return the selected date, today's guest count, the selected
  date's guest count, and the most common recorded payment method.
- The selected date defaults to the current UTC date when omitted.
- Exclude null payment methods when calculating the most common payment method.
- Return null for the most common payment method when no non-null payment
  methods have been recorded.
- Define deterministic behavior for ties, document it, and cover it with tests.

Pagination and guest-entry queries:
- GET /api/guest-entries must support date, search, page, and page_size query
  parameters.
- page defaults to 1 and page_size defaults to 25.
- Limit page_size to a maximum of 100 and reject invalid pagination values.
- Search guest names case-insensitively after trimming the search term.
- Sort entries by check_in_time descending by default, with deterministic
  ordering for equal timestamps.
- Return pagination metadata, including items, page, page_size, total, and
  total_pages.
- The frontend must provide usable pagination controls and preserve the active
  date and search filters while changing pages.

Payment method semantics:
- The API uses enum names: CASH, CARD, BANK_TRANSFER, MOBILE_PAYMENT,
  MEMBERSHIP, NONE, and OTHER.
- null means that the payment method has not yet been recorded.
- NONE means that no payment was required or no payment was made.
- OTHER means that a payment method exists but is not represented by another
  enum value.
- Human-readable payment labels must be defined and displayed only in the
  frontend; do not change the API enum values into display labels.

Validation and mutation rules:
- Trim leading and trailing whitespace from text inputs.
- guest_name is required, must contain non-whitespace characters, and may be
  no longer than 200 characters.
- notes is required on creation, must contain non-whitespace characters, and
  may be no longer than 2,000 characters.
- PATCH may update notes and payment_method only.
- guest_name and check_in_time are immutable after creation.
- Reject empty PATCH requests with HTTP 422.
- Reject client-supplied server-managed fields with HTTP 422.
- Reject unknown payment methods with HTTP 422.

Delete and error handling:
- DELETE /api/guest-entries/{id} permanently deletes the entry and returns
  HTTP 204 with no response body.
- Deleting the final entry must not delete its daily register.
- Use consistent JSON errors containing detail and code fields, for example:
  {"detail": "Guest entry not found", "code": "GUEST_ENTRY_NOT_FOUND"}.
- Use HTTP 201 for successful creation, HTTP 200 for reads and updates, HTTP
  204 for deletion, HTTP 404 for missing resources, HTTP 409 for applicable
  conflicts, and HTTP 422 for validation errors.

Frontend architecture and static hosting:
- Use separate static HTML pages for the dashboard, guest register, new guest
  entry, and update guest entry workflows.
- Do not build a React application or use a frontend framework.
- Do not require Node.js, npm, a bundler, or a frontend build step at runtime.
- Serve the static frontend files using the latest stable Nginx image available
  when the application is generated.
- The frontend must read the backend URL from a configurable value such as
  window.APP_CONFIG.API_BASE_URL. Do not hard-code http://localhost:8000 in
  application logic.
- Configure the value appropriately for local Docker Compose use and document
  how to change it.
- Configure backend CORS for the frontend origin.
- Include loading, empty, success, and error states, accessible labels,
  semantic HTML, keyboard navigation, visible focus states, and a confirmation
  step before deletion.
- Use UK timezone labels and display hours and minutes only.

Testing:
- Use pytest and a disposable PostgreSQL database for integration/API tests.
- Provide a configurable TEST_DATABASE_URL.
- Do not substitute SQLite for PostgreSQL in integration tests.
- Test automatic register creation, one-register-per-day behavior, concurrent
  register creation, server-generated check-in times, rejected client-supplied
  check-in times, immutable fields, nullable payment methods, payment method
  semantics, validation, pagination, date filtering, case-insensitive search,
  dashboard aggregation, missing resources, updates, and deletion.

Container startup and migrations:
- Docker Compose must include a PostgreSQL health check.
- The backend must wait for PostgreSQL readiness before starting.
- For this learning demonstration, backend startup must run Alembic migrations
  automatically before starting FastAPI.
- Also document the equivalent manual Alembic migration command for local
  development and troubleshooting.
- Provide backend and database health checks where practical.