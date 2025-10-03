from typing import Any, Dict
from urllib.parse import parse_qs

from fastapi import Request
from twilio.request_validator import RequestValidator

from app.core.mixins import logger


def parse_form_body_if_needed(body: bytes, content_type: str) -> Dict[str, Any]:
    if content_type and content_type.startswith("application/x-www-form-urlencoded"):
        try:
            parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True)
            return {k: v[0] for k, v in parsed.items()}
        except Exception as e:
            logger(f"[WARN] Failed to parse form body: {e}")
            return {}
    return {}


def _external_url_from_proxy_headers(request: Request) -> str:
    """Rebuild public URL Twilio used when signing (respect proxy headers)."""
    fwd = request.headers.get("forwarded")
    proto = host = None
    if fwd:
        try:
            first = fwd.split(",")[0]
            for part in [p.strip() for p in first.split(";")]:
                if part.lower().startswith("proto="):
                    proto = part.split("=", 1)[1].strip('"')
                elif part.lower().startswith("host="):
                    host = part.split("=", 1)[1].strip('"')
        except Exception as e:
            logger(f"[WARN] Failed to parse Forwarded header: {e}")
    if not proto:
        proto = request.headers.get("x-forwarded-proto")
    if not host:
        host = request.headers.get("x-forwarded-host")
    if not host:
        host = request.headers.get("host") or request.url.netloc
    if not proto:
        proto = request.url.scheme
    url = f"{proto}://{host}{request.url.path}"
    if request.url.query:
        url += f"?{request.url.query}"
    return url


def validate_twilio_signature(request: Request, body: bytes, auth_token: str) -> bool:
    """Validate Twilio request signature header."""
    validator = RequestValidator(auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        logger("[ERROR] Missing X-Twilio-Signature header.")
        return False
    url = _external_url_from_proxy_headers(request)
    form = parse_form_body_if_needed(body, request.headers.get("content-type", ""))
    expected = validator.compute_signature(url, form)
    logger(f"[DEBUG] Provided sig={signature} Expected sig={expected} URL={url}")
    ok = validator.validate(url, form, signature)
    if not ok:
        logger("[ERROR] Twilio signature validation failed.")
    return ok
