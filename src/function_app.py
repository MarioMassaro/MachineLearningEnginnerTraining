import json
import azure.functions as func
from shared.runner import run_job

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"status": "ok"}),
        mimetype="application/json",
        status_code=200,
    )

@app.route(route="run", methods=["POST"])
def run(req: func.HttpRequest) -> func.HttpResponse:
    """
    POST /api/run
    Body:
      {
        "job": "hello",
        "payload": {...}
      }

    Nota: "job" se ejecuta por whitelist (seguro). No ejecutamos código arbitrario.
    """
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            mimetype="application/json",
            status_code=400,
        )

    job = body.get("job", "")
    payload = body.get("payload", {})

    try:
        result = run_job(job, payload)
        return func.HttpResponse(
            json.dumps({"ok": True, "job": job, "result": result}),
            mimetype="application/json",
            status_code=200,
        )
    except ValueError as e:
        return func.HttpResponse(
            json.dumps({"ok": False, "error": str(e)}),
            mimetype="application/json",
            status_code=400,
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"ok": False, "error": "Unhandled error", "detail": str(e)}),
            mimetype="application/json",
            status_code=500,
        )
