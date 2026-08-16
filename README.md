# RepoMind AI — MVP

A working core of the "RepoMind AI" spec: clone/upload a repo → it gets chunked and
embedded → ask questions and get answers grounded in the actual code, routed to a
security, architecture, or general Q&A agent.

- Clone a public/private (token) GitHub repo, or upload a `.zip`
- Walks the tree, skips `node_modules`/`build`/`venv`/etc., detects language per file
- Chunks files (line-window w/ overlap) and embeds them into ChromaDB
- 3 agents: `qa`, `security`, `architecture` — an orchestrator keyword-routes to one
- REST API via FastAPI, OpenAPI docs auto-generated at `/docs`
