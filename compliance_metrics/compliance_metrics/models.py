from pydantic import BaseModel
import datetime
from typing import Optional
import enum

class Operators(enum.Enum):
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"


class Goal(BaseModel):
    target_value: str | int
    operator: Optional[Operators] = None
    # TODO: We can create histograms if we want allow for tracking of enums


class Task(BaseModel):
    name: str
    data_type: str
    values: Optional[list[str]] = None
    goal: Goal


class MetricsSheetSchema(BaseModel):
    sheet_name: str
    start_tracking_date: datetime.date
    end_tracking_date: datetime.date
    metrics: list[Task]
    sheet_id: Optional[str] = None


class MetricContext(BaseModel):
    metric_name: str
    compliance_pct: Optional[float]
    average: Optional[float]
    heatmap_file_name: Optional[str]
    linechart_file_name: Optional[str]


class TemplateContext(BaseModel):
    metrics: list[MetricContext]
