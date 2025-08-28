#integrate5.py
import streamlit as st
import sqlite3
from PyPDF2 import PdfReader
import docx2txt
import re
from datetime import datetime, date
import tempfile
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import numpy as np
import onnxruntime as ort
import pandas as pd
from auditnew import ensure_audit_table, log_audit
from reports import extract_text, ask_llm_for_parameters, approve_treatment
import os

def render_pa_page():
    ensure_audit_table()

    DB_PATH = os.path.join(os.path.dirname(__file__), "prior_auth.db")    ONNX_MODEL_PATH = "yolov7-p6-bonefracture.onnx"
    session = ort.InferenceSession(ONNX_MODEL_PATH)
    bone_to_icd10 = {
        'femur': 'S72.0',
        'tibia': 'S82.5',
        'radius': 'S52.5',
        'ulna': 'S52.6'
    }
    allowed_fractures = {
        "S72.0": ["S72.0", "S72.1", "S72.2", "S72.3"],
        "S82.5": ["S82.5", "S82.6", "S82.7", "S82.8"],
        "S52.5": ["S52.5", "S52.6", "S52.7", "S52.8"]
    }

    def to_int(x, default=0):
        try:
            if x is None:
                return default
            if isinstance(x, int):
                return x
            s = str(x).strip().replace(",", "")
            m = re.search(r"[-+]?\d+", s)
            return int(m.group(0)) if m else default
        except:
            return default

    def parse_date_any(s):
        if not s:
            return None
        s = str(s).strip()
        fmts = ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y", "%Y.%m.%d"]
        for f in fmts:
            try:
                return datetime.strptime(s[:10], f).date()
            except:
                continue
        return None

    def get_document_text(file):
        text = ""
        if file.type == "application/pdf":
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(file.getbuffer())
                tmp_path = tmp.name
            text += docx2txt.process(tmp_path) + "\n"
        else:
            try:
                text += file.read().decode("utf-8")
            except:
                text += ""
        return text

    def extract_patient_data(file):
        text = get_document_text(file)
        text = re.sub(r"\s+", " ", text)
        patient_ids = re.findall(r"Patient\s*ID[:\s\-]*([A-Za-z0-9\-_]+)", text, flags=re.I)
        npi_numbers = re.findall(r"NPI\s*(?:#|number)?\s*[:\s]*([0-9]{10})", text, flags=re.I)
        icd10_codes = re.findall(r"\b([A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?)\b", text)
        return {
            "Patient_ID": patient_ids[0].strip() if patient_ids else None,
            "Provider_NPI": npi_numbers[0].strip() if npi_numbers else None,
            "ICD-10_Codes": list(set(icd10_codes)) if icd10_codes else []
        }

    def get_treatment_from_icd(conn, icd_codes):
        cur = conn.cursor()
        for code in icd_codes:
            cur.execute("SELECT treatment_name FROM treatment_table WHERE icd10_code=?", (code,))
            row = cur.fetchone()
            if row and row[0]:
                return row[0].strip()
        return None

    def check_rules(conn, patient_id, treatment_name, provider_npi):
        cur = conn.cursor()
        reasons = []
        provider_npi_int = int(provider_npi)

        # Rule 0: Patient exists
        cur.execute("SELECT Age, Insurance_ID FROM patient_table WHERE Patient_ID=?", (patient_id,))
        p = cur.fetchone()
        if not p:
            reasons.append("Patient not found")
            patient_age = None
            insurance_id = None
        else:
            patient_age, insurance_id = to_int(p[0]), p[1]

        # Rule 1: Claim date within policy term (3 years)
        claim_date = None
        if insurance_id:
            cur.execute("SELECT Claim_Date FROM insurance_table WHERE Insurance_ID=?", (insurance_id,))
            ins = cur.fetchone()
            claim_date = parse_date_any(ins[0]) if ins else None
            if not claim_date or (date.today() - claim_date).days > 365 * 3:
                reasons.append("Claim date outside 3 years")

        # Rule 2: Provider active
        cur.execute("SELECT Start_date, End_date, Rndrng_Prvdr_Type FROM provider_table WHERE Rndrng_NPI=?",
                    (provider_npi_int,))
        prov = cur.fetchone()
        if prov:
            prov_start = parse_date_any(prov[0])
            prov_end = parse_date_any(prov[1])
            prov_type = prov[2].strip() if prov[2] else None
            if not (prov_start and prov_end and claim_date and prov_start <= claim_date <= prov_end):
                reasons.append("Provider not active on claim date")
        else:
            reasons.append("Provider not found")
            prov_type = None

        # Rule 3: Valid treatment
        cur.execute("SELECT COUNT(1) FROM treatment_table WHERE treatment_name=?", (treatment_name,))
        if cur.fetchone()[0] <= 0:
            reasons.append(f"Treatment '{treatment_name}' not authorized")

        # Rule 4: Provider services should not exceed beneficiaries
        cur.execute("SELECT Tot_Srvcs, Tot_Benes FROM provider_table WHERE Rndrng_NPI=?", (provider_npi_int,))
        row = cur.fetchone()
        if row:
            tot_srvcs, tot_benes = to_int(row[0]), to_int(row[1])
            if tot_srvcs > tot_benes:
                reasons.append("Provider services exceed beneficiaries.")
        else:
            reasons.append("Provider service/beneficiary data not found")

        # Rule 5: Provider type matches treatment dynamically
        treatment_provider_map = {
            "Dialysis": "Nephrologist",
            "Chemotherapy": "Oncologist",
            "Angioplasty": "Cardiologist",
            "Cataract": "Ophthalmologist",
            "Fracture": "Orthologist"
        }
        expected_type = treatment_provider_map.get(treatment_name)
        if expected_type and prov_type and prov_type.lower() != expected_type.lower():
            reasons.append(f"Provider type '{prov_type}' does not match treatment '{treatment_name}'")

        overall_decision = "APPROVED" if not reasons else "DENIED"
        summary = "; ".join(reasons) if reasons else "All rules passed"
        return overall_decision, summary

    def preprocess_image(image):
        image = image.convert('RGB')
        image = image.resize((640, 640))
        image_np = np.array(image) / 255.0
        image_np = image_np.transpose(2, 0, 1).astype(np.float32)
        image_np = np.expand_dims(image_np, axis=0)
        return image_np

    def detect_fracture(image_np):
        inputs = {session.get_inputs()[0].name: image_np}
        outputs = session.run(None, inputs)
        return outputs

    def postprocess(outputs, conf_threshold=0.5):
        predictions = outputs[0]
        class_ids = []
        for pred in predictions:
            conf_obj = pred[4]
            class_scores = pred[5:]
            class_id = int(np.argmax(class_scores))
            confidence = conf_obj * class_scores[class_id]
            if confidence > conf_threshold:
                class_ids.append(class_id)
        return class_ids

    def map_to_icd10(class_ids):
        bone_classes = ['femur', 'tibia', 'radius', 'ulna']
        detected_bones = [bone_classes[cid] for cid in class_ids]
        icd10_codes = [bone_to_icd10[bone] for bone in detected_bones]
        return detected_bones, icd10_codes

    def generate_pdf(patient_id, treatment, provider, rule_status, proof_status, final_decision, summary):
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.setFont("Helvetica", 12)
        c.drawString(50, 800, f"Patient ID: {patient_id}")
        c.drawString(50, 780, f"Treatment: {treatment}")
        c.drawString(50, 760, f"Provider NPI: {provider}")
        c.drawString(50, 740, f"Rule Status: {rule_status}")
        c.drawString(50, 720, f"Proof Status: {proof_status}")
        c.drawString(50, 700, f"Final Decision: {final_decision}")
        c.drawString(50, 680, f"Summary: {summary}")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    st.title("⚖ Prior Authorization Approval System")

    uploaded_file = st.file_uploader("Upload PA PDF/Docx", type=["pdf", "docx"])
    if uploaded_file:
        extracted = extract_patient_data(uploaded_file)
        st.subheader("✅ Extracted Info")
        st.write(extracted)

        conn = sqlite3.connect(DB_PATH)
        treatment_name = get_treatment_from_icd(conn, extracted["ICD-10_Codes"])
        rule_status, rule_summary = check_rules(conn, extracted["Patient_ID"], treatment_name, extracted["Provider_NPI"])
        st.write(f"Rule Engine Status: {rule_status}")
        st.write(f"Rule Summary: {rule_summary}")

        proof_choice = st.radio("Select Proof Type", ["Lab Report", "X-ray Fracture"])
        proof_status = "PENDING"

        if proof_choice == "Lab Report":
            lab_file = st.file_uploader("Upload Lab Report", type=["pdf", "docx", "txt", "md", "csv"])
            if lab_file and treatment_name:
                with st.spinner("🔎 Analyzing lab report..."):
                    text = extract_text(lab_file)

                    json_str = ask_llm_for_parameters(text, treatment_name)
                    st.subheader("🔎 Extracted Data from Report")
                    st.code(json_str, language="json")

                    try:
                        df = pd.read_json(json_str)
                    except Exception as e:
                        st.error(f"JSON parse error: {e}")
                        df = pd.DataFrame()

                    if not df.empty:
                        st.subheader("📊 Extracted Parameters")
                        st.dataframe(df)

                        doc_decision, details = approve_treatment(treatment_name, df)

                        st.subheader("📋 Lab Report Verification")
                        for k, v in details.items():
                            st.write(f"- {k} → {v}")

                        if "Approved" in doc_decision:
                            proof_status = "APPROVED"
                            st.success("Lab Report Verified ✅ (Approved by LLM check)")
                        else:
                            proof_status = "DENIED"
                            st.error("Lab Report Verification ❌ (All values in normal range → Deny)")
                    else:
                        proof_status = "DENIED"
                        st.error("No valid test data extracted from lab report ❌")

        elif proof_choice == "X-ray Fracture":
            xray_file = st.file_uploader("Upload X-ray Image", type=["jpg", "jpeg", "png"])
            if xray_file and extracted["ICD-10_Codes"]:
                icd10_claimed = extracted["ICD-10_Codes"][0]
                image = Image.open(xray_file)
                image_np = preprocess_image(image)
                outputs = detect_fracture(image_np)
                class_ids = postprocess(outputs)
                detected_bones, predicted_icd10_codes = map_to_icd10(class_ids)

                allowed_codes = allowed_fractures.get(icd10_claimed, [icd10_claimed])
                matched_codes = [code for code in predicted_icd10_codes if code in allowed_codes]

                if matched_codes:
                    proof_status = "APPROVED"
                    st.success(f"Fracture Verified ✅ Detected: {detected_bones[0]}, Code: {matched_codes[0]}")
                else:
                    proof_status = "DENIED"
                    st.error(f"Fracture Verification Failed ❌ (Expected: {icd10_claimed}, Got: {predicted_icd10_codes})")

        if st.button("Generate Final PDF"):
            final_decision = "APPROVED" if rule_status == "APPROVED" and proof_status == "APPROVED" else "DENIED"
            st.write(f"Final Decision: {final_decision}")

            icd10_code = extracted["ICD-10_Codes"][0] if extracted.get("ICD-10_Codes") else None

            log_audit(
                extracted["Patient_ID"],
                treatment_name,
                icd10_code,
                extracted["Provider_NPI"],
                rule_status,
                proof_status,
                final_decision
            )

            pdf_buffer = generate_pdf(
                extracted["Patient_ID"],
                treatment_name,
                extracted["Provider_NPI"],
                rule_status,
                proof_status,
                final_decision,
                rule_summary
            )
            st.download_button("Download PA Result PDF",
                               data=pdf_buffer,
                               file_name="PA_Result.pdf",
                               mime="application/pdf")

        conn.close()
