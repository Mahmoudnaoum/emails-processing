"""
Fetch the last 10 emails with full body content.
Uses same OAuth as fetch_email_metadata.py; saves to last_10_emails_full.json.
"""

import base64
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent / "token.json"
MAX_MESSAGES = 10
OUTPUT_FILE = Path(__file__).parent / "last_10_emails_full.json"


def get_credentials():
    """OAuth2 flow: use credentials.json, save token for next runs."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE}. See README for setup."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def header_value(headers, name):
    name = name.lower()
    for h in headers or []:
        if h.get("name", "").lower() == name:
            return h.get("value", "")
    return ""


def get_body_from_payload(payload):
    """
    Extract plain text (or HTML) body from Gmail API message payload.
    Handles single-part (payload.body) and multipart (payload.parts) messages.
    """
    if not payload:
        return ""

    # Single-part: body is in payload.body
    body = payload.get("body", {})
    if body.get("data"):
        try:
            return base64.urlsafe_b64decode(body["data"]).decode("utf-8", errors="replace")
        except Exception:
            return "[Could not decode body]"

    # Multipart: look for text/plain first, then text/html
    parts = payload.get("parts", [])
    plain = None
    html = None
    for part in parts:
        mime = (part.get("mimeType") or "").lower()
        part_body = part.get("body", {})
        if not part_body.get("data"):
            continue
        try:
            decoded = base64.urlsafe_b64decode(part_body["data"]).decode("utf-8", errors="replace")
        except Exception:
            continue
        if mime == "text/plain":
            plain = decoded
        elif mime == "text/html":
            html = decoded
    return plain or html or ""


def fetch_last_n_full(service, n=MAX_MESSAGES):
    """List last n message IDs, then get full message (including body) for each."""
    result = (
        service.users()
        .messages()
        .list(userId="me", maxResults=n)
        .execute()
    )
    messages = result.get("messages", [])
    if not messages:
        return []

    full_messages = []
    for i, m in enumerate(messages):
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=m["id"], format="full")
            .execute()
        )
        full_messages.append(msg)
        print(f"  Fetched {i + 1}/{len(messages)}...")
    return full_messages


def to_serializable(msg):
    """Build a dict with metadata + full body for JSON output."""
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])
    return {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "labelIds": msg.get("labelIds", []),
        "snippet": msg.get("snippet", ""),
        "internalDate": msg.get("internalDate"),
        "From": header_value(headers, "From"),
        "To": header_value(headers, "To"),
        "Subject": header_value(headers, "Subject"),
        "Date": header_value(headers, "Date"),
        "body": get_body_from_payload(payload),
    }


def main():
    print("Fetching last 10 emails (full body)...\n")
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    full_messages = fetch_last_n_full(service, MAX_MESSAGES)
    print(f"Done. Got {len(full_messages)} messages.\n")

    out = [to_serializable(m) for m in full_messages]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {OUTPUT_FILE}")
    print("Each entry has: id, threadId, labelIds, snippet, From, To, Subject, Date, body (full text).")


if __name__ == "__main__":
    main()
