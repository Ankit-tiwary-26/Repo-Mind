from app.agents.base import BaseAgent
from app.services import llm


class ArchitectureAgent(BaseAgent):
    name = "architecture"
    system_prompt = (
        "You are a staff software architect. Explain project architecture clearly and "
        "practically — layers, data flow, frameworks, and how components connect. "
        "Use the import graph and call graph to give accurate dependency information. "
        "Flag SOLID or clean-architecture violations only if you see concrete evidence "
        "in the given context, not in general."
    )

    def run(self, project_id: str, question: str, local_path: str | None = None) -> str:
        context = self.retrieve_context(project_id, question, n_results=10)
        summary_block = ""
        if local_path:
            try:
                from app.services.ingest import project_summary
                from app.services.code_graph import get_project_graph_summary
                summary = project_summary(local_path)
                graph = get_project_graph_summary(local_path)
                summary_block = (
                    f"PROJECT SUMMARY:\nFiles: {summary['total_files']}\n"
                    f"Languages: {summary['languages']}\nFrameworks: {summary['frameworks']}\n\n"
                    f"{graph}\n\n"
                )
            except Exception:
                pass
        prompt = f"{summary_block}CODE CONTEXT:\n{context}\n\nQUESTION:\n{question}"
        return llm.chat(self.system_prompt, prompt)
