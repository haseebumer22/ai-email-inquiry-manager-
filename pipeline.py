"""
AI Email Inquiry Manager - Production Backend Engine
Autonomous Communications & Lead Capture Pipeline

Pipeline Architecture:
1. Gmail Inbox Trigger -> Polls unread customer/lead emails.
2. Sender Filter       -> Filters out no-reply, automated alerts, and system daemons.
3. AI Intelligence Core -> Gemini Flash extracts structured lead data.
4. Google Sheets CRM   -> Appends structured lead to target spreadsheet.
5. Gmail Dispatcher    -> Sends context-aware instant reply to the thread.
"""

import os
import sys
import time
import base64
import argparse
import datetime
from email.mime.text import MIMEText
from typing import Optional, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Google GenAI SDK & Google Client Libraries
from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load environment variables from .env
load_dotenv()

# Senders, domains, and automated daemons to ignore
IGNORE_KEYWORDS = [
    'no-reply',
    'noreply',
    'notifications',
    'notification',
    'mailer-daemon',
    'donotreply',
    'billing@',
    'alerts@',
    'google.com',
    'security@',
    'account-protection'
]


# ----------------- DATA SCHEMA -----------------
class LeadQualification(BaseModel):
    sender_name: str = Field(
        description="Full name of sender parsed from greeting, signature, or metadata"
    )
    company_name: str = Field(
        default="Individual",
        description="Company or organization name (defaults to 'Individual')"
    )
    inquiry_category: str = Field(
        description="Classification: Enterprise Sales, Product Support, Partnership, or General Inquiry"
    )
    urgency_level: str = Field(
        description="Calculated urgency: High, Medium, or Low"
    )
    summary_intent: str = Field(
        description="Concise 1-sentence breakdown of what the prospect or customer wants"
    )
    recommended_reply: str = Field(
        description="Professional, warm, context-aware auto-reply draft addressing specific inquiries"
    )


# ----------------- AUTHENTICATION -----------------
def authenticate_google_services():
    """
    Authenticates with Google APIs (Gmail and Google Sheets) using OAuth2.
    Requires 'credentials.json' from Google Cloud Console.
    Generates and refreshes 'token.json' automatically.
    """
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/spreadsheets'
    ]

    creds = None
    token_file = os.getenv('GOOGLE_TOKEN_FILE', 'token.json')
    creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"[!] Warning reading {token_file}: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[*] Refreshing Google OAuth credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_file):
                raise FileNotFoundError(
                    f"Google credentials file '{creds_file}' not found.\n"
                    f"Please download your OAuth client credentials from Google Cloud Console "
                    f"and save as '{creds_file}'."
                )
            print("[*] Initiating new Google OAuth authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            print(f"[+] Credentials saved to {token_file}")

    gmail = build('gmail', 'v1', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)
    return gmail, sheets


# ----------------- AI REASONING -----------------
def run_gemini_extraction(client: genai.Client, sender: str, subject: str, body: str) -> LeadQualification:
    """
    Uses Google GenAI SDK to evaluate incoming email text and return structured Pydantic model.
    """
    prompt = (
        f"You are the AI Email Inquiry Manager. Extract buyer details and draft a personalized reply.\n\n"
        f"From: {sender}\n"
        f"Subject: {subject}\n"
        f"Email Content:\n{body}\n"
    )
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LeadQualification,
                    temperature=0.2,
                ),
            )
            return response.parsed
        except Exception as e:
            if "503" in str(e) and attempt < 4:
                wait_time = (attempt + 1) * 3
                print(f"[!] Model high demand (503). Retrying in {wait_time}s (attempt {attempt + 1}/5)...")
                time.sleep(wait_time)
            else:
                raise e


# ----------------- SIMULATION MODE -----------------
def run_mock_pipeline():
    """
    Simulated local test run without requiring active Google API credentials.
    """
    print("=" * 60)
    print("   AI EMAIL INQUIRY MANAGER — SIMULATION MODE")
    print("=" * 60)

    sample_email = {
        "from": "Sarah Jenkins <sarah.jenkins@enterprise.com>",
        "subject": "Need enterprise pricing for 500 seats",
        "snippet": "We are evaluating tools for our 500-member team and need an enterprise quote with SLA support. Can we set up a 15-minute demo this Thursday? Best, Sarah Jenkins (Jenkins Logistics)"
    }

    print("\n[Step 1: Monitor Inquiries] Received message:")
    print(f"  From: {sample_email['from']}")
    print(f"  Subject: {sample_email['subject']}")
    print(f"  Snippet: {sample_email['snippet']}")

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("\n[Step 2: AI Intelligence Core] Querying Gemini via google-genai SDK...")
        ai_client = genai.Client(api_key=api_key)
        data = run_gemini_extraction(
            ai_client,
            sample_email['from'],
            sample_email['subject'],
            sample_email['snippet']
        )
    else:
        print("\n[Step 2: AI Intelligence Core] No GEMINI_API_KEY found, using structured mock output...")
        data = LeadQualification(
            sender_name="Sarah Jenkins",
            company_name="Jenkins Logistics",
            inquiry_category="Enterprise Sales",
            urgency_level="High",
            summary_intent="Evaluating tools for 500-member team, requests enterprise quote and 15-minute demo on Thursday.",
            recommended_reply=(
                "Hi Sarah,\n\n"
                "Thank you for contacting us regarding enterprise pricing for Jenkins Logistics. "
                "We would be delighted to demonstrate our platform for your 500-member team.\n\n"
                "Our senior solutions architect will contact you directly to confirm a walkthrough time this Thursday.\n\n"
                "Best regards,\nOperations Desk"
            )
        )

    print(f"  Extracted Name:     {data.sender_name}")
    print(f"  Extracted Company:  {data.company_name}")
    print(f"  Category:           {data.inquiry_category}")
    print(f"  Urgency:            {data.urgency_level}")
    print(f"  Summary Intent:     {data.summary_intent}")

    print("\n[Step 3: Organize Leads] Google Sheets Payload:")
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = [timestamp, data.sender_name, sample_email['from'], data.company_name, data.inquiry_category, data.summary_intent]
    print(f"  Sheet row: {row}")

    print("\n[Step 4: Send Instant Replies] Generated Dispatch:")
    print("-" * 60)
    print(f"To: {sample_email['from']}")
    print(f"Subject: Re: {sample_email['subject']}")
    print(f"\n{data.recommended_reply}")
    print("-" * 60)
    print("\n[+] Simulation completed successfully!")


# ----------------- PRODUCTION PIPELINE -----------------
def run_inquiry_pipeline(dry_run: bool = False):
    """
    Runs the full end-to-end production pipeline against Gmail and Google Sheets.
    """
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheet_tab = os.getenv('SPREADSHEET_RANGE', 'Lead_Inquiries_2026!A:F')
    inbox_query = os.getenv('GMAIL_SEARCH_QUERY', 'is:unread label:INBOX')

    if not dry_run and not spreadsheet_id:
        print("[!] ERROR: SPREADSHEET_ID environment variable is missing in .env")
        sys.exit(1)

    print("[*] Connecting to Google Services...")
    gmail, sheets = authenticate_google_services()

    print("[*] Initializing Gemini GenAI Client...")
    ai = genai.Client()

    # Step 1: Monitor Inquiries (Capture)
    print(f"[*] Querying Gmail inbox with filter: '{inbox_query}'...")
    res = gmail.users().messages().list(userId='me', q=inbox_query).execute()
    messages = res.get('messages', [])

    if not messages:
        print("[i] No new unread inquiries found in inbox.")
        return

    print(f"[+] Found {len(messages)} unread inquiry message(s). Processing...")

    for msg_meta in messages:
        msg_id = msg_meta['id']
        msg = gmail.users().messages().get(userId='me', id=msg_id, format='full').execute()

        headers = {h['name'].lower(): h['value'] for h in msg.get('payload', {}).get('headers', [])}
        sender = headers.get('from', '')
        subject = headers.get('subject', 'No Subject')
        snippet = msg.get('snippet', '')
        thread_id = msg.get('threadId', msg_id)

        print(f"\n---> Inspecting message ID: {msg_id}")
        print(f"     From: {sender}")
        print(f"     Subject: {subject}")

        # SENDER FILTER: Skip system, automated, and notification emails
        sender_lower = sender.lower()
        if any(keyword in sender_lower for keyword in IGNORE_KEYWORDS):
            print(f"     [-] Skipping automated/system email from: {sender}")
            if not dry_run:
                # Mark as read so it isn't picked up on every subsequent loop
                gmail.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            continue

        # Step 2: Extract Lead Details (Qualify)
        print("     [Step 2] Reasoning with Gemini Flash...")
        data = run_gemini_extraction(ai, sender, subject, snippet)
        print(f"     [+] Extracted: {data.sender_name} ({data.company_name}) | Category: {data.inquiry_category} | Urgency: {data.urgency_level}")

        if dry_run:
            print("     [DRY RUN] Skipping Google Sheets append and email dispatch.")
            continue

        # Step 3: Organize Leads (Sync Google Sheets)
        print("     [Step 3] Syncing lead to Google Sheets...")
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        row_values = [[
            now_iso,
            data.sender_name,
            sender,
            data.company_name,
            data.inquiry_category,
            data.summary_intent
        ]]

        sheets.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_tab,
            valueInputOption='RAW',
            body={'values': row_values}
        ).execute()
        print("     [+] Row appended to sheet.")

        # Step 4: Send Instant Replies (Respond)
        print("     [Step 4] Dispatching context-aware reply...")
        reply = MIMEText(data.recommended_reply)
        reply['to'] = sender
        reply['subject'] = f"Re: {subject}" if not subject.startswith("Re:") else subject
        raw = base64.urlsafe_b64encode(reply.as_bytes()).decode('utf-8')

        gmail.users().messages().send(
            userId='me',
            body={'raw': raw, 'threadId': thread_id}
        ).execute()

        # Mark message as read by removing UNREAD label
        gmail.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f"     [+] Reply sent and thread marked as read.")

    print("\n[+] All pending inquiries processed successfully.")


# ----------------- CLI ENTRYPOINT -----------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AI Email Inquiry Manager - Production Pipeline")
    parser.add_argument("--simulate", action="store_true", help="Run in mock/simulation mode without live Google APIs")
    parser.add_argument("--dry-run", action="store_true", help="Authenticate with Google and inspect messages without writing or sending replies")
    args = parser.parse_args()

    if args.simulate:
        run_mock_pipeline()
    else:
        try:
            run_inquiry_pipeline(dry_run=args.dry_run)
        except FileNotFoundError as fnf:
            print(f"\n[!] Error: {fnf}")
            print("[*] Tip: You can test the pipeline anytime using:\n    python pipeline.py --simulate")
        except Exception as e:
            print(f"\n[!] Pipeline Execution Error: {e}")
            