from app.agents.base import BaseAgent
from app.services import llm

SECRET_PATTERNS_HINT = (
    "Look specifically for: hardcoded API keys, passwords, AWS/GCP credentials, "
    "JWT secrets, private keys, unsafe deserialization (pickle.loads, yaml.load without "
    "SafeLoader, eval/exec on input), unsafe subprocess calls (shell=True with user input), "
    "SQL built via string concatenation/f-strings (SQL injection), missing auth checks on "
    "routes, open redirects, and path traversal in file operations."
)


class SecurityAgent(BaseAgent):
    name = "security"
    system_prompt = (
        "You are a senior application security engineer reviewing real production code. "
        "Only flag issues you can actually see in the provided context — never invent "
        "line numbers or files not shown. For each finding give: severity (Critical/High/"
        "Medium/Low), file:line, a one-line explanation, and a concrete fix."
    )

    def run(self, project_id: str, question: str) -> str:
        context = self.retrieve_context(project_id, question, n_results=12)
        prompt = f"{SECRET_PATTERNS_HINT}\n\nCODE CONTEXT:\n{context}\n\nTASK:\n{question}"
        return llm.chat(self.system_prompt, prompt)
