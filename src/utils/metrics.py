"""Metrics and monitoring utilities for the PR Reviewer Agent."""
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """A single metric measurement."""
    timestamp: float
    value: float
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """Collect and manage metrics for the agent."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.timers: Dict[str, float] = {}

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for the metric
        """
        self.metrics[name].append(
            MetricPoint(
                timestamp=time.time(),
                value=value,
                tags=tags or {}
            )
        )

    def start_timer(self, name: str) -> None:
        """Start a timer for a named operation.

        Args:
            name: Timer name
        """
        self.timers[name] = time.time()

    def stop_timer(self, name: str) -> Optional[float]:
        """Stop a timer and record its duration.

        Args:
            name: Timer name

        Returns:
            Duration in seconds or None if timer wasn't started
        """
        start_time = self.timers.pop(name, None)
        if start_time is None:
            logger.warning(f"No timer found with name: {name}")
            return None

        duration = time.time() - start_time
        self.record_metric(f"{name}_duration", duration)
        return duration

    def get_metric_average(
        self,
        name: str,
        window_seconds: Optional[float] = None
    ) -> Optional[float]:
        """Get average value for a metric.

        Args:
            name: Metric name
            window_seconds: Optional time window to average over

        Returns:
            Average value or None if no data
        """
        points = self.metrics.get(name, [])
        if not points:
            return None

        if window_seconds:
            cutoff = time.time() - window_seconds
            points = [p for p in points if p.timestamp >= cutoff]

        if not points:
            return None

        return sum(p.value for p in points) / len(points)

    def get_metrics_summary(self) -> Dict[str, Dict]:
        """Get summary of all metrics.

        Returns:
            Dictionary with metric summaries
        """
        summary = {}
        for name, points in self.metrics.items():
            if not points:
                continue

            values = [p.value for p in points]
            summary[name] = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1]
            }

        return summary