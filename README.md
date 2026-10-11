<div align="center">

# TrustBridge

### Transparent humanitarian aid donations on the Stellar blockchain

[![CI](https://github.com/trustbridge-platform/trustbridge/actions/workflows/ci.yml/badge.svg)](https://github.com/trustbridge-platform/trustbridge/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/trustbridge-platform/trustbridge/blob/main/LICENSE)
[![Built on Stellar](https://img.shields.io/badge/built%20on-Stellar-black.svg)](https://stellar.org)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/trustbridge-platform/trustbridge/blob/main/CONTRIBUTING.md)

[Live demo](https://trustbridge-frontend-rzkz.onrender.com) · [Open issues](https://github.com/trustbridge-platform/trustbridge/issues) · [Good first issues](https://github.com/trustbridge-platform/trustbridge/issues?q=is%3Aopen+label%3A%22good+first+issue%22) · [Contributing](https://github.com/trustbridge-platform/trustbridge/blob/main/CONTRIBUTING.md) · [Security](https://github.com/trustbridge-platform/trustbridge/blob/main/SECURITY.md)

</div>

---

**TrustBridge connects donors with humanitarian campaigns and makes every contribution traceable.** Donors browse campaigns and connect a Stellar wallet. Campaign creators publish a goal and receive donations directly to their own wallet. Every payment is verifiable on the public ledger, and administrators can deactivate campaigns that break the platform's guidelines.

**Status: active development, open to contributors.** The core platform is live: accounts, campaigns, wallet connection, transaction history, email notifications and the admin dashboard. The main open workstream is **on-chain signing for Donate and Send** ([#37](https://github.com/trustbridge-platform/trustbridge/issues/37), [#38](https://github.com/trustbridge-platform/trustbridge/issues/38)), which currently runs in a clearly labelled preview mode. The server-side verification behind it is already built and tested. Everything still to do is scoped as an issue with acceptance criteria, so you can pick something up in minutes.

## Contents

[Why TrustBridge](#why-trustbridge) · [Features](#features) · [Status](#status) · [How it works](#how-it-works) · [Wallets](#wallets) · [Tech stack](#tech-stack) · [Quick start](#quick-start) · [Configuration](#configuration) · [API overview](#api-overview) · [Project structure](#project-structure) · [Testing and quality](#testing-and-quality) · [Deployment](#deployment) · [Security](#security) · [Roadmap](#roadmap) · [Contributing](#contributing) · [Community](#community-and-support) · [FAQ](#faq) · [License](#license)

## Why TrustBridge

Donors rarely see where their money goes, and small relief efforts struggle to earn trust. TrustBridge takes a simple approach:

- **Direct and traceable.** Donations go to the campaign's own wallet. Anyone can follow a payment on the ledger.
- **Verified server-side.** The API reads the amount, destination and sender from the signed Stellar transaction itself, so a client cannot claim a different amount than the one actually paid.
- **Honest about its status.** Anything unfinished is labelled in the product and listed below, not hidden.
- **Easy to contribute to.** Setup takes minutes, issues have testable acceptance criteria, and reviews are quick.

## Features

**For donors**
- Browse and search campaigns by category and keyword, with progress toward each goal
- Connect a Freighter or Lobstr wallet and see the account balance and a balance history chart
- Full, filterable transaction history with pagination and CSV export
- Comment on campaigns, and choose which emails to receive (one-click unsubscribe)
- Sign in with email and password or with GitHub

**For campaign creators**
- Publish a campaign with a goal, deadline, category, urgent flag and cover image
- Donations are directed to the campaign's own wallet (defaults to the creator's linked wallet)
- Live progress, donor count and a progress ring on every campaign

**For administrators**
- Platform statistics, a list of all campaigns, and one-click deactivation of campaigns that break the guidelines (deactivated campaigns disappear from the public list)

**Platform**
- Responsive UI with a light and dark theme
- Interface in English, Spanish, French, Arabic and Chinese
- Pages: landing, campaigns, campaign detail, create campaign, dashboard, analytics, transactions, send, receive, profile, settings, admin, and community boards (announcements, bugs, features, general, support, updates)

## Status

| Area | State | Notes |
| --- | --- | --- |
| Email and password accounts (JWT) | Working | bcrypt hashing, rate-limited login, generic error messages |
| GitHub sign-in | Working | Verified emails only, CSRF `state` check |
| Browse and search campaigns | Working | Debounced, API-backed search |
| Create campaigns with image upload | Working | Cloudinary; server-side validation |
| Freighter and Lobstr wallets | Working | Detect, connect, balance |
| Transaction history, filters, CSV export | Working | Paginated; CSV is formula-safe |
| Email notifications (Resend) | Working | Signed one-click unsubscribe |
| Admin dashboard (`/admin`) | Working | Stats, campaign list, deactivate |
| Multilingual UI | Working | English, Spanish, French, Arabic, Chinese |
| **On-chain donations** | **Preview** | API verification done; client signing flow in [#37](https://github.com/trustbridge-platform/trustbridge/issues/37) |
| **Sending XLM** | **Preview** | Same; see [#38](https://github.com/trustbridge-platform/trustbridge/issues/38) |
| Dashboard and Analytics figures | Sample data | Labelled in the UI; real aggregates in [#40](https://github.com/trustbridge-platform/trustbridge/issues/40) |
| xBull and Albedo wallets | Not started | [#34](https://github.com/trustbridge-platform/trustbridge/issues/34), [#35](https://github.com/trustbridge-platform/trustbridge/issues/35) |
| Two-factor authentication | Not started | [#2](https://github.com/trustbridge-platform/trustbridge/issues/2) |

## How it works

```
 Browser (React SPA)                       Express API                      Stellar
+----------------------+   HTTPS / JSON   +-------------------+
| TanStack Start (SPA) | ---------------> | Auth, Campaigns   |
| Freighter / Lobstr   |                  | Transactions      | ---> Horizon (testnet or mainnet)
| extension wallets    | <--------------- | Admin, Email      |
+----------+-----------+                  +---------+---------+
           |  signed transaction (XDR)              |
           +------ POST /campaigns/:id/donate ------+  checks source, destination
                                                    |  and amount in the signed XDR,
                                                    v  then submits and records it
                                              SQLite (better-sqlite3)
```

The donation endpoint accepts exactly one native XLM payment, signed by the donor's linked wallet, sent to the campaign's wallet. Totals are updated in a single atomic SQL statement so concurrent donations cannot overwrite each other.

### Donation verification flow

1. The donor connects a wallet. The API stores the wallet address on the user's profile (validated as a Stellar public key).
2. The client builds a native XLM payment to the campaign's `wallet_address` and has the wallet sign it.
3. The client sends only the signed transaction (XDR) to `POST /api/campaigns/:id/donate`.
4. The API decodes the XDR and **reads the source, destination and amount from the transaction itself**. It rejects anything other than a single native payment, a sender that is not the user's linked wallet, or a destination that is not the campaign's wallet.
5. Only then does it submit the transaction to Horizon and, in one database transaction, record the payment and add the amount to the campaign total (`raised = raised + ?`). When the goal is reached, the campaign becomes `funded`.

Steps 2 and 3 are the part still to build in the UI ([#37](https://github.com/trustbridge-platform/trustbridge/issues/37)); steps 4 and 5 are implemented and covered by tests.

### Authentication

Email and password accounts use bcrypt and signed JWTs. GitHub sign-in asks the API for a consent URL plus a random `state`, which the browser stores and must see returned on the callback. Only emails GitHub has verified are trusted. Login and registration are rate-limited.

### Data model

| Table | Holds |
| --- | --- |
| `users` | Profile, hashed password or GitHub id, wallet address, role (`user` or `admin`), notification preference |
| `campaigns` | Title, description, organization, category, goal, raised, donors, status (`active`, `funded`, `expired`), end date, urgent flag, creator, donation `wallet_address` |
| `transactions` | Hash, from and to addresses, amount, asset, type (`donation`, `send`), status, memo, campaign and user |
| `comments` | Campaign comments with author and timestamps |

The database is a single SQLite file created on first run. Schema changes are applied as small migrations in `backend/src/config/database.js`.

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | React 18, TanStack Start and Router (SPA mode), Vite, TypeScript, Tailwind CSS v4 |
| Backend | Node.js 20+ (ES modules), Express 4, SQLite via `better-sqlite3`, JWT, bcrypt |
| Blockchain | Stellar SDK 16, Horizon, Freighter and Lobstr wallet APIs |
| Services | Resend (email), Cloudinary (images), GitHub OAuth |
| Quality | Node's built-in test runner, GitHub Actions CI |

## Wallets

| Wallet | Support | Install |
| --- | --- | --- |
| Freighter | Detect, connect, balance | [freighter.app](https://www.freighter.app) |
| Lobstr | Detect, connect | [lobstr.co](https://lobstr.co) |
| xBull | Open for contribution ([#34](https://github.com/trustbridge-platform/trustbridge/issues/34)) | |
| Albedo | Open for contribution ([#35](https://github.com/trustbridge-platform/trustbridge/issues/35)); popup-based, not an extension | |

Install the extension, create or import an account, then reload TrustBridge and choose **Connect wallet**. Use a **testnet** account while developing; Friendbot can fund it for free.

## Quick start

**Requirements:** Node.js 20 or newer, npm and Git. Use **testnet** while developing.

```bash
git clone https://github.com/trustbridge-platform/trustbridge.git
cd trustbridge

# 1. API (terminal 1)
cd backend
cp .env.example .env          # Windows PowerShell: Copy-Item .env.example .env
npm install
npm run dev                   # http://localhost:5000

# 2. Frontend (terminal 2, from the repository root)
cp .env.example .env.local    # Windows PowerShell: Copy-Item .env.example .env.local
npm install
npm run dev                   # http://localhost:5173
```

The SQLite database is created automatically on first run. Optional services (email, image upload, GitHub sign-in) are skipped when their keys are empty, so the whole app runs locally with only the defaults. Set `STELLAR_NETWORK=testnet` in `backend/.env`.

## Configuration

Every variable is documented in [`backend/.env.example`](https://github.com/trustbridge-platform/trustbridge/blob/main/backend/.env.example) and [`.env.example`](https://github.com/trustbridge-platform/trustbridge/blob/main/.env.example).

| Variable | Where | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | frontend | API base URL including `/api` (defaults to `http://localhost:5000/api`) |
| `PORT`, `NODE_ENV` | API | Server port and mode |
| `FRONTEND_URL` | API | Allowed CORS origin(s), comma-separated; also used for OAuth redirects and email links |
| `JWT_SECRET` | API | **Required in production**, at least 32 characters |
| `STELLAR_NETWORK` | API | `testnet` or `mainnet` (defaults to `mainnet`) |
| `API_BASE_URL` | API | Public API URL, used in email unsubscribe links |
| `EMAIL_API_KEY`, `EMAIL_FROM` | API | Resend notifications |
| `CLOUDINARY_*` | API | Campaign image upload |
| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` | API | GitHub sign-in |

| Command | Where | Does |
| --- | --- | --- |
| `npm run dev` | root, `backend/` | Start the dev server |
| `npm run build` | root | Production build of the SPA |
| `npm run lint` | root | ESLint |
| `npm test` | `backend/` | Run backend tests |

### Troubleshooting

| Problem | Likely cause and fix |
| --- | --- |
| API exits with `JWT_SECRET must be set...` | Production mode needs a secret of at least 32 characters. Generate one with `node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"` |
| Browser shows a network or CORS error | `FRONTEND_URL` on the API must exactly match the frontend's origin (no trailing slash). Locally, any `localhost` port is allowed in development |
| Frontend calls the wrong server | Set `VITE_API_URL` (ending in `/api`) and rebuild; the value is read at build time |
| Wallet is not detected | Install the extension, allow it on all sites, reload the page. Brave or privacy extensions can block injection |
| Port already in use | Change `PORT` in `backend/.env`, or stop the other process using 5000 or 5173 |
| Data disappears on the hosted demo | The free host has no persistent disk, so SQLite is reset on every deploy and restart |

## API overview

Base path `/api`. Routes marked (auth) need `Authorization: Bearer <token>`.

| Area | Endpoints |
| --- | --- |
| Auth | `POST /auth/register`, `POST /auth/login`, (auth) `GET /auth/me`, `PUT /auth/profile`, `PUT /auth/notifications`, `PUT /auth/change-password`, `GET /auth/unsubscribe` |
| GitHub | `GET /auth/github/url`, `POST /auth/github/callback` |
| Campaigns | `GET /campaigns`, `GET /campaigns/:id`, (auth) `POST /campaigns`, `POST /campaigns/:id/donate` |
| Comments | (auth) `POST /campaigns/:id/comments`, `DELETE /campaigns/:campaignId/comments/:commentId` |
| Transactions | (auth) `GET /transactions/me`, `POST /transactions/send`, `GET /transactions/export/csv`; public `GET /transactions/balance/:address`, `GET /transactions/balance-history/:address` |
| Admin | (admin) `GET /admin/stats`, `GET /admin/campaigns`, `POST /admin/campaigns/:id/deactivate` |
| Health | `GET /health`, `GET /health/ping` |

## Project structure

```
src/                   React app
  routes/              File-based routes (TanStack)
  components/          Layout, modals, shared UI
  services/api.ts      API client
  lib/                 Wallet detection and helpers
  i18n/                Translations
backend/
  server.js            Entry point
  src/app.js           Express app, CORS, rate limiting
  src/routes/          auth, oauth, campaigns, transactions, admin, health
  src/models/          SQLite data access
  src/services/        Stellar, email, image upload
  src/middleware/      JWT auth, admin guard, upload
  src/utils/           CSV, HTML escaping, tokens, serialisation
  test/                Node test runner suites
.github/               CI workflow, issue forms, pull request template
```

## Testing and quality

- **19 backend tests** cover Stellar transaction parsing (including rejecting multi-operation and non-native payments), unsubscribe tokens, HTML escaping, CSV formula protection and user serialisation. Run them with `cd backend && npm test`.
- **GitHub Actions** builds the frontend and runs the backend tests on every push and pull request.
- Broader API integration tests and frontend tests are open work: [#42](https://github.com/trustbridge-platform/trustbridge/issues/42).

## Deployment

TrustBridge runs as two services, for example on [Render](https://render.com):

1. **API** (Web Service, root directory `backend`): build `npm install`, start `node server.js`. Set `NODE_ENV=production`, `JWT_SECRET` (32+ characters; the API refuses to start without it), `FRONTEND_URL` (exact public frontend URL, no trailing slash), `API_BASE_URL` and `STELLAR_NETWORK`.
2. **Frontend** (Static Site): build `npm install && npm run build`, publish `.output/public`, and set `VITE_API_URL` to the API URL ending in `/api`. The value is read at build time, so rebuild after changing it. Add a rewrite of `/*` to `/index.html` for client-side routing.

> **Data persistence.** The API stores data in a SQLite file. On hosts without a persistent disk (including Render's free plan) that file is wiped on every deploy and restart, so accounts and campaigns do not survive. For anything beyond a demo, attach a persistent disk or move to a hosted database.

## Security

- Passwords are hashed with bcrypt and sessions use signed JWTs. The server refuses to start in production without a strong secret.
- Login and registration are rate-limited, and login never reveals whether an email exists.
- GitHub sign-in uses a random `state` and trusts only emails GitHub has verified.
- Donation amounts and destinations are verified from the signed Stellar transaction.
- CSV exports neutralise spreadsheet formulas, and user content is escaped in emails.

Found a vulnerability? Please use GitHub's private reporting described in [SECURITY.md](https://github.com/trustbridge-platform/trustbridge/blob/main/SECURITY.md) and do not open a public issue.

## Roadmap

- [ ] Connect the Donate flow to wallet signing and the verified API ([#37](https://github.com/trustbridge-platform/trustbridge/issues/37))
- [ ] Connect the Send page to wallet signing ([#38](https://github.com/trustbridge-platform/trustbridge/issues/38))
- [ ] xBull and Albedo wallets ([#34](https://github.com/trustbridge-platform/trustbridge/issues/34), [#35](https://github.com/trustbridge-platform/trustbridge/issues/35))
- [ ] Two-factor authentication ([#2](https://github.com/trustbridge-platform/trustbridge/issues/2)) and password reset ([#39](https://github.com/trustbridge-platform/trustbridge/issues/39))
- [ ] Real aggregates for the Dashboard and Analytics pages ([#40](https://github.com/trustbridge-platform/trustbridge/issues/40))
- [ ] Campaign wallet field and editing ([#41](https://github.com/trustbridge-platform/trustbridge/issues/41))
- [ ] Move from SQLite to a hosted database so data survives redeploys
- [ ] Campaign milestones and fund-release rules

## Contributing

Contributions are welcome, and newcomers are especially encouraged. Setup takes about five minutes.

**Workflow**

1. Read [CONTRIBUTING.md](https://github.com/trustbridge-platform/trustbridge/blob/main/CONTRIBUTING.md) and the [Code of Conduct](https://github.com/trustbridge-platform/trustbridge/blob/main/CODE_OF_CONDUCT.md).
2. Pick an issue. [Good first issues](https://github.com/trustbridge-platform/trustbridge/issues?q=is%3Aopen+label%3A%22good+first+issue%22) are small and well scoped, and every issue lists acceptance criteria.
3. Comment to be assigned. Issues entered into a funded event (Grainlify GrainHack, Drips Wave) are assigned through that event's platform instead, as described in the guide.
4. Branch from `main` as `fix/123-short-description` or `feat/123-short-description`, make a focused change, and run `npm run build` and `cd backend && npm test`.
5. Open a pull request that links the issue with `Closes #123`, with a screenshot or recording for any UI change.

**What we promise:** a first review within 48 hours, clear feedback, and merges by a maintainer once CI is green.

**Issue tiers.** Easy issues are small fixes or docs, Standard issues are features or involved fixes, and Advanced issues are larger integrations or refactors. The tier is stated on each issue.

## Community and support

- **Questions and ideas:** use [GitHub Discussions](https://github.com/trustbridge-platform/trustbridge/discussions)
- **Bugs and feature requests:** open an [issue](https://github.com/trustbridge-platform/trustbridge/issues/new/choose) using the template
- **Security problems:** report privately as described in [SECURITY.md](https://github.com/trustbridge-platform/trustbridge/blob/main/SECURITY.md)

## FAQ

**Are donations live?** Not yet. The Donate and Send screens run in a labelled preview mode while the wallet signing flow is built ([#37](https://github.com/trustbridge-platform/trustbridge/issues/37)). The API side already verifies signed transactions.

**Which Stellar network does it use?** Set by `STELLAR_NETWORK` (`testnet` or `mainnet`). Use testnet for development.

**Why does the hosted demo lose data?** It runs on a free tier without a persistent disk. See [Deployment](#deployment).

**How do I get an issue assigned?** Comment on it. For event issues, apply on the event platform and follow its rules.

**Can I work on something that is not listed?** Yes. Open a feature request first so we can agree on scope before you invest time.

## License

Released under the [MIT License](https://github.com/trustbridge-platform/trustbridge/blob/main/LICENSE).
