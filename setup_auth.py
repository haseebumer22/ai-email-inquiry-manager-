"""
Google Account Linking Helper (Gmail & Google Sheets OAuth2)
Runs a local OAuth server and opens your default browser to let you
sign in to your Google Account and approve Gmail & Sheets permissions.
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets'
]

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def link_google_account():
    print("=" * 60)
    print("   LINK YOUR GOOGLE ACCOUNT (GMAIL & GOOGLE SHEETS)")
    print("=" * 60)

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"\n[!] Missing '{CREDENTIALS_FILE}' in project root.")
        print("\nQuick 3-step setup to enable 1-click Google Sign-In:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Click '+ CREATE CREDENTIALS' -> 'OAuth client ID'")
        print("   - Application type: 'Desktop app'")
        print("   - Name: 'AI Email Inquiry Manager'")
        print("3. Click 'Download JSON' and save it as 'credentials.json' in this folder:")
        print(f"   {os.path.abspath(CREDENTIALS_FILE)}")
        print("\nOnce saved, run this script again to open the Google Sign-in screen.")
        sys.exit(1)

    print("\n[*] Starting OAuth authorization flow...")
    print("[*] A browser window will open shortly asking you to sign in.")
    print("    Select the Google account where you receive lead inquiries.\n")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

        print("\n" + "=" * 60)
        print("  SUCCESSFULLY LINKED YOUR GOOGLE ACCOUNT!")
        print(f"  Authorization token stored securely in: {TOKEN_FILE}")
        print("=" * 60)
    except Exception as e:
        print(f"\n[!] Authentication error: {e}")

if __name__ == '__main__':
    link_google_account()

