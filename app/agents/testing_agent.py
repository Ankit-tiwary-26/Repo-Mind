from app.agents.base import BaseAgent
from app.services import llm


class TestingAgent(BaseAgent):
    name = "testing"
    system_prompt = (
        "You are a senior QA engineer and test architect. Analyze the provided code and: "
        "1) Identify untested or under-tested code paths, edge cases, and error scenarios. "
        "2) Suggest specific test cases with descriptive names and expected behavior. "
        "3) Generate working test code (pytest for Python, Jest for JS/TS) that tests "
        "actual function signatures from the code context — never guess signatures. "
        "4) Prioritize tests by risk: test critical paths and error handling first. "
        "Only reference code visible in the provided context."
    )

    def run(self, project_id: str, question: str) -> str:
        context = self.retrieve_context(project_id, question, n_results=10)
        prompt = f"CODE CONTEXT:\n{context}\n\nTASK:\n{question}"
        return llm.chat(self.system_prompt, prompt)
