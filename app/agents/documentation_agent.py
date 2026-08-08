from app.agents.base import BaseAgent
from app.services import llm


class DocumentationAgent(BaseAgent):
    name = "documentation"
    system_prompt = (
        "You are a senior technical writer specializing in developer documentation. "
        "Analyze the provided code and: "
        "1) Generate or improve docstrings for functions, classes, and modules. "
        "2) Suggest README sections, API documentation, and usage examples. "
        "3) Identify missing or outdated documentation. "
        "4) Write clear, concise documentation that follows the project's existing style. "
        "Use Google-style docstrings for Python, JSDoc for JavaScript/TypeScript. "
        "Only document code visible in the provided context."
    )

    def run(self, project_id: str, question: str) -> str:
        context = self.retrieve_context(project_id, question, n_results=10)
        prompt = f"CODE CONTEXT:\n{context}\n\nTASK:\n{question}"
        return llm.chat(self.system_prompt, prompt)
