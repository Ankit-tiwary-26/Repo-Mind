import json
import logging
from app.agents.qa_agent import QAAgent
from app.agents.security_agent import SecurityAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.testing_agent import TestingAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.refactoring_agent import RefactoringAgent
from app.agents.bug_detection_agent import BugDetectionAgent
from app.agents.dependency_agent import DependencyAgent
from app.services import llm

logger = logging.getLogger(__name__)

_agents = {
    "qa": QAAgent(),
    "security": SecurityAgent(),
    "architecture": ArchitectureAgent(),
    "performance": PerformanceAgent(),
    "testing": TestingAgent(),
    "documentation": DocumentationAgent(),
    "refactoring": RefactoringAgent(),
    "bug_detection": BugDetectionAgent(),
    "dependency": DependencyAgent(),
}

ROUTER_SYSTEM_PROMPT = """You are an intent classifier for a code analysis platform. Given a user question about a codebase, classify it into exactly ONE of these agent categories:

- qa: General questions about how code works, what it does, explaining logic
- security: Security vulnerabilities, secrets, authentication, injection, XSS, CSRF
- architecture: Project structure, design patterns, layers, data flow, component relationships
- performance: Speed, optimization, bottlenecks, memory, caching, algorithmic complexity
- testing: Test cases, test coverage, QA, unit tests, integration tests
- documentation: Docstrings, README, API docs, comments, technical writing
- refactoring: Code smells, clean code, SOLID violations, restructuring, DRY
- bug_detection: Bugs, errors, edge cases, null references, race conditions, logic errors
- dependency: Dependencies, packages, versions, outdated libs, vulnerabilities in deps

Respond with ONLY the category name, nothing else."""

# Keyword fallback for when LLM routing fails
KEYWORD_MAP = {
    "security": ["security", "vulnerab", "secret", "sql injection", "xss", "csrf", "auth", "password", "token", "credential", "inject"],
    "architecture": ["architecture", "structure", "how does this project", "design", "layers", "diagram", "overview"],
    "performance": ["performance", "slow", "fast", "speed", "optimize", "bottleneck", "memory", "cache", "latency"],
    "testing": ["test", "coverage", "unittest", "pytest", "jest", "spec", "qa"],
    "documentation": ["document", "docstring", "readme", "comment", "api doc", "explain this function"],
    "refactoring": ["refactor", "clean", "smell", "duplicate", "dry", "solid", "maintainab"],
    "bug_detection": ["bug", "error", "crash", "exception", "null", "race condition", "fix", "broken"],
    "dependency": ["dependency", "dependencies", "package", "version", "outdated", "npm", "pip", "cargo"],
}


def route(question: str) -> str:
    """Route using LLM classification with keyword fallback."""
    try:
        result = llm.chat(ROUTER_SYSTEM_PROMPT, question, temperature=0.0)
        agent_name = result.strip().lower().replace('"', '').replace("'", "")
        if agent_name in _agents:
            logger.info(f"LLM routed to: {agent_name}")
            return agent_name
        logger.warning(f"LLM returned unknown agent '{agent_name}', falling back to keywords")
    except Exception as e:
        logger.warning(f"LLM routing failed ({e}), falling back to keywords")

    # Keyword fallback
    q = question.lower()
    for agent_name, keywords in KEYWORD_MAP.items():
        if any(k in q for k in keywords):
            return agent_name
    return "qa"


def handle(project_id: str, question: str, local_path: str | None = None) -> dict:
    """Route to an agent and return the complete answer."""
    agent_name = route(question)
    agent = _agents[agent_name]

    if agent_name == "architecture" and local_path:
        answer = agent.run(project_id, question, local_path=local_path)
    else:
        answer = agent.run(project_id, question)

    return {"agent": agent_name, "answer": answer}


def handle_stream(project_id: str, question: str, local_path: str | None = None):
    """Route to an agent and stream the answer. Yields (agent_name, chunk) tuples."""
    agent_name = route(question)
    agent = _agents[agent_name]

    # Build the prompt the same way the agent would
    if agent_name == "architecture" and local_path:
        context = agent.retrieve_context(project_id, question, n_results=10)
        summary_block = ""
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
    elif agent_name == "security":
        from app.agents.security_agent import SECRET_PATTERNS_HINT
        context = agent.retrieve_context(project_id, question, n_results=12)
        prompt = f"{SECRET_PATTERNS_HINT}\n\nCODE CONTEXT:\n{context}\n\nTASK:\n{question}"
    else:
        n = 12 if agent_name == "bug_detection" else 10
        context = agent.retrieve_context(project_id, question, n_results=n)
        prompt = f"CODE CONTEXT:\n{context}\n\nTASK:\n{question}"

    from app.services.llm import chat_stream
    for chunk in chat_stream(agent.system_prompt, prompt):
        yield (agent_name, chunk)
