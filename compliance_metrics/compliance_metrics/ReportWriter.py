import os
from datetime import datetime 
from models import TemplateContext
from jinja2 import Environment, FileSystemLoader
from namespace import BUILD_DIR, TEMPLATE_DIR, REPORTS_DIR
from typing import NoReturn
import pdfkit
from jinja2_custom_filters import get_min_and_max_metrics_by_field

class ReportWriter:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        self.env.filters["get_min_and_max_metrics_by_field"] = get_min_and_max_metrics_by_field

    def _generate_pdf(self, html_path: str) -> str:
        pdf_path = os.path.join(REPORTS_DIR, f"report-{datetime.today().strftime('%Y-%m-%d')}.pdf")
        options = {
            'page-size': 'Letter',
            'margin-top': '0.35in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        with open(html_path) as f:
            pdfkit.from_file(f, pdf_path, options=options)
        return html_path

    def _generate_template_html(self, context: TemplateContext) -> str:
        template = self.env.get_template('_base_report.jinja2')
        output = template.render(context.dict())
        html_path = os.path.join(BUILD_DIR, "report.html")
        html_file = open(html_path, 'w')
        html_file.write(output)
        html_file.close()
        return html_path
    
    def write_report(self, context: TemplateContext) -> str:
        html = self._generate_template_html(context)
        pdf = self._generate_pdf(html)
        # TODO: Upload the generated report to Google Drive


def get_report_writer() -> ReportWriter:
    return ReportWriter()