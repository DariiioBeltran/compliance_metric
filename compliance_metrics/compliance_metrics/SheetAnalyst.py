import os
import csv
from utils import get_sheet
from namespace import DATA_DIR, TEMPLATE_DIR, BUILD_DIR
from typing import NoReturn
from models import MetricsSheetSchema, Operators, TemplateContext, MetricContext, Task
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ReportWriter import get_report_writer


class SheetAnalyst:
    def __init__(self, schema: MetricsSheetSchema):
        self.schema = schema
        assert self.schema.sheet_id, f"Sheet id is not in the yaml file"
        self.writer = get_report_writer()
        self.sheet = get_sheet(self.schema.sheet_id)
        self.metrics = {}
        for metric in self.schema.metrics:
            self.metrics[metric.name] = metric.dict()

        # Report data
        self.df = None
        self.averages = {}
        self.compliance_percentages = {}
        self.line_chart_paths = {}
        self.heat_map_paths = {}

    def _generate_csv_files(self) -> str:
        ws = self.sheet.worksheet(self.schema.sheet_name)
        assert ws, "Worksheet was not found"
        csv_file_name = f"{ws.title.replace(' ', '')}.csv"
        with open(os.path.join(DATA_DIR, csv_file_name), "w")  as f:
            writer = csv.writer(f)
            writer.writerows(ws.get_all_values())
        return csv_file_name

    def _load_data_with_pandas(self, csv_file_name: str) -> NoReturn:
        df = pd.read_csv(os.path.join(DATA_DIR, csv_file_name), delimiter=",")
        self.df = df

    def _compliance_rate_for_numeric_values(self, operator, target_value, value) -> bool:
        if operator == Operators.GT:
            return value > target_value
        elif operator == Operators.GTE:
            return value >= target_value
        elif operator == Operators.LT:
            return value < target_value
        elif operator == Operators.LTE:
            return value <= target_value
        else:
            raise NotImplementedError("This operator is currently not supported")
    
    def _basic_stats(self) -> NoReturn:
        for col in self.df.columns[1:]:
            # Averages
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.averages[col] = self.df[col].mean()

            # Compliance Percentage
            goal = self.metrics[col]["goal"]
            if not goal["operator"] is None:
                pct = self.df[col].apply(lambda x: self._compliance_rate_for_numeric_values(goal["operator"], goal["target_value"], x)).mean() * 100
                self.compliance_percentages[col] = pct
            else:
                pct = (self.df[col] == goal["target_value"]).mean() * 100
                self.compliance_percentages[col] = pct

    def _create_line_charts(self) -> NoReturn:
        assert self.df is not None, f"DataFrame has not been created yet"
        for metric in self.schema.metrics:
            if metric.data_type in {"int", "float"}:
                fig = px.line(self.df, x='Date', y=metric.name, title=f"{metric.name} Line Chart")
                linechart_path = os.path.join(BUILD_DIR, f"{metric.name}_line_chart.jpeg")
                fig.write_image(linechart_path)
                self.line_chart_paths[metric.name] = linechart_path

    def _create_heatmaps(self) -> NoReturn:
        assert self.df is not None, f"DataFrame has not been created yet"

        def _success_value(metric: Task, value: int | float | str) -> bool:
            target_value = metric.goal.target_value
            if metric.data_type in {"int", "float"}:
                if metric.goal.operator == Operators.GTE:
                    return bool(value >= target_value)
                if metric.goal.operator == Operators.GT:
                    return bool(value > target_value)
                elif metric.goal.operator == Operators.LTE:
                    return bool(value <= target_value)
                elif metric.goal.operator == Operators.LT:
                    return bool(value < target_value)
            return bool(value == target_value)

        for metric in self.schema.metrics:
            data = self.df[["Date", metric.name]].copy()
            data['Date'] = pd.to_datetime(data['Date'])
            data["Above Target"] = data[metric.name].apply(lambda x: 1 if _success_value(metric, x) else 0)

            data['Week'] = data['Date'].dt.isocalendar().week
            data['DayOfWeek'] = data['Date'].dt.weekday  # 0=Monday, 6=Sunday
            heatmap_data = data.pivot(index='Week', columns='DayOfWeek', values='Above Target').fillna(0)

            colorscale = [
                [0, "red"],
                [1, "green"],
            ]

            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.index,
                y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                colorscale=colorscale,
                colorbar=dict(title="Above Target")
            ))
            fig.update_layout(
                title='Heatmap of Values by Week Number and Day of the Week',
                xaxis_title='Week Number',
                yaxis_title='Month',
            )

            heatmap_path = os.path.join(BUILD_DIR, f"{metric.name}_heatmap.jpeg")
            fig.write_image(heatmap_path)
            self.heat_map_paths[metric.name] = heatmap_path

    def _get_template_context(self) -> TemplateContext:
        parsed_metrics = []
        for metric in self.schema.metrics:
            parsed_metrics.append(
                MetricContext(
                    metric_name=metric.name,
                    compliance_pct=self.compliance_percentages.get(metric.name),
                    average=self.averages.get(metric.name),
                    heatmap_file_name=self.heat_map_paths.get(metric.name),
                    linechart_file_name=self.line_chart_paths.get(metric.name),
                )
            )

        return TemplateContext(
            metrics=parsed_metrics, 
            css_path=os.path.join(TEMPLATE_DIR, "styling.css")
        )

    def analyze(self) -> NoReturn:
        csv_file_name = self._generate_csv_files()
        self._load_data_with_pandas(csv_file_name)
        self._basic_stats()
        self._create_line_charts()
        self._create_heatmaps()
        context = self._get_template_context()
        self.writer.write_report(context)


def get_sheet_analyst(schema: MetricsSheetSchema) -> SheetAnalyst:
    return SheetAnalyst(schema=schema)
