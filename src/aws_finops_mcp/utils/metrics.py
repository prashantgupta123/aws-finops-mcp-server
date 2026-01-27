"""CloudWatch metrics utilities."""

from datetime import datetime
from typing import Any


def calculate_metrics(datapoints: list[dict[str, Any]]) -> tuple[str, str, str]:
    """Calculate average, minimum, and maximum from CloudWatch datapoints.
    
    Args:
        datapoints: List of CloudWatch metric datapoints
        
    Returns:
        Tuple of (average, minimum, maximum) as formatted strings
    """
    if not datapoints:
        return "0.00", "0.00", "0.00"
    
    average = sum(point["Average"] for point in datapoints) / len(datapoints)
    minimum = min(point["Minimum"] for point in datapoints)
    maximum = max(point["Maximum"] for point in datapoints)
    
    return f"{average:.2f}", f"{minimum:.2f}", f"{maximum:.2f}"


def calculate_memory_metrics_gb(datapoints: list[dict[str, Any]]) -> tuple[str, str, str]:
    """Calculate memory metrics in GB from bytes.
    
    Args:
        datapoints: List of CloudWatch metric datapoints (in bytes)
        
    Returns:
        Tuple of (average, minimum, maximum) in GB as formatted strings
    """
    if not datapoints:
        return "0.00", "0.00", "0.00"
    
    average = sum(point["Average"] for point in datapoints) / len(datapoints)
    minimum = min(point["Minimum"] for point in datapoints)
    maximum = max(point["Maximum"] for point in datapoints)
    
    # Convert bytes to GB
    average_gb = average / (1024**3)
    minimum_gb = minimum / (1024**3)
    maximum_gb = maximum / (1024**3)
    
    return f"{average_gb:.2f}", f"{minimum_gb:.2f}", f"{maximum_gb:.2f}"


def get_metric_statistics(
    cloudwatch_client: Any,
    namespace: str,
    metric_name: str,
    dimensions: list[dict[str, str]],
    start_time: datetime,
    end_time: datetime,
    period: int = 86400,
) -> list[dict[str, Any]]:
    """Get CloudWatch metric statistics.
    
    Args:
        cloudwatch_client: Boto3 CloudWatch client
        namespace: CloudWatch namespace
        metric_name: Metric name
        dimensions: List of dimension dictionaries
        start_time: Start time for metrics
        end_time: End time for metrics
        period: Period in seconds (default: 86400 = 1 day)
        
    Returns:
        List of datapoints
    """
    response = cloudwatch_client.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=["Average", "Minimum", "Maximum"],
    )
    return response.get("Datapoints", [])
