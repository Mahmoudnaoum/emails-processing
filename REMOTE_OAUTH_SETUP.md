# Let someone sign in via your domain (redirect to your PC)

Use this when you want the client (e.g. Joseph) to open a **link** to sign in with their Gmail. The OAuth callback hits **your** server (on your PC), you save their token, then you run the export on your machine.

**Your setup:** host **https://api.mahnao.xyz/** → localhost port **3000**. The OAuth server runs on port 3000 by default.

---

## 1. Expose your PC (you already have api.mahnao.xyz → localhost:3000)

If **api.mahnao.xyz** already points to your machine on port 3000 (tunnel, reverse proxy, or port forward), you’re set. Just run the OAuth server on port 3000 (default).

If you use something else (e.g. ngrok, Cloudflare Tunnel), point it at **localhost:3000** so that `https://api.mahnao.xyz` reaches the app.

---

## 2. Add the redirect URI in Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → your project → **APIs & Services** → **Credentials**.
2. Open your **OAuth 2.0 Client ID** (use **Web application** if you use a redirect to your domain; add the URI below).
3. Under **Authorized redirect URIs**, add exactly:
   - **`https://api.mahnao.xyz/callback`**
4. Save.

---

## 3. Run the OAuth server on your PC

In the project folder (server listens on port 3000 by default):

```bash
set GMAIL_OAUTH_REDIRECT_URI=https://api.mahnao.xyz/callback
python oauth_server.py
```

On Linux/Mac: `export GMAIL_OAUTH_REDIRECT_URI=https://api.mahnao.xyz/callback` then `python oauth_server.py`.

Leave this running. Ensure **api.mahnao.xyz** points to this machine on port 3000.

---

## 4. Send the client the link

Send Joseph (or whoever) this URL:

**`https://api.mahnao.xyz/`**

They open it → get sent to Google → sign in with their Gmail → Google redirects to your `/callback` → your server saves the token to **`token_remote.json`** and shows “You’re all set”.

---

## 5. Run the export for that user

After they’ve signed in once, on your PC run:

```bash
set GMAIL_TOKEN_FILE=token_remote.json
python fetch_last_1000_full.py
```

The script will use their token and write **`last_1000_emails_full.json`** with their emails. You can rename or copy that file so you don’t overwrite it for the next user.

---

## Summary

| Step | What |
|------|------|
| 1 | api.mahnao.xyz → localhost:3000 (you already have this). |
| 2 | In Google Cloud, add **Authorized redirect URI** = **`https://api.mahnao.xyz/callback`**. |
| 3 | Run `oauth_server.py` with `GMAIL_OAUTH_REDIRECT_URI=https://api.mahnao.xyz/callback` (default port 3000). |
| 4 | Send the user **`https://api.mahnao.xyz/`**. They sign in; token saved as `token_remote.json` on your PC. |
| 5 | Run `fetch_last_1000_full.py` with `GMAIL_TOKEN_FILE=token_remote.json` to export their emails. |

**Security:** Only people you send the link to (and who are added as test users in Google Cloud) can sign in. The token is stored only on your PC. Use a strong `FLASK_SECRET_KEY` if you set one in production.
