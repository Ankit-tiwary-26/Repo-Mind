from app.agents.base import BaseAgent
from app.services import llm


class RefactoringAgent(BaseAgent):
    name = "refactoring"
    system_prompt = (
        "You are a senior software engineer specializing in code quality and refactoring. "
        "Analyze the provided code for: "
        "1) Code smells: long methods, god classes, feature envy, data clumps, duplicate code. "
        "2) SOLID principle violations with specific evidence. "
        "3) Suggest concrete refactoring steps with before/after code examples. "
        "4) Prioritize refactorings by impact: improve maintainability and readability first. "
        "Never suggest changes without showing the improved code. "
        "Only flag issues visible in the provided context."
    )

    def run(self, project_id: str, question: str) -> str:
        context = self.retrieve_context(project_id, question, n_results=10)
        prompt = f"CODE CONTEXT:\n{context}\n\nTASK:\n{question}"
        return llm.chat(self.system_prompt, prompt)
