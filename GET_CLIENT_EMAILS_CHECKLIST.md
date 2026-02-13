# Get your client’s emails (he only clicks one link)

Joseph does **one thing**: open the link and sign in with his Gmail. You do the rest on your side.

---

## Before you start

- Your host **https://api.mahnao.xyz/** is already pointing at your PC on port **3000**.
- You have **credentials.json** in this folder (from Google Cloud).

---

## Step 1: Google Cloud – allow Joseph and set redirect

1. Open [Google Cloud Console](https://console.cloud.google.com/) → your project.
2. **OAuth consent screen** (APIs & Services → OAuth consent screen):
   - Under **Test users**, click **+ ADD USERS** and add **Joseph’s Gmail address**. Save.
3. **Credentials** (APIs & Services → Credentials):
   - Open your **OAuth 2.0 Client ID**.
   - If it’s “Desktop”, create a **new** “Web application” client (or change this one to Web application).
   - Under **Authorized redirect URIs** add exactly:  
     **`https://api.mahnao.xyz/callback`**  
   - Save.

---

## Step 2: Run the OAuth server on your PC

In this folder, in a terminal:

**Windows (PowerShell or CMD):**
```bash
set GMAIL_OAUTH_REDIRECT_URI=https://api.mahnao.xyz/callback
python oauth_server.py
```

**Mac/Linux:**
```bash
export GMAIL_OAUTH_REDIRECT_URI=https://api.mahnao.xyz/callback
python oauth_server.py
```

Leave this running. The server listens on port **3000** (so api.mahnao.xyz reaches it).

---

## Step 3: Send Joseph this link (the only thing he does)

Send him:

**https://api.mahnao.xyz/**

He should:
1. Open the link.
2. Sign in with **his** Gmail (the one you want to export).
3. Click **Allow** when Google asks for permission.
4. See “You’re all set” and close the tab.

That’s it for him. No script, no zip, no Python.

---

## Step 4: On your PC – run the export (after he’s signed in)

In **another** terminal, in this folder:

**Windows:**
```bash
set GMAIL_TOKEN_FILE=token_remote.json
python fetch_last_1000_full.py
```

**Mac/Linux:**
```bash
export GMAIL_TOKEN_FILE=token_remote.json
python fetch_last_1000_full.py
```

Wait for it to finish. It will create **`last_1000_emails_full.json`** with his last ~1,000 emails (metadata + full body).

---

## Step 5: Keep or rename the file

- **`token_remote.json`** = Joseph’s sign-in (keep it to pull his emails again later).
- **`last_1000_emails_full.json`** = his emails. Rename or copy it (e.g. `joseph_1000_emails.json`) if you’ll run the export for someone else next so you don’t overwrite it.

---

## If something goes wrong

- **“Access blocked” / “not completed verification”**  
  Add Joseph’s Gmail as a test user (Step 1, OAuth consent screen).

- **“redirect_uri_mismatch”**  
  In Credentials, the redirect URI must be exactly **`https://api.mahnao.xyz/callback`** (no trailing slash, HTTPS).

- **Joseph can’t open the link**  
  Check the OAuth server is running (Step 2) and that api.mahnao.xyz really points to your machine on port 3000.

- **You run the export but get your own emails**  
  You used your normal token. Run the export with **`GMAIL_TOKEN_FILE=token_remote.json`** (Step 4).
