# 📖 User Guide

How to use PORTNET Incident Resolver. Read this in 5 minutes.

---

## What This Does

Analyzes incidents in 90 seconds instead of 2.5 hours.

**You paste incident → System searches everything → You get fix + escalation emails**

---

## Quick Start

1. Open `http://localhost:8501`
2. Click "Load Test Case 3" in sidebar
3. Click "Analyze Incident"
4. Wait 60 seconds
5. View results in tabs

Done. You just analyzed an incident.

---

## How to Use

### Step 1: Paste Incident

**What to paste:**
- Email from L1 support
- SMS alert
- Call notes
- Any incident description

**Example:**
```
Alert: SMS INC-154599
EDI message REF-IFT-0007 stuck in ERROR
No acknowledgment sent
```

**Tip:** Include ALL details. More info = better analysis.

---

### Step 2: Click Analyze

System will:
1. Extract entities (container numbers, error codes)
2. Search logs, cases, knowledge base
3. AI analyzes with evidence
4. Generate fix + escalation

Takes 30-90 seconds.

---

### Step 3: Review Results

**Analysis Results Tab:**
```
Shows:
├─ What kind of incident
├─ Root cause (with evidence from logs)
├─ Step-by-step fix (with actual SQL)
└─ Who to escalate to
```

**Escalation Summaries Tab:**
```
Ready-to-send emails:
├─ L3 Technical (with SQL, error codes)
└─ Management (business language, no jargon)
```

---

## Understanding Results

### Confidence Levels

**HIGH:** Clear evidence, safe to proceed
- Found in logs + matched historical case + KB article

**MEDIUM:** Some evidence, review carefully
- Found in logs + similar case OR KB article

**LOW:** Limited evidence, escalate to L3
- No clear match, AI making educated guess

**Rule:** If confidence isn't HIGH, get L3 help.

---

### When to Escalate

**Always escalate if:**
- Confidence is LOW
- You don't understand the fix
- Involves database changes you're unsure about
- Affects multiple customers
- Customer is urgent/angry

**You can handle if:**
- Confidence is HIGH
- Steps are clear
- You've done similar before
- One customer only

---

## Common Scenarios

### Duplicate Container

**Input:**
```
Customer seeing duplicate container CMAU0000020
```

**Output:**
```
Root Cause: Race condition
Fix: DELETE duplicate + ADD unique constraint
SQL: [actual queries]
Contact: Kevin Ng (Container L3)
```

---

### Vessel Error

**Input:**
```
Can't create vessel advice for MV Lion City 07
Error: VESSEL_ERR_4
```

**Output:**
```
Root Cause: Old advice not closed
Fix: Close old advice, retry creation
SQL: UPDATE vessel_advice SET...
Contact: Sarah Lee (Vessel L3)
```

---

### EDI Stuck

**Input:**
```
EDI message REF-IFT-0007 stuck in ERROR
```

**Output:**
```
Root Cause: Missing segment
Fix: Check segments, reprocess
SQL: SELECT * FROM edi_message_segments...
Contact: Tom Tan (EDI Support)
```

---

## Tips

### Get Better Results

✅ **DO:**
- Copy exact error messages
- Include all IDs (container, vessel, reference)
- Paste raw text (don't summarize)

❌ **DON'T:**
- Paraphrase or summarize
- Remove "unimportant" details
- Edit the incident text

### Download Results

- Click download button for complete plan
- Copy-paste escalation emails
- Save for documentation

---

## Troubleshooting

**System shows error?**
→ Check `.env` has API key, restart app

**Takes too long?**
→ First time: 60-90s normal. After: 30-60s. If always slow: check network

**Results don't make sense?**
→ Add more details, try again. Still unclear? Escalate to L3.

---

## Security

**DON'T:**
- Share API keys
- Copy sensitive data to personal devices
- Share escalation emails outside team

**DO:**
- Keep .env private
- Use secure network
- Log out when done

---

## That's It

System is simple. Three tabs:
1. Paste incident
2. View analysis
3. Get escalation emails

If in doubt, escalate. The system helps you, doesn't replace your judgment.

**Questions?** Ask your team lead.