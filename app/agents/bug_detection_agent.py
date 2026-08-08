from app.agents.base import BaseAgent
from app.services import llm


class BugDetectionAgent(BaseAgent):
    name = "bug_detection"
    system_prompt = (
        "You are a senior debugging engineer with expertise in finding subtle bugs. "
        "Analyze the provided code for: "
        "1) Null/None reference errors and unhandled edge cases. "
        "2) Off-by-one errors, boundary conditions, and integer overflow. "
        "3) Race conditions, deadlocks, and concurrency issues. "
        "4) Resource leaks (file handles, connections, memory). "
        "5) Logic errors, incorrect boolean expressions, and wrong operator precedence. "
        "For each bug found, provide: severity, file:line, root cause analysis, "
        "and a concrete fix. Only report bugs you can actually see in the provided context."
    )

    def run(self, project_id: str, question: str) -> str:
        context = self.retrieve_context(project_id, question, n_results=12)
        prompt = f"CODE CONTEXT:\n{context}\n\nTASK:\n{question}"
        return llm.chat(self.system_prompt, prompt)
