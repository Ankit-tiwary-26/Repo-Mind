from abc import ABC, abstractmethod
from app.services import vectorstore, llm


class BaseAgent(ABC):
    name: str = "base"
    system_prompt: str = "You are a senior software engineer."

    def retrieve_context(self, project_id: str, question: str, n_results: int = 8) -> str:
        hits = vectorstore.query(project_id, question, n_results=n_results)
        blocks = []
        for h in hits:
            meta = h["metadata"]
            blocks.append(
                f"# File: {meta['path']} (lines {meta['start_line']}-{meta['end_line']})\n"
                f"{h['text']}"
            )
        return "\n\n---\n\n".join(blocks)

    @abstractmethod
    def run(self, project_id: str, question: str) -> str:
        ...
