# Contributing to TrustBridge

Thank you for helping. TrustBridge is a humanitarian aid donation platform built on Stellar, so careful, well-tested contributions matter. This guide takes you from a fresh clone to a merged pull request.

By taking part you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md). For security problems, see [SECURITY.md](SECURITY.md) instead of opening a public issue.

## Contents

- [Set up your environment](#set-up-your-environment)
- [Find something to work on](#find-something-to-work-on)
- [Make your change](#make-your-change)
- [Before you open a pull request](#before-you-open-a-pull-request)
- [Review process](#review-process)
- [Code guidelines](#code-guidelines)
- [Reporting bugs and ideas](#reporting-bugs-and-ideas)

## Set up your environment

**Requirements:** Node.js 20 or newer, npm, Git. A Stellar wallet extension ([Freighter](https://www.freighter.app) or [Lobstr](https://lobstr.co)) helps for wallet features. Use **testnet** while developing.

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/<your-username>/trustbridge.git
cd trustbridge
git remote add upstream https://github.com/trustbridge-platform/trustbridge.git

# API (terminal 1)
cd backend
cp .env.example .env        # Windows PowerShell: Copy-Item .env.example .env
npm install
npm run dev                 # http://localhost:5000

# Frontend (terminal 2, repository root)
cp .env.example .env.local  # Windows PowerShell: Copy-Item .env.example .env.local
npm install
npm run dev                 # http://localhost:5173
```

The database is created automatically on first run. Optional services (email, image upload, GitHub sign-in) are skipped when their keys are empty, so you can work without any accounts. Set `STELLAR_NETWORK=testnet` in `backend/.env`.

**Never commit secrets.** `.env` files and `*.db` files are git-ignored. Do not paste keys, tokens or private keys into issues, pull requests or chats.

## Find something to work on

1. Look for issues labelled **good first issue** (small, well scoped) or **help wanted**. Each issue lists acceptance criteria.
2. Comment on the issue with a short note on how you plan to approach it, then wait for a maintainer to **assign** it to you. This avoids two people building the same thing.
3. If you go quiet for 7 days we may unassign you so someone else can help. Tell us if you need more time.

**Event issues (Grainlify GrainHack, Drips Wave).** Issues entered into a funded event are assigned through that event's platform, not by commenting here:

- **Grainlify GrainHack:** apply for the issue on Grainlify during the application window. A weighted draw picks the assignee, and maintainers do not choose or assign anyone on GitHub. Read the event's eligibility rules first.
- **Drips Wave:** issues carry the `Stellar Wave` label. Apply in the Drips Wave app, and wait until a maintainer accepts your application and assigns you.

Do not start work on an event issue before you are assigned. When you open your pull request, link the issue with `Closes #123` so it can be verified.

Have an idea that is not listed? Open a [feature request](../../issues/new/choose) first so we can agree on scope before you invest time.

## Make your change

```bash
git fetch upstream
git checkout -b fix/123-short-description upstream/main
```

- Name branches `fix/123-short-description`, `feat/123-short-description` or `docs/123-short-description`, where 123 is the issue number.
- Keep each pull request focused on **one** issue.
- Prefer small commits with clear messages (see below).
- Add or update tests when you change behaviour.
- Update the README or other docs when behaviour or setup changes.

### Commit messages

Use a short, imperative summary, optionally with a type prefix:

```
fix(auth): reject unverified GitHub emails
feat(wallet): add xBull connection
docs: clarify testnet setup
```

Explain *why* in the body when it is not obvious.

## Before you open a pull request

```bash
npm run build            # frontend: must succeed
npm run lint             # frontend: fix new warnings you introduced
cd backend && npm test   # API: all tests must pass
```

Then **open the app in a real browser and try your change**, including the failure paths. Include a screenshot or short screen recording in the pull request for any UI change. "It should work" is not enough.

Push to your fork and open a pull request against `main`. Fill in the template and link the issue with `Closes #123`.

## Review process

- A maintainer aims to give a first review within **48 hours**.
- Reviewers may request changes. That is normal and not a rejection.
- Small pull requests are reviewed and merged faster; consider splitting large ones.
- Maintainers merge pull requests. Please do not merge your own.
- Automated checks (CI) must be green before merging.

## Code guidelines

- **Frontend** (`src/`) is TypeScript with React and Tailwind CSS. File-based routes live in `src/routes/` (nested routes use dots, for example `auth.github.callback.tsx`). Keep touch targets at least 44px on mobile.
- **Backend** (`backend/src/`) is plain JavaScript (ES modules). Do not put TypeScript syntax in `.js` files.
- Validate input on the server. Never trust amounts, addresses or roles sent by the client.
- Use parameterised SQL (`?` placeholders); never build queries from user input.
- Escape user-supplied text before putting it in HTML or email.
- Do not add dependencies without explaining why in the pull request.
- Do not present sample or simulated data as real. Label it clearly.

## Reporting bugs and ideas

Use the issue templates. For bugs include steps to reproduce, expected and actual behaviour, browser and OS, and screenshots (remove personal data and tokens first).

Thank you for helping make aid giving more transparent.
