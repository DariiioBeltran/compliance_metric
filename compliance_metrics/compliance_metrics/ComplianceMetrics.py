import os
import fire
from utils import create_sheet
from dotenv import load_dotenv
from namespace import DOT_ENV_PATH
from utils import get_metrics_schema, create_sheet
from gspread import Spreadsheet
from SheetCreator import get_sheet_creator
from SheetAnalyst import get_sheet_analyst
from typing import NoReturn


class ComplianceMetrics:
    def __init__(self):
        self.metrics_schema = get_metrics_schema()

    def setup(self) -> NoReturn:
        creator = get_sheet_creator(self.metrics_schema)
        creator.setup_sheet()

    def report(self) -> Spreadsheet:
        analyst = get_sheet_analyst(self.metrics_schema)
        analyst.analyze()

if __name__ == '__main__':
    fire.Fire(ComplianceMetrics)
