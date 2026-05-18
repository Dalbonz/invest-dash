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
        return json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
    except Exception as e:
        logger.error(f"creds load failed: {e}")
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))

def _get_sheets_id() -> str:
    try:
        import streamlit as st
        return str(st.secrets["GOOGLE_SHEETS_ID"])
    except Exception:
        import os
        return os.getenv("GOOGLE_SHEETS_ID", "")

def _get_client() -> gspread.Client:
    creds = Credentials.from_service_account_info(_get_creds_dict(), scopes=SCOPES)
    return gspread.authorize(creds)

def read_sheet(sheet_name: str, header_row: int = 2) -> List[dict]:
    """
    header_row: 실제 컬럼명이 있는 행 번호 (1-based)
    주식현황상세는 1행=그룹헤더, 2행=컬럼명이라 header_row=2
    """
    try:
        client = _get_client()
        sheets_id = _get_sheets_id()
        logger.info(f"Opening sheet_id={sheets_id}, tab={sheet_name}")
        sheet = client.open_by_key(sheets_id).worksheet(sheet_name)

        all_values = sheet.get_all_values()
        if len(all_values) < header_row:
            logger.warning("Sheet has no data")
            return []

        headers = all_values[header_row - 1]  # 2행 = index 1
        rows = []
        for row in all_values[header_row:]:  # 3행부터 데이터
            if not any(row):  # 빈 행 스킵
                continue
            row_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
            rows.append(row_dict)

        logger.info(f"read_sheet OK: {len(rows)} rows")
        return rows
    except Exception as e:
        logger.error(f"read_sheet failed [{sheet_name}]: {type(e).__name__}: {e}")
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
        logger.error(f"write_sheet failed [{sheet_name}]: {type(e).__name__}: {e}")
        return False

def append_row(sheet_name: str, row: dict) -> bool:
    try:
        sheet = _get_client().open_by_key(_get_sheets_id()).worksheet(sheet_name)
        sheet.append_row(list(row.values()))
        return True
    except Exception as e:
        logger.error(f"append_row failed [{sheet_name}]: {type(e).__name__}: {e}")
        return False