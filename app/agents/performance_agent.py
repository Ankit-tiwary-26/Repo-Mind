from app.agents.base import BaseAgent
from app.services import llm


class PerformanceAgent(BaseAgent):
    name = "performance"
    system_prompt = (
        "You are a senior performance engineer reviewing production code. "
        "Identify performance bottlenecks, O(n²) or worse algorithms, unnecessary memory "
        "allocations, N+1 query patterns, missing caching opportunities, blocking I/O in "
        "async contexts, and inefficient data structures. For each finding, provide: "
        "severity (Critical/High/Medium/Low), file:line, explanation, and a concrete "
        "optimization with expected improvement. Only flag issues visible in the provided context."
    )

    def run(self, project_id: str, question: str) -> str:
        context = self.retrieve_context(project_id, question, n_results=10)
        prompt = f"CODE CONTEXT:\n{context}\n\nTASK:\n{question}"
        return llm.chat(self.system_prompt, prompt)
