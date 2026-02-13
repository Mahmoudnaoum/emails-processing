# Gmail API – Email Metadata Demo

Mini test to **pull the latest 100 emails and see what the metadata looks like**. No email body content is read — only who you spoke to, when, subject, and labels. Useful for exploring “who knows who” and connection graphs from real email data.

## What this does

1. **Authenticates** with your Gmail via OAuth (one-time browser flow).
2. **Lists** the latest 100 message IDs from your mailbox.
3. **Fetches metadata only** for each message (`format=metadata`): From, To, Date, Subject, labels, snippet — no body.
4. **Prints** the raw API response structure and a flattened summary, and saves `latest_100_metadata.json` for inspection.

## Setup

### 1. Google Cloud project and Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or pick an existing one).
3. **Enable the Gmail API**: APIs & Services → Library → search “Gmail API” → Enable.
4. **Create OAuth credentials**:
   - APIs & Services → Credentials → Create Credentials → **OAuth client ID**.
   - If asked, configure the OAuth consent screen (External is fine for a personal test).
   - Application type: **Desktop app**.
   - Download the JSON and save it as **`credentials.json`** in this folder (same folder as `fetch_email_metadata.py`).

### 2. Python environment

```bash
cd e:\Projects\gmail-apis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the demo

```bash
python fetch_email_metadata.py
```

- First run: a browser window opens so you can sign in and grant **read-only** access to Gmail.
- After that, the script fetches the latest 100 emails’ metadata and prints:
  - The structure of `messages.list()` and `messages.get(format='metadata')`.
  - A table of From, To, Date, Subject for all 100.
- Output is also written to **`latest_100_metadata.json`**.

## Files

| File | Purpose |
|------|--------|
| `fetch_email_metadata.py` | Script that does OAuth, list, and metadata fetch. |
| `credentials.json` | Your OAuth client secret (from Cloud Console). **Do not commit.** |
| `token.json` | Stored refresh token after first login. **Do not commit.** |
| `latest_100_metadata.json` | Flattened metadata for the 100 messages (optional to commit). |

## Next steps (after you’re happy with the metadata)

- Connect this to your Retool system and expose via the WhatsApp bot (e.g. via n8n).
- Use metadata to build “who you’ve spoken to, how often, about what” and recommend trusted connections (e.g. who knows a good agency or lawyer).

## Scopes

The script uses **`gmail.readonly`** so it can list and read message metadata (and could read body if we wanted). For a production “metadata only” product you could narrow to **`gmail.metadata`** so body is never accessible.
