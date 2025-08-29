#reports.py
import streamlit as st
import sqlite3
import pandas as pd
import re
import pdfplumber
import docx2txt
import joblib
import google.generativeai as genai
import json
from datetime import datetime, date
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "prior_auth.db")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

procedure_rules = {
    "Cataract": ["Fasting Blood Sugar"],
    "Dialysis": ["eGFR"],
    "Chemotherapy": ["Creatinine"],
    "Angioplasty": ["PT", "INR"]
}

def extract_text(file):
    if file.type == "application/pdf":
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += t + "\n"
        return text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(file)
    elif file.type in ["text/plain", "text/markdown"]:
        return file.read().decode("utf-8")
    elif file.type == "text/csv":
        df = pd.read_csv(file); return df.to_string()
    else: return ""

def ask_llm_for_parameters(report_text, treatment):
    required_tests = procedure_rules.get(treatment, [])
    prompt = f"""
    Extract ONLY the following test results if they exist:
    {required_tests}

    Return valid JSON array:
    [{{"Test Name": "Creatinine", "Result": "1.2 mg/dL", "Normal Range": "0.6–1.3 mg/dL"}}]

    Report:
    {report_text}
    """
    resp = model.generate_content(prompt)
    json_str = resp.text.strip()
    json_str = re.search(r"\[.*\]", json_str, re.DOTALL)
    if json_str: return json_str.group(0)
    return "[]"

def check_within_range(result_str, range_str):
    try:
        result = float(re.findall(r"[\d.]+", result_str)[0])
        numbers = re.findall(r"[\d.]+", range_str)
        if "–" in range_str or "-" in range_str:
            low, high = map(float, numbers); return low <= result <= high
        elif ">" in range_str: return result > float(numbers[0])
        elif "<" in range_str: return result < float(numbers[0])
        elif len(numbers) == 1: return result == float(numbers[0])
        else: return False
    except: return False

def approve_treatment(treatment, df):
    required_tests = procedure_rules.get(treatment, [])
    results = {}
    any_out_of_range = False

    for rule_test in required_tests:
        row = df[df["Test Name"].str.contains(rule_test, case=False, na=False)]
        if not row.empty:
            result = row.iloc[0]["Result"]; normal_range = row.iloc[0]["Normal Range"]
            status = check_within_range(result, normal_range)
            if not status:
                any_out_of_range = True
            results[rule_test] = f"Pass ✅ (Result: {result}, Range: {normal_range})" if status else f"Fail ❌ (Result: {result}, Range: {normal_range})"
        else:
            results[rule_test] = "Not Found ⚠"

    approved = any_out_of_range
    return ("Approved ✅" if approved else "Denied ❌"), results
