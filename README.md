# TEAM-INNOVATHERS---PRIOR-AUTHORIZATION-AUTOMATION
Documentation on Prior Authorization Automation Project

## Overview

The Prior Authorization Automation system streamlines approval for prior authorization (PA) requests from hospitals and healthcare providers. It validates PA requests using rule-based verification, document analysis (lab reports or X-ray images), and AI-driven decision-making to ensure quick, consistent, and accurate authorization decisions.

This approach significantly reduces delays and improves efficiency in the authorization process.

---

## Tech Stack

- **Database:** SQLite
- **Frontend:** Streamlit
- **AI/ML Models:**
  - **Rule Engine:** Patient/Provider/Treatment verification
  - **LLM (Large Language Model):** Lab report interpretation & result range verification
  - **YOLOv7:** X-ray image fracture detection & ICD code classification

---

## Workflow

1. **Submission:** Hospital submits a PA request letter with provider’s consent.
2. **Verification:** System checks patient ID, provider ID, and treatment name (ICD code) in the database.
   - If valid, continues; else, denied.
3. **Document Analysis:**
   - **Lab Report:** LLM interprets results, verifies ranges, and cross-references ICD code.
   - **X-ray Image:** YOLOv7 detects fractures and determines ICD code.
4. **Decision:** Compares ICD code from document to PA letter.
   - If codes match, request approved; else, denied.
5. **Audit Trail:** Every decision logged with a timestamp, accessible from the homepage.

---

## Features

- Automated verification of PA requests
- LLM-powered lab report analysis
- YOLOv7-based X-ray fracture detection
- Rule engine for patient/provider/treatment validation
- Transparent audit trail with timestamps
- Interactive Streamlit frontend

---

## How to Run

```sh
# Clone the repository
git clone https://github.com/yourusername/prior-authorization-automation.git
cd prior-authorization-automation

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

---

## Use Cases

- Automates prior authorization requests for hospitals and providers.
- Enables insurers to validate patient, provider, and treatment codes.
- Analyzes lab reports (LLM) and X-rays (YOLOv7) for treatment justification.
- Maintains timestamped audit trails for compliance.
