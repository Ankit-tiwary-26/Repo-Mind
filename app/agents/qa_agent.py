from app.agents.base import BaseAgent
from app.services import llm


class QAAgent(BaseAgent):
    name = "qa"
    system_prompt = (
        "You are a senior software engineer who has spent days reading this codebase. "
        "Answer using ONLY the provided code context. If the context doesn't contain the "
        "answer, say so explicitly instead of guessing. Cite file paths and line ranges "
        "when relevant."
    )

    def run(self, project_id: str, question: str) -> str:
        context = self.retrieve_context(project_id, question)
        prompt = f"CODE CONTEXT:\n{context}\n\nQUESTION:\n{question}"
        return llm.chat(self.system_prompt, prompt)
