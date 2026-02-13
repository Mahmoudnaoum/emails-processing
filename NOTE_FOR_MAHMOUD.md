# Before sending the pack to Joseph

1. **Add his Gmail as a test user**  
   Google Cloud Console → your project → APIs & Services → **OAuth consent screen** → scroll to **Test users** → **+ ADD USERS** → enter Joseph’s Gmail → Save.

2. **Zip the folder** for him with everything **except**:
   - `token.json` (your token — don’t send)
   - `*.pyc`, `__pycache__`, `.venv` (not needed)
   - `last_10_emails_full.json` / `latest_100_metadata.json` (your data — don’t send)

   **Include:** `Export my emails.bat`, `CLIENT_INSTRUCTIONS.md`, `credentials.json`, `fetch_last_10_full.py`, `requirements.txt`, `.gitignore` (optional).

3. Send him the zip **and** the **CLIENT_INSTRUCTIONS** (you can copy the text or send the file). Tell him to unzip, then follow the instructions and double‑click **Export my emails.bat**.

4. When he sends back **`last_1000_emails_full.json`**, you have ~1,000 of his emails (full body) to run through the LLM for relationship summarisation and to test by-person vs by-thread.

**In the zip, include:** `Export my emails.bat`, **`Export my emails (1000).bat`**, `CLIENT_INSTRUCTIONS.md`, `credentials.json`, `fetch_last_10_full.py`, **`fetch_last_1000_full.py`**, `requirements.txt`.
