from models import MetricContext


def get_min_and_max_metrics_by_field(metrics: list[MetricContext], field_name: str) -> dict[str, MetricContext]:
    if len(metrics) == 0:
        return ""

    minimum = min(metrics, key=lambda m: m.get(field_name, 0))
    maximum = max(metrics, key=lambda m: m.get(field_name, 0))

    return {"minimum": minimum, "maximum": maximum}
