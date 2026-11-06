# Guest Check-In Manager: Auth, Billing, React, and Deployment Plan

## 1. Agreed decisions

- One registered user owns one independent account.
- Email verification is required before the account becomes active.
- The subscription is a Standard plan.
- Billing options:
  - £5 per month.
  - £50 per year as the initial annual price assumption.
- Mollie is the payment provider.
- The frontend will be migrated from static HTML and vanilla JavaScript to React.
- Development placeholders:
  - Frontend: `app.guest-checkin.local`
  - API: `api.guest-checkin.local`
- Production domains will remain configurable placeholders until the real Cloudflare domain is supplied.

The local `.local` names are development labels only. They are not public Mollie webhook URLs and will require hosts-file entries or a local HTTPS tunnel when testing Mollie callbacks.

## 2. Target architecture

```text
React/Vite frontend
        |
        | HTTPS / JSON API
        v
FastAPI application
  - authentication
  - account ownership
  - guest registers
  - subscription and Mollie integration
        |
        v
PostgreSQL

Mollie ------------> FastAPI Mollie webhook endpoint
Email provider ----> verification and password-reset messages
Cloudflare --------> DNS, TLS proxy, and production edge
```

The backend remains responsible for authorization, subscription state, payment verification, and all business rules. The React application only presents state and starts user-facing flows.

## 3. Backend domain changes

### 3.1 Account and authentication models

Add SQLAlchemy models under `backend/app/models/`:

- `User`
  - UUID primary key.
  - Normalized, unique email address.
  - Argon2id password hash.
  - `is_active` and `email_verified_at` fields.
  - Created and updated timestamps.
- `AuthSession`
  - UUID primary key.
  - User foreign key.
  - Hash of an opaque session token.
  - Expiry, revoked-at, created-at, and last-used timestamps.
  - Store only the token hash in PostgreSQL.
- `EmailVerificationToken`
  - Hashed, single-use token.
  - Expiry and consumed-at timestamps.
- `PasswordResetToken`
  - Hashed, single-use token.
  - Expiry and consumed-at timestamps.

Use secure HTTP-only cookies for browser sessions. Cookies must be `Secure` and use an appropriate `SameSite` policy in production. Add CSRF protection for state-changing cookie-authenticated requests.

### 3.2 Account ownership

Add `user_id` to `DailyGuestRegister`, or introduce an `Account` model if future multi-user expansion is expected. For the agreed one-user-per-account scope, the simpler design is:

- `DailyGuestRegister.user_id` foreign key to `users.id`.
- Unique constraint on `(user_id, register_date)`.
- Every guest-entry query filters through the authenticated user's ID.
- Existing data migration assigns legacy rows to a configured migration user or requires an explicit migration step before deployment.

Guest entries remain associated through their register and do not need a duplicate user foreign key.

### 3.3 Subscription and billing models

Add models under `backend/app/models/`:

- `SubscriptionPlan`
  - Stable code such as `STANDARD_MONTHLY` or `STANDARD_YEARLY`.
  - Currency `GBP`.
  - Price in minor units: `500` or `5000`.
  - Billing interval: month or year.
  - Active flag.
- `Subscription`
  - User foreign key.
  - Plan foreign key.
  - Mollie customer ID.
  - Mollie subscription ID, when recurring billing is established.
  - Status: pending, active, past_due, cancelled, expired, or failed.
  - Current period start/end and cancellation timestamp.
- `Payment`
  - User and subscription foreign keys.
  - Mollie payment ID, unique.
  - Amount, currency, status, and payment type.
  - Raw provider metadata where appropriate.
- `MollieWebhookEvent`
  - Mollie object ID and event type.
  - Processing status, attempts, processed-at, and error details.
  - Unique provider event/object key for idempotency.

Never trust payment status from the browser. The webhook handler must retrieve the payment or subscription from Mollie using the server-side API key before updating local state.

### 3.4 Configuration

Extend `backend/app/core/config.py` with environment-driven settings for:

- Session cookie name, signing/secrets, secure-cookie mode, and session expiry.
- Email verification URL and frontend URL.
- Email provider configuration, with a development console adapter.
- Mollie API key, profile ID if required, webhook URL, and redirect URL.
- Standard plan prices and identifiers.
- Allowed CORS origins.

Secrets must never be committed or exposed to React.

## 4. Authentication API

Add an `auth` router under `backend/app/api/`:

- `POST /api/auth/register`
  - Validate and normalize email.
  - Hash password.
  - Create inactive user.
  - Generate a verification token.
  - Send a verification email through the configured email service.
- `GET /api/auth/verify-email?token=...`
  - Consume a valid token and activate the user.
- `POST /api/auth/login`
  - Reject unverified or inactive users.
  - Create a session and set the HTTP-only cookie.
- `POST /api/auth/logout`
  - Revoke the current session and clear the cookie.
- `GET /api/auth/me`
  - Return the authenticated user and subscription summary.
- `POST /api/auth/request-password-reset`
  - Always return a non-enumerating response.
- `POST /api/auth/reset-password`
  - Consume a valid reset token and revoke existing sessions.

Use consistent error objects with `detail` and `code`, while avoiding disclosure of whether an email is registered in reset and verification-related flows.

Add an authenticated dependency in `backend/app/api/deps.py` and apply it to all guest and billing routes that require a logged-in user.

## 5. Billing API and Mollie flow

Add a `billing` router and service layer:

- `GET /api/billing/plans`
  - Return active Standard monthly and annual plans.
- `GET /api/billing/subscription`
  - Return the current user's subscription state.
- `POST /api/billing/checkout`
  - Accept a plan code.
  - Create or reuse a Mollie customer.
  - Create a first payment with a checkout redirect.
  - Persist a pending payment and subscription.
  - Return the Mollie checkout URL.
- `POST /api/billing/cancel`
  - Cancel at the provider and locally record the requested cancellation.
- `POST /api/billing/webhooks/mollie`
  - Accept Mollie's callback.
  - Retrieve the provider object server-side.
  - Process the event idempotently.
  - Update payment and subscription state.
  - Return success quickly and log retryable failures.

The first payment establishes the recurring-payment mandate where supported by Mollie. Recurring billing must be created only after the first payment has succeeded and the provider confirms the required mandate/customer state.

Use a development email adapter that logs verification links rather than sending real email. Use Mollie's test API key and test mode during development.

## 6. Guest API changes

Update the existing guest routers, services, repositories, schemas, and queries:

- Require authentication.
- Scope every read, update, and delete to the current user's account.
- Keep server-generated UTC check-in timestamps.
- Keep one register per user per UTC date.
- Preserve the existing pagination, filtering, validation, and payment-method semantics.
- Return `401` for missing or invalid sessions and `403` for inactive/unverified accounts where applicable.
- Decide whether guest operations require an active subscription; recommended default is to require an active subscription after a short account grace period.

Do not use `Base.metadata.create_all()`; all schema changes remain Alembic migrations.

## 7. React frontend migration

Replace the static frontend with a Vite React application under `frontend/`.

Recommended structure:

```text
frontend/
  src/
    api/
    auth/
    billing/
    components/
    pages/
    routes/
    styles/
    App.tsx
    main.tsx
  public/
  package.json
  vite.config.ts
  Dockerfile
```

Required routes:

- `/register`
- `/verify-email`
- `/login`
- `/forgot-password`
- `/reset-password`
- `/billing`
- `/`
- `/registers`
- `/guest-entries/new`
- `/guest-entries/:id/edit`

Frontend behavior:

- Load the authenticated user with `/api/auth/me`.
- Redirect unauthenticated users to login.
- Display verification-required and subscription-required states.
- Provide monthly/yearly Standard plan selection and Mollie checkout redirect.
- Preserve the existing dashboard, guest register, filtering, pagination, editing, and deletion workflows.
- Include loading, empty, success, and error states.
- Use accessible labels, keyboard navigation, visible focus states, and responsive layouts.
- Do not store passwords, Mollie secrets, or long-lived access tokens in browser storage.
- Configure the API base URL through a Vite environment variable or runtime configuration rather than hard-coding localhost.

## 8. Docker Compose environments

### 8.1 Development

Create a development Compose configuration with:

- PostgreSQL with a persistent development volume and exposed port `5432`.
- FastAPI using a development Dockerfile or command with `uvicorn --reload`.
- React Vite dev server on port `3000` with source mounts.
- Backend port `8000`.
- PostgreSQL healthcheck.
- Backend dependency on the healthy database.
- Development email logging adapter.
- Mollie test credentials supplied through `.env.dev`.
- Optional Mailpit service for testing real email flows.

Add hosts-file entries for the dummy names or use `localhost` during development. For Mollie webhook testing, expose the backend through an HTTPS tunnel such as Cloudflare Tunnel and configure that public URL as the Mollie webhook URL.

### 8.2 Production

Create a production Compose configuration with:

- React built into static assets using a multi-stage Node build.
- Nginx serving the React build.
- Nginx proxying `/api` to FastAPI.
- FastAPI running without reload.
- PostgreSQL on a private Docker network with no published port.
- Secrets supplied from the deployment environment or secret files.
- Healthchecks for database, API, and frontend.
- Separate migration job or release command running `alembic upgrade head` before API rollout.
- Persistent PostgreSQL volume and explicit backup policy.

Keep the existing backend `WORKDIR /app`, `PYTHONPATH=/app`, async Alembic setup, and safe enum migration behavior.

## 9. Cloudflare deployment

Configure Cloudflare with:

- `app.<real-domain>` pointing to the production Nginx origin.
- `api.<real-domain>` pointing to the API/reverse-proxy origin, or route both through the same Nginx origin.
- Proxy enabled for web traffic.
- SSL/TLS mode `Full (strict)`.
- Origin certificate installed at the origin.
- CORS restricted to the frontend origin.
- DNS-only or otherwise supported handling for any infrastructure that cannot be proxied.
- Mollie webhook URL using the public API hostname.

Cloudflare should provide DNS and edge TLS, but application authentication, authorization, webhook verification, and payment-state validation remain backend responsibilities.

## 10. Alembic migrations

Create migrations in this order:

1. Users, sessions, verification tokens, and password-reset tokens.
2. Add user ownership to daily registers and backfill or explicitly handle existing records.
3. Subscription plans, subscriptions, payments, and webhook events.
4. Indexes and unique constraints for email, provider IDs, account/date, and session lookup.

Each migration must be restart-safe and reversible where practical. Seed the two Standard plan records through a migration or a controlled application startup command, not through request handling.

Review every migration for:

- Correct imports when invoked by the `alembic` executable.
- No duplicate PostgreSQL enum creation.
- Correct transaction ordering.
- Safe behavior after an interrupted migration.
- Existing-volume restart compatibility.

## 11. Testing plan

### Backend unit and integration tests

Add PostgreSQL-backed tests for:

- Registration validation and password hashing.
- Duplicate email handling.
- Email verification and token expiry.
- Login, logout, session expiry, and invalid sessions.
- Password reset without account enumeration.
- Guest isolation between users.
- Automatic per-user register creation.
- Existing guest validation, pagination, filtering, dashboard, update, and delete behavior.
- Plan listing and checkout creation.
- Mollie webhook success, failure, cancellation, retries, and duplicate delivery.
- Subscription access enforcement.
- Payment status changes that originate only from provider verification.

Use a configurable disposable PostgreSQL database through `TEST_DATABASE_URL`; do not substitute SQLite.

### Frontend tests

Add tests for:

- Registration and login form validation.
- Verification-required state.
- Authenticated route protection.
- Plan selection and checkout redirect handling.
- Subscription-required state.
- Guest register filters and pagination.
- API error and loading states.

### Deployment checks

Verify:

1. Fresh development database migration.
2. Restart with the existing PostgreSQL volume.
3. Second `alembic upgrade head` is a no-op.
4. `/health` is available after startup.
5. React production build succeeds.
6. Production Nginx serves the SPA routes.
7. API requests reach FastAPI through the Nginx `/api` proxy.
8. Mollie test webhook processing is idempotent.
9. Cloudflare-origin TLS and CORS settings work with the real domain configuration.

## 12. Documentation updates

Update `README.md` with:

- React, FastAPI, PostgreSQL, Mollie, and Docker architecture.
- Development and production Compose commands.
- Environment variable reference.
- Hosts-file or tunnel setup for dummy domains.
- Mollie test-mode setup and webhook configuration.
- Email verification development behavior.
- Alembic migration commands.
- Cloudflare DNS, TLS, and origin configuration.
- Security requirements for production secrets, cookies, backups, and webhook endpoints.

## 13. Implementation order

1. Add authentication models, migrations, password hashing, sessions, and API routes.
2. Add email verification with a development logging adapter.
3. Add user ownership to guest registers and enforce authenticated queries.
4. Add subscription and payment models, plan seed data, and Mollie service abstraction.
5. Add checkout and idempotent webhook processing using Mollie test mode.
6. Migrate the frontend to React/Vite and implement auth screens.
7. Implement subscription screens and access-state handling.
8. Rebuild dashboard, registers, and guest-entry workflows in React.
9. Add development and production Compose files and Nginx routing.
10. Update Cloudflare-ready configuration and documentation.
11. Run the complete migration, API, frontend, billing, and deployment verification suite.

## 14. Definition of done

The implementation is complete when a new user can register, verify their email, log in, select either Standard billing interval, complete Mollie test checkout, return to the React application, and use only their own guest registers. The application must run through the development Compose stack, build and serve through the production stack, process duplicate Mollie webhooks safely, and document the Cloudflare configuration needed to replace the dummy domains.
