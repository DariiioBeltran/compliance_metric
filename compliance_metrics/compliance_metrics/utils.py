import yaml
import gspread
from gspread import Spreadsheet
from google.oauth2.service_account import Credentials
from models import MetricsSheetSchema


def get_metrics_schema() -> MetricsSheetSchema:
    with open("compliance_metrics/metrics.yaml") as schema:
        raw = yaml.safe_load(schema)
        return MetricsSheetSchema.parse_obj(raw)

def get_sheet(sheet_id: str) -> Spreadsheet:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)

def create_sheet(sheet_name: str) -> Spreadsheet:
    scopes = ["https://www.googleapis.com/auth/spreadsheets", 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    return client.create(sheet_name)

def calculate_col_letter_from_idx(idx: int) -> str:
    # This is only valid for two letters, beyond that this will NOT work
    offset = ord("A") - 1
    quot = offset + (idx // 26)
    rem = offset + (idx % 26)
    return chr(quot)+chr(rem) if idx > 26 else chr(offset + idx)