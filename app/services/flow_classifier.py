from dataclasses import dataclass


CANDIDATE_KW = {
    "resume", "cv", "apply", "vacancy", "hiring", "open position",
    "remote work", "salary", "intern", "junior", "hr", "portfolio"
}

CLIENT_KW = {
    "estimate", "rate", "hourly", "case studies", "rfp", "book a call",
    "mvp", "enterprise", "budget", "timeline", "dedicated team", "outstaff", "augment"
}


@dataclass
class FlowDecision:
    flows: list[str]  # ["candidate"], ["client"], or ["candidate","client"]
    kw_hits: int


def _hits(text: str, vocab: set[str]) -> int:
    t = text.lower()
    return sum(1 for k in vocab if k in t)


def classify_flow(query: str) -> FlowDecision:
    c = _hits(query, CANDIDATE_KW)
    cl = _hits(query, CLIENT_KW)
    if c and cl:
        return FlowDecision(["candidate", "client"], c + cl)
    if c:
        return FlowDecision(["candidate"], c)
    if cl:
        return FlowDecision(["client"], cl)
    return FlowDecision(["candidate", "client"], 0)
