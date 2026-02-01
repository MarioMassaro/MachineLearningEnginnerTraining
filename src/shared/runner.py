from typing import Any, Dict

ALLOWED_JOBS = {"hello", "sum"}

def run_job(job: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if job not in ALLOWED_JOBS:
        raise ValueError(f"Job '{job}' not allowed. Allowed: {sorted(ALLOWED_JOBS)}")

    if job == "hello":
        name = str(payload.get("name", "world"))
        return {"message": f"hello {name}"}

    if job == "sum":
        a = float(payload.get("a", 0))
        b = float(payload.get("b", 0))
        return {"a": a, "b": b, "sum": a + b}

    # Nunca debería llegar aquí por whitelist
    raise ValueError("Invalid job")
