# How to export your emails (for Joseph)

You can export your Gmail into a file and send it to Mahmoud. No programming needed — just follow the steps below.

- **Quick test (10 emails):** use **`Export my emails.bat`** — fast, good to check everything works.
- **Full export (~1,000 emails):** use **`Export my emails (1000).bat`** — takes a few minutes, for LLM analysis and relationship mapping.

---

## Before you start

- **Mahmoud will add your Gmail address** to the app so you can sign in. Wait for him to confirm that’s done before Step 2.
- You need **Python** on your computer (free). If you’re not sure, do Step 1.

---

## Step 1: Install Python (one-time)

1. Go to: **https://www.python.org/downloads**
2. Click the yellow **“Download Python 3.x”** button.
3. Run the downloaded file (e.g. `python-3.12.x-amd64.exe`).
4. **Important:** On the first screen, **tick the box** that says **“Add python.exe to PATH”** at the bottom.
5. Click **“Install Now”** and wait until it says “Setup was successful”.
6. Close any open Command Prompt or PowerShell windows.

---

## Step 2: Get the folder from Mahmoud

Mahmoud will send you a **zip file** containing a folder with everything needed. Save it somewhere easy to find (e.g. your Desktop or Documents).

**Unzip the folder** (right‑click the zip → “Extract All…” → choose a location → Extract).

You should see files inside like:
- `Export my emails.bat` (10 emails, quick)
- `Export my emails (1000).bat` (~1,000 emails, for LLM work)
- `credentials.json`
- a few other files

---

## Step 3: Run the export

**For ~1,000 emails (what Mahmoud needs for the LLM):**

1. **Double‑click** **`Export my emails (1000).bat`**.
2. A black window will open. The first time it may say “Installing dependencies…” — that’s normal. Wait for it to finish.
3. When it says **“Please visit this URL to authorize”**, it will show a web address. **Copy that address** (or click it if it’s a link), open it in your browser, and **sign in with your Gmail** (the one you want to export from).
4. Click **“Allow”** when Google asks for permission to read your email.
5. Go back to the black window. It will fetch in batches (e.g. “Fetched 100/1000…”). **This takes a few minutes.** Wait until it says **“Done”** and **“Saved to: last_1000_emails_full.json”**.
6. Close the window when done.

**Quick test (10 emails only):** double‑click **`Export my emails.bat`** instead to get **`last_10_emails_full.json`** in a few seconds.

---

## Step 4: Send the file to Mahmoud

In the **same folder** you’ll see a new file:

**`last_1000_emails_full.json`** (or **`last_10_emails_full.json`** if you ran the quick test)

Send that file to Mahmoud (email, WhatsApp, etc.) — that’s your exported emails for the LLM and relationship mapping.

---

## If something goes wrong

- **“Python is not recognized”**  
  You need to do Step 1 again and make sure you ticked **“Add python.exe to PATH”**, then restart your computer and try Step 3 again.

- **“Access blocked” or “not completed the Google verification process”**  
  Your Gmail address isn’t added yet. Ask Mahmoud to add you as a test user and try again.

- **“Gmail API has not been used… or it is disabled”**  
  Tell Mahmoud — he needs to turn on the Gmail API in the project and then you can try again.

- **Anything else**  
  Take a screenshot of the error message and send it to Mahmoud.

---

**That’s it.** You only need to do Step 1 once. After that, whenever Mahmoud asks for a fresh export, just do Steps 3 and 4 again.
