import os
import yaml
from models import MetricsSheetSchema
from gspread import Spreadsheet
from typing import NoReturn
from dotenv import load_dotenv
from namespace import DOT_ENV_PATH
from utils import create_sheet, calculate_col_letter_from_idx
from datetime import timedelta


class SheetCreator:
    def __init__(self, schema: MetricsSheetSchema):
        self.schema = schema
        self.sheet = None

    def create_sheet(self) -> Spreadsheet:
        load_dotenv(DOT_ENV_PATH)
        self.sheet = create_sheet(self.schema.sheet_name)
        self.sheet.share(
            email_address=os.environ.get("GMAIL"),
            perm_type="user",
            role="writer",
            notify=True,
            email_message=None,
            with_link=True
        )
        print(f"\n\nCreated new sheet for mesocylce here: {self.sheet.url}")
        print(f"You can expect an email granting you access once the command finished running.\n\n")

    def add_sheet_id_to_schema_file(self, sheet_id: str) -> NoReturn:
        data = self.schema.dict()
        data["sheet_id"] = sheet_id
        with open("compliance_metrics/metrics.yaml", "w") as file:
            yaml.dump(data, file)

    def setup_sheet(self) -> NoReturn:
        self.create_sheet()
        assert isinstance(self.sheet, Spreadsheet), f"The tracking sheet has not been created"
        rows = [(self.schema.start_tracking_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((self.schema.end_tracking_date - self.schema.start_tracking_date).days + 1)]
        cols = ["Date"] + [task.name for task in self.schema.metrics]

        # Add worksheet
        self.sheet.add_worksheet(title=self.schema.sheet_name, rows=len(rows)+1, cols=len(cols))
        worksheet = self.sheet.worksheet(self.schema.sheet_name)
        # Fill in the column names
        worksheet.update(
            values=[cols],
            range_name=f"A1:{calculate_col_letter_from_idx(len(cols))}2",
        )
        # Fill in the dates row
        worksheet.update(
            values=[[d] for d in rows],
            range_name=f"A2:A{len(rows)+1}"
        )

        # Delete the default "Sheet1" that gets created by default by Google
        sheet1 = self.sheet.worksheet("Sheet1")
        self.sheet.del_worksheet(sheet1)

        self.add_sheet_id_to_schema_file(self.sheet.id)


def get_sheet_creator(schema: MetricsSheetSchema) -> SheetCreator:
    return SheetCreator(schema=schema)
