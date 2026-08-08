from app.agents.base import BaseAgent
from app.services import llm


class DependencyAgent(BaseAgent):
    name = "dependency"
    system_prompt = (
        "You are a senior DevOps and dependency management engineer. "
        "Analyze the provided code and dependency files (package.json, requirements.txt, "
        "pyproject.toml, go.mod, Cargo.toml, pom.xml, etc.) for: "
        "1) Outdated dependencies that may have security vulnerabilities. "
        "2) Unused dependencies that bloat the project. "
        "3) Missing dependencies that are imported but not declared. "
        "4) Version conflicts and incompatible dependency combinations. "
        "5) License compatibility issues. "
        "Provide specific version recommendations and migration steps. "
        "Only analyze dependencies visible in the provided context."
    )

    def run(self, project_id: str, question: str) -> str:
        context = self.retrieve_context(project_id, question, n_results=10)
        prompt = f"CODE CONTEXT:\n{context}\n\nTASK:\n{question}"
        return llm.chat(self.system_prompt, prompt)
