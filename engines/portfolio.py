import json, os
from google.oauth2.service_account import Credentials
import gspread

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = os.environ.get('GOOGLE_SHEETS_ID', '')
SHEET_TAB = '주식현황상세'

def get_client():
    creds_json = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '{}'))
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    return gspread.authorize(creds)

def run():
    try:
        sheet = get_client().open_by_key(SHEET_ID).worksheet(SHEET_TAB)
        all_values = sheet.get_all_values()
        headers = all_values[1]  # 2행 = 컬럼명
        holdings = []
        for row in all_values[2:]:
            if not any(row): continue
            r = {headers[i]: row[i] if i < len(row) else '' for i in range(len(headers))}
            if not r.get('종목명'): continue
            holdings.append(r)
        print(f'포트폴리오 {len(holdings)}개 로드')
        return {'holdings': holdings, 'count': len(holdings)}
    except Exception as e:
        print(f'포트폴리오 오류: {e}')
        return {'holdings': [], 'count': 0, 'error': str(e)}

if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))