"""
OAuth server so someone can sign in with their Gmail from a link (e.g. your domain).
You run this on your PC and expose it via your domain or a tunnel (ngrok, Cloudflare Tunnel).
After they sign in, their token is saved to token_remote.json; you run the export script
with that token to pull their emails.

Set REDIRECT_URI to the full URL of /callback (e.g. https://export.yourdomain.com/callback).
Add that exact URL in Google Cloud Console → APIs & Services → Credentials → your OAuth client
→ Authorized redirect URIs.
"""

import os
from pathlib import Path

from flask import Flask, redirect, request
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_REMOTE_FILE = Path(__file__).parent / "token_remote.json"

# Must match exactly what you set in Google Cloud Console → Credentials → Redirect URIs
# e.g. https://export.yourdomain.com/callback  or  https://abc123.ngrok-free.app/callback
REDIRECT_URI = os.environ.get("GMAIL_OAUTH_REDIRECT_URI", "https://api.mahnao.xyz/callback").strip()
if not REDIRECT_URI:
    raise SystemExit(
        "Set GMAIL_OAUTH_REDIRECT_URI to your callback URL, e.g.\n"
        "  set GMAIL_OAUTH_REDIRECT_URI=https://export.yourdomain.com/callback\n"
        "Then add that URL in Google Cloud Console → Credentials → your OAuth client → Redirect URIs"
    )

# Base URL for this app (same origin as redirect, without /callback)
BASE_URL = REDIRECT_URI.rsplit("/", 1)[0]

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-in-production")


def _flow():
    return Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )


@app.route("/")
def index():
    """Send the user to Google to sign in."""
    flow = _flow()
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    """Google redirects here with ?code=...; exchange for token and save."""
    code = request.args.get("code")
    if not code:
        return (
            "<p>No authorization code received. Try again from the start.</p>"
            f'<p><a href="{BASE_URL}/">Start again</a></p>',
            400,
        )
    try:
        flow = _flow()
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open(TOKEN_REMOTE_FILE, "w") as f:
            f.write(creds.to_json())
    except Exception as e:
        return (
            f"<p>Could not complete sign-in: {e}</p>"
            f'<p><a href="{BASE_URL}/">Try again</a></p>',
            500,
        )
    return """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Done</title></head>
    <body style="font-family:sans-serif; max-width:480px; margin:2em auto; padding:1em;">
        <h1>You're all set</h1>
        <p>Your sign-in was successful. You can close this tab.</p>
        <p>The person who sent you this link can now export your emails (they will not see your password).</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    if not CREDENTIALS_FILE.exists():
        raise SystemExit(f"Missing {CREDENTIALS_FILE}")
    port = int(os.environ.get("PORT", "3000"))
    app.run(host="0.0.0.0", port=port)
