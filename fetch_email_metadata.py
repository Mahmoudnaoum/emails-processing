"""
Gmail API demo: fetch the latest 100 emails and show metadata structure only.
No email body content is read — only who, when, subject, and labels.

Run once to authenticate (browser opens), then fetches and prints metadata.
"""

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope: read-only access to email metadata and headers (no body needed for this demo)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent / "token.json"
MAX_MESSAGES = 10
SAMPLE_FULL = 10  # number of full message objects to print as examples


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
                    f"Missing {CREDENTIALS_FILE}. "
                    "Download OAuth client credentials from Google Cloud Console "
                    "(APIs & Services > Credentials > Create OAuth 2.0 Client ID, Desktop app) "
                    "and save as credentials.json in this folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def header_value(headers, name):
    """Get a header value by name (case-insensitive)."""
    name = name.lower()
    for h in headers or []:
        if h.get("name", "").lower() == name:
            return h.get("value", "")
    return ""


def fetch_latest_metadata(service, max_results=MAX_MESSAGES):
    """List latest message IDs, then get metadata (no body) for each."""
    result = (
        service.users()
        .messages()
        .list(userId="me", maxResults=max_results)
        .execute()
    )
    messages = result.get("messages", [])
    if not messages:
        return [], result

    ids = [m["id"] for m in messages]
    # Fetch each message with format=metadata (headers + labels, no body)
    metadatas = []
    for i, msg_id in enumerate(ids):
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_id, format="metadata")
            .execute()
        )
        metadatas.append(msg)
        if (i + 1) % 20 == 0:
            print(f"  Fetched {i + 1}/{len(ids)}...")

    return metadatas, result


def flatten_message_for_display(msg):
    """Turn a Gmail API message (metadata) into a small dict for display."""
    headers = msg.get("payload", {}).get("headers", [])
    return {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "labelIds": msg.get("labelIds", []),
        "snippet": msg.get("snippet", ""),
        "internalDate": msg.get("internalDate"),
        "sizeEstimate": msg.get("sizeEstimate"),
        "From": header_value(headers, "From"),
        "To": header_value(headers, "To"),
        "Subject": header_value(headers, "Subject"),
        "Date": header_value(headers, "Date"),
        "Message-ID": header_value(headers, "Message-ID"),
    }


def main():
    print("Gmail API – latest emails metadata demo\n")
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    print(f"Fetching latest {MAX_MESSAGES} messages (metadata only)...")
    metadatas, list_result = fetch_latest_metadata(service, MAX_MESSAGES)
    print(f"Done. Got {len(metadatas)} messages.\n")

    # Show raw structure of list response
    print("=" * 60)
    print("1. Structure of messages.list() response (first 2 entries)")
    print("=" * 60)
    list_sample = {
        "resultSizeEstimate": list_result.get("resultSizeEstimate"),
        "messages": list_result.get("messages", [])[:2],
    }
    print(json.dumps(list_sample, indent=2))

    # Show raw structure of one full message (metadata format)
    print("\n" + "=" * 60)
    print(f"2. Structure of one message.get(format='metadata') (first {SAMPLE_FULL} messages)")
    print("=" * 60)
    for i, msg in enumerate(metadatas[:SAMPLE_FULL]):
        print(f"\n--- Message {i + 1} ---")
        print(json.dumps(msg, indent=2, default=str))

    # Summary table: who, when, subject
    print("\n" + "=" * 60)
    print("3. Flattened metadata for all (id, From, To, Date, Subject)")
    print("=" * 60)
    flattened = [flatten_message_for_display(m) for m in metadatas]
    for i, row in enumerate(flattened):
        print(f"\n[{i + 1}] id={row['id']}")
        print(f"    From: {row['From']}")
        print(f"    To:   {row['To']}")
        print(f"    Date: {row['Date']}")
        print(f"    Subject: {row['Subject'][:80]}{'...' if len(row['Subject'] or '') > 80 else ''}")

    # Save full flattened list to JSON for inspection
    out_file = Path(__file__).parent / "latest_100_metadata.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(flattened, f, indent=2, default=str)
    print(f"\nFull flattened metadata for all {len(flattened)} messages saved to: {out_file}")

    print("\nDone. You now have a clear view of the metadata format (who, when, subject, labels).")


if __name__ == "__main__":
    main()
