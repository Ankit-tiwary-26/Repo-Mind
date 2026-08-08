# RepoMind AI — MVP

A working core of the "RepoMind AI" spec: clone/upload a repo → it gets chunked and
embedded → ask questions and get answers grounded in the actual code, routed to a
security, architecture, or general Q&A agent.

This is **Phase 1 of a multi-phase build**, not the full enterprise spec — see the
roadmap at the bottom for what's deliberately deferred and why.

## What's actually working right now

- Clone a public/private (token) GitHub repo, or upload a `.zip`
- Walks the tree, skips `node_modules`/`build`/`venv`/etc., detects language per file
- Chunks files (line-window w/ overlap) and embeds them into ChromaDB
- 3 agents: `qa`, `security`, `architecture` — an orchestrator keyword-routes to one
- REST API via FastAPI, OpenAPI docs auto-generated at `/docs`

## Setup

1. **Get a free Groq API key**: https://console.groq.com (you already use this — same
   key works here as your email-triage agent).

2. Create `.env` in the project root:
   ```
   GROQ_API_KEY=your_key_here
   ```

3. Install deps (no Docker needed for local dev):
   ```bash
   cd repomind
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run it:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open http://localhost:8000/docs — this is your test UI for now (build the
   React/Next frontend in Phase 3).

## Try it end to end (curl)

```bash
# Ingest a public repo
curl -X POST http://localhost:8000/api/v1/repo/clone \
  -H "Content-Type: application/json" \
  -d '{"git_url": "https://github.com/psf/requests"}'
# → returns {"project_id": "...", "files_indexed": N, ...}

# Ask a question
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"project_id": "PASTE_ID_HERE", "question": "Explain how this project handles HTTP sessions."}'
```

Or run with Docker: `docker-compose up --build`.

## Why the MVP is scoped this way

Building all ~150 features in the original spec at once means nothing gets tested and
most of it silently doesn't work — same lesson as the CAPE zip bug in your lightning
project: get one path fully correct before scaling out. This MVP proves the hardest
part first: **grounded RAG over real code with agent routing.** Everything else in the
full spec is an extension of this same pattern (ingest → index → retrieve → agent →
answer), so once this works, adding agents is mostly copy-paste + a new system prompt.

---

## Roadmap: Phase 2–6 (in the order I'd actually build them)

### Phase 2 — Better ingestion & code understanding
- Replace line-window chunking with **tree-sitter** based chunking (chunk by
  function/class boundaries — big quality jump for code Q&A)
- Build import graph + call graph (static analysis per language, start with Python via `ast`)
- Persist project metadata in **Postgres** instead of the in-memory `PROJECTS` dict
- GitHub OAuth (instead of raw token) for private repo access

### Phase 3 — More agents + real orchestration
- Add: Performance Agent, Testing Agent, Documentation Agent, Refactoring Agent,
  Bug Detection Agent, Dependency Agent
- Replace keyword routing with an **LLM router** that can fan out to multiple agents
  in parallel (asyncio.gather) and have the Orchestrator merge/de-duplicate findings
- Streaming responses over WebSockets instead of blocking REST calls

### Phase 4 — Code review & security scanning (deterministic, not just LLM)
- Pair the Security Agent with actual static analyzers so findings aren't
  hallucination-prone: `bandit` (Python), `semgrep` (multi-language), `eslint` (JS/TS)
- Feed static analyzer output into the LLM as *evidence* rather than asking the LLM
  to spot vulnerabilities from raw code alone — much higher precision

### Phase 5 — Docs, tests, DevOps analysis
- README/Swagger/API doc generation (template + LLM fill-in)
- Test generation (pytest/Jest) — generate against actual function signatures, not
  guessed ones
- Dockerfile/docker-compose/GitHub Actions parsing + suggestions

### Phase 6 — Dashboard, frontend, scale-out
- Next.js frontend (chat UI, dependency/call graph visualization via Mermaid)
- Project Health Score dashboard (aggregate agent outputs into 0–100 scores)
- Redis caching, Celery background jobs for large-repo ingestion, rate limiting,
  RBAC, API versioning, Prometheus/Grafana monitoring

### What I deliberately left out of the MVP and why
- **GitHub OAuth**: needs a registered OAuth app + callback infra — not useful to
  build before the core RAG loop is proven
- **Kubernetes/Terraform analysis, voice chat, PDF export**: high effort, low
  learning value this early — bolt-on features once the core is solid
- **pgvector vs Chroma**: Chroma is faster to get running locally; swap to pgvector
  later only if you need it to live in the same Postgres instance as everything else

## Next step I'd actually take
Get Phase 1 running against your **lightning-prediction repo** as a real test case —
ask it "explain the CAPE feature pipeline" and see if it retrieves the right chunks.
That'll surface any chunking/retrieval quality issues before you add more agents on
top of a shaky foundation.
