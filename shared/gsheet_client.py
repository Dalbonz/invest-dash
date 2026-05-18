import json
from typing import List
import gspread
from google.oauth2.service_account import Credentials
from shared.logger import get_logger

logger = get_logger("gsheet_client")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def _get_creds_dict() -> dict:
    try:
        import streamlit as st
        sa = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
        return {
            "type": sa["type"],
            "project_id": sa["project_id"],
            "private_key_id": sa["private_key_id"],
            "private_key": sa["private_key"],
            "client_email": sa["client_email"],
            "client_id": sa["client_id"],
            "auth_uri": sa["auth_uri"],
            "token_uri": sa["token_uri"],
            "auth_provider_x509_cert_url": sa["auth_provider_x509_cert_url"],
            "client_x509_cert_url": sa["client_x509_cert_url"],
        }
    except Exception:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))

def _get_sheets_id() -> str:
    try:
        import streamlit as st
        return st.secrets["GOOGLE_SHEETS_ID"]
    except Exception:
        import os
        return os.getenv("GOOGLE_SHEETS_ID", "")

def _get_client() -> gspread.Client:
    creds = Credentials.from_service_account_info(_get_creds_dict(), scopes=SCOPES)
    return gspread.authorize(creds)

def read_sheet(sheet_name: str) -> List[dict]:
    try:
        sheet = _get_client().open_by_key(_get_sheets_id()).worksheet(sheet_name)
        return sheet.get_all_records()
    except Exception as e:
        logger.error(f"read_sheet failed: {e}")
        return []

def write_sheet(sheet_name: str, rows: List[dict]) -> bool:
    try:
        spreadsheet = _get_client().open_by_key(_get_sheets_id())
        try:
            sheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(sheet_name, rows=1000, cols=20)
        if not rows:
            return True
        headers = list(rows[0].keys())
        values = [headers] + [[row.get(h, "") for h in headers] for row in rows]
        sheet.clear()
        sheet.update(values, "A1")
        return True
    except Exception as e:
        logger.error(f"write_sheet failed: {e}")
        return False

def append_row(sheet_name: str, row: dict) -> bool:
    try:
        sheet = _get_client().open_by_key(_get_sheets_id()).worksheet(sheet_name)
        sheet.append_row(list(row.values()))
        return True
    except Exception as e:
        logger.error(f"append_row failed: {e}")
        return False