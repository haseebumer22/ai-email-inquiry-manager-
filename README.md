# AI Email Inquiry Manager
> **Capture. Qualify. Organize. Respond.** — End-to-End System Blueprint & Vibe Code

The **AI Email Inquiry Manager** is an autonomous communications and lead capture pipeline designed to process incoming unstructured emails, extract structured buyer and intent data, synchronize entries to Google Sheets, and deliver instantaneous, personalized, context-aware replies.

---

## 1. Pipeline Architecture

```
[ Gmail Inbox Trigger ] ──▶ [ AI Intelligence Core ] ──▶ [ Google Sheets CRM ] ──▶ [ Gmail Dispatcher ]
 Polls unread customer        Gemini Flash extracts         Appends structured        Dispatches context-aware
 & lead emails                structured JSON entities      row (Cols A-F)            instant reply & archives
```

| Stage | Node / Step | Description |
|---|---|---|
| **1. Monitor Inquiries** | Gmail Inbox Trigger | Polls or receives push notifications for unread customer inquiries (`is:unread label:INBOX`). |
| **2. Extract Lead Details** | AI Intelligence Core | Gemini Flash parses intent, buyer parameters, urgencies, and contact entities with zero hallucination. |
| **3. Organize Leads** | Google Sheets CRM | Appends record into centralized lead tracking ledger with timestamp and categorization. |
| **4. Send Instant Replies** | Gmail Dispatcher | Sends drafted, personalized reply directly back to sender thread, cutting response time to 0. |

---

## 2. Extraction Data Schema & Destination Schema

### AI Extraction Schema (`LeadQualification`)
```json
{
  "sender_name": "Full name of prospect/customer parsed from greeting, signature, or metadata",
  "company_name": "Extracted organization or enterprise name (defaults to 'Individual')",
  "inquiry_category": "Enterprise Sales | Product Support | Partnership | General Inquiry",
  "urgency_level": "High | Medium | Low",
  "summary_intent": "Concise 1-sentence breakdown of prospect's exact requirements",
  "recommended_reply": "Professional, warm, context-aware email body addressing all specific inquiries raised"
}
```

### Google Sheets Destination Schema (`Lead_Inquiries_2026`)
| Column | Field Name | Description |
|---|---|---|
| **Column A** | Timestamp | ISO 8601 formatted execution timestamp |
| **Column B** | Sender Name | Full extracted lead name |
| **Column C** | Sender Email | Sender's email address |
| **Column D** | Company | Identified organization or firm |
| **Column E** | Category | Sales, Support, Partnership, or General |
| **Column F** | Summary / Intent | Concise synthesized requirements summary |

---

## 3. Quick Start: Interactive Prototype

Open [`index.html`](file:///d:/AD/AI%20email/index.html) in any modern web browser or start a lightweight local server:

```powershell
npx serve .
# or double click index.html
```

### Features of the Interactive Prototype:
- **Preset Scenarios:** Switch between *Enterprise Sales (500 seats)*, *Urgent SSO Support Outage*, *Reseller Partnership*, and *General Inquiry*.
- **Live Gemini API Support:** Click **"Live Gemini API"** in the top bar to provide an API key for live inference directly in the browser, or use the built-in high-fidelity heuristic engine.
- **Visual Pipeline Stages:** Real-time status indicators across all 4 pipeline stages.
- **Live Google Sheets CRM Sync:** Real-time simulated sheet table with CSV export.

---

## 4. Production Python Engine

### Prerequisites
1. Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment configuration:
   ```bash
   copy .env.example .env
   ```

### Google Cloud OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable **Gmail API** and **Google Sheets API**.
3. Create an **OAuth 2.0 Client ID** (Desktop Application) and download it as `credentials.json` into this project folder.
4. Set your Google Sheet ID in `.env` (`SPREADSHEET_ID`).

### Execution Modes

#### 1. Simulation / Dry Run (No Credentials Required)
Verify the pipeline extraction logic and formatted outputs:
```bash
python pipeline.py --simulate
```

#### 2. Dry Run with Live Google Services
Test Gmail polling and Gemini extraction without mutating data or sending emails:
```bash
python pipeline.py --dry-run
```

#### 3. Full Production Autonomous Execution
```bash
python pipeline.py
```

---

## 5. Node-by-Node Low-Code Spec (n8n / Orchestrators)

For n8n, Zapier, or Antigravity Agent configurations:

| Stage | Node Type | Parameters |
|---|---|---|
| **1. Monitor Inquiries** | Gmail Trigger | Event: `Message Received`<br>Filter: `is:unread label:INBOX`<br>Poll: `Every 1 min` |
| **2. Extract Lead Details** | AI Agent / Gemini Model | Model: `gemini-2.5-flash`<br>Mode: `Structured Output (JSON Schema)`<br>Input: `Email Snippet / Body` |
| **3. Organize Leads** | Google Sheets Node | Resource: `Sheet`<br>Operation: `Append Row`<br>Sheet: `Lead_Inquiries_2026`<br>Mapping: Columns A-F |
| **4. Send Instant Replies** | Gmail Action | Resource: `Message`<br>Operation: `Send`<br>Thread ID: `$json.threadId`<br>Body: `$json.recommended_reply` |

