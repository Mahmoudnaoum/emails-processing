"""
Fetch the last ~1,000 emails with full body content.
Uses pagination (Gmail API max 500 per list call). Saves to last_1000_emails_full.json.
Takes a few minutes to run.

To pull a *remote* user's emails (someone who signed in via your domain):
  set GMAIL_TOKEN_FILE=token_remote.json
  python fetch_last_1000_full.py
"""

import base64
import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
_token_file = os.environ.get("GMAIL_TOKEN_FILE", "token_remote.json")
TOKEN_FILE = Path(_token_file) if os.path.isabs(_token_file) else Path(__file__).parent / _token_file
MAX_MESSAGES = 1000
OUTPUT_FILE = Path(__file__).parent / "last_1000_emails_full.json"
LIST_PAGE_SIZE = 500  # Gmail API max for messages.list


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
    """Extract plain text (or HTML) body from Gmail API message payload."""
    if not payload:
        return ""

    body = payload.get("body", {})
    if body.get("data"):
        try:
            return base64.urlsafe_b64decode(body["data"]).decode("utf-8", errors="replace")
        except Exception:
            return "[Could not decode body]"

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


def list_message_ids(service, max_results=MAX_MESSAGES):
    """Paginate through messages.list to get up to max_results message IDs."""
    ids = []
    page_token = None
    while len(ids) < max_results:
        count = min(LIST_PAGE_SIZE, max_results - len(ids))
        request = service.users().messages().list(
            userId="me", maxResults=count, pageToken=page_token
        )
        result = request.execute()
        messages = result.get("messages", [])
        ids.extend([m["id"] for m in messages])
        page_token = result.get("nextPageToken")
        if not page_token or not messages:
            break
    return ids[:max_results]


def fetch_last_n_full(service, n=MAX_MESSAGES):
    """List last n message IDs (with pagination), then get full message for each."""
    print(f"  Listing up to {n} message IDs...")
    ids = list_message_ids(service, n)
    print(f"  Found {len(ids)} messages. Fetching full content (this may take a few minutes)...")
    full_messages = []
    for i, msg_id in enumerate(ids):
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_id, format="full")
            .execute()
        )
        full_messages.append(msg)
        if (i + 1) % 100 == 0 or (i + 1) == len(ids):
            print(f"  Fetched {i + 1}/{len(ids)}...")
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
    print(f"Fetching last {MAX_MESSAGES} emails (full body)...\n")
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    full_messages = fetch_last_n_full(service, MAX_MESSAGES)
    print(f"\nDone. Got {len(full_messages)} messages.\n")

    out = [to_serializable(m) for m in full_messages]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {OUTPUT_FILE}")
    print("Each entry has: id, threadId, labelIds, snippet, From, To, Subject, Date, body (full text).")


if __name__ == "__main__":
    main()
