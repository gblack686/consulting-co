#!/usr/bin/env python3
"""
Analytics Module - High-level analytics functions for Langfuse dashboard.
Built on top of langfuse_query_api.py for dashboard and reporting.

Phase 5A: Analytics primitives for cost, performance, and error tracking.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics


@dataclass
class CostMetrics:
    """Cost metrics for a time period."""
    total_cost: float
    average_cost_per_trace: float
    cost_per_tool_call: float
    cost_breakdown_by_project: Dict[str, float]
    cost_breakdown_by_agent: Dict[str, float]
    cost_trend: List[Tuple[str, float]]  # List of (date, cost)


@dataclass
class PerformanceMetrics:
    """Performance metrics for tools and agents."""
    tool_latencies: Dict[str, Dict[str, float]]  # tool_name → {min, max, mean, p95, p99}
    tool_error_rates: Dict[str, float]  # tool_name → error_rate_percent
    session_duration_stats: Dict[str, float]  # {min, max, mean, p95, p99}
    cache_hit_rate: float  # percentage
    slowest_tools: List[Tuple[str, float]]  # List of (tool_name, avg_latency)
    most_reliable_tools: List[Tuple[str, float]]  # List of (tool_name, success_rate)


@dataclass
class HierarchyMetrics:
    """Metrics about agent hierarchy and subagents."""
    total_root_agents: int
    total_subagent_calls: int
    average_children_per_agent: float
    max_hierarchy_depth: int
    depth_distribution: Dict[int, int]  # depth → count
    agents_with_subagents: int


@dataclass
class ErrorMetrics:
    """Error statistics and patterns."""
    total_error_traces: int
    error_rate_percent: float
    errors_by_tool: Dict[str, int]
    errors_by_agent: Dict[str, int]
    most_common_errors: List[Tuple[str, int]]  # (error_msg, count)
    recent_errors: List[Dict[str, Any]]  # Latest error traces


class Analytics:
    """High-level analytics functions for dashboards."""

    def __init__(self, query_api):
        """Initialize analytics with query API.

        Args:
            query_api: LangfuseQueryAPI instance
        """
        self.query_api = query_api

    # ==================== COST ANALYTICS ====================

    def get_cost_metrics(
        self,
        days: int = 30
    ) -> CostMetrics:
        """Calculate comprehensive cost metrics.

        Args:
            days: Number of days to analyze

        Returns:
            CostMetrics object with cost breakdown and trends
        """
        cost_by_project = self.query_api.get_cost_by_project(days=days)
        cost_by_agent = self.query_api.get_cost_by_agent(days=days)

        total_cost = sum(cost_by_project.values())
        total_projects = len(cost_by_project)

        # Get trace count for average calculation
        traces = self.query_api.get_traces(
            limit=1000,
            from_timestamp=(datetime.now() - timedelta(days=days)).isoformat()
        )

        total_tool_calls = sum(t.get("observations_count", 0) for t in traces)
        cost_per_tool = total_cost / total_tool_calls if total_tool_calls > 0 else 0

        # Calculate daily trend (simplified - 7 day windows)
        cost_trend = []
        for i in range(days // 7):
            window_start = datetime.now() - timedelta(days=days - (i * 7))
            window_end = datetime.now() - timedelta(days=days - ((i + 1) * 7))
            # Simplified: divide total by number of windows
            window_cost = total_cost / (days // 7)
            cost_trend.append((window_start.strftime("%Y-%m-%d"), window_cost))

        return CostMetrics(
            total_cost=round(total_cost, 4),
            average_cost_per_trace=round(total_cost / len(traces), 6) if traces else 0,
            cost_per_tool_call=round(cost_per_tool, 6),
            cost_breakdown_by_project={k: round(v, 4) for k, v in cost_by_project.items()},
            cost_breakdown_by_agent={k: round(v, 4) for k, v in cost_by_agent.items()},
            cost_trend=cost_trend
        )

    def get_cost_projection(
        self,
        days_historical: int = 30,
        days_forecast: int = 30
    ) -> Dict[str, Any]:
        """Project future costs based on historical data.

        Args:
            days_historical: Number of historical days to analyze
            days_forecast: Number of days to forecast

        Returns:
            Dict with projected costs and confidence intervals
        """
        metrics = self.get_cost_metrics(days=days_historical)
        daily_cost = metrics.total_cost / days_historical

        # Simple projection: assume linear trend
        projected_total = daily_cost * days_forecast

        return {
            "historical_daily_avg": round(daily_cost, 4),
            "projected_total": round(projected_total, 4),
            "projected_daily_avg": round(daily_cost, 4),
            "confidence_level": "low",  # Disclaimer: simple linear projection
            "forecast_days": days_forecast,
            "forecast_date": (datetime.now() + timedelta(days=days_forecast)).isoformat()
        }

    # ==================== PERFORMANCE ANALYTICS ====================

    def get_performance_metrics(
        self,
        days: int = 7
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics.

        Args:
            days: Number of days to analyze

        Returns:
            PerformanceMetrics object with latency and error data
        """
        # Get tool statistics
        tool_names = self._get_unique_tools(days=days)
        tool_latencies = {}
        tool_error_rates = {}

        for tool_name in tool_names:
            latency_stats = self.query_api.get_tool_latency_stats(
                tool_name=tool_name,
                days=days
            )
            if latency_stats.get("count", 0) > 0:
                tool_latencies[tool_name] = {
                    "min": latency_stats.get("min_ms", 0),
                    "max": latency_stats.get("max_ms", 0),
                    "mean": latency_stats.get("mean_ms", 0),
                    "p95": latency_stats.get("p95_ms", 0),
                    "p99": latency_stats.get("p99_ms", 0)
                }

            error_stats = self.query_api.get_tool_error_rate(
                tool_name=tool_name,
                days=days
            )
            if tool_name in error_stats:
                tool_error_rates[tool_name] = error_stats[tool_name]["error_rate_percent"]

        # Identify fastest and most reliable tools
        slowest_tools = sorted(
            [(k, v["mean"]) for k, v in tool_latencies.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        most_reliable = sorted(
            tool_error_rates.items(),
            key=lambda x: x[1]
        )[:5]
        most_reliable_tools = [(k, 100 - v) for k, v in most_reliable]

        return PerformanceMetrics(
            tool_latencies=tool_latencies,
            tool_error_rates=tool_error_rates,
            session_duration_stats={},  # Would need additional data collection
            cache_hit_rate=0.0,  # Would need cache tracking
            slowest_tools=slowest_tools,
            most_reliable_tools=most_reliable_tools
        )

    def get_tool_comparison(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Compare performance of all tools.

        Args:
            days: Number of days to analyze

        Returns:
            Tool comparison matrix
        """
        metrics = self.get_performance_metrics(days=days)

        comparison = []
        for tool_name, latencies in metrics.tool_latencies.items():
            error_rate = metrics.tool_error_rates.get(tool_name, 0)
            comparison.append({
                "tool": tool_name,
                "avg_latency_ms": round(latencies["mean"], 2),
                "p95_latency_ms": round(latencies["p95"], 2),
                "p99_latency_ms": round(latencies["p99"], 2),
                "error_rate_percent": round(error_rate, 2),
                "reliability_score": round(100 - error_rate, 2)
            })

        # Sort by reliability
        comparison.sort(key=lambda x: x["reliability_score"], reverse=True)

        return {
            "tools": comparison,
            "best_performer": comparison[0] if comparison else None,
            "most_problematic": comparison[-1] if comparison else None,
            "average_error_rate": round(
                statistics.mean([t["error_rate_percent"] for t in comparison]),
                2
            ) if comparison else 0
        }

    # ==================== HIERARCHY ANALYTICS ====================

    def get_hierarchy_metrics(
        self,
        days: int = 7
    ) -> HierarchyMetrics:
        """Calculate metrics about agent hierarchy.

        Args:
            days: Number of days to analyze

        Returns:
            HierarchyMetrics object with hierarchy information
        """
        # Get root agents
        traces = self.query_api.get_traces(
            limit=500,
            from_timestamp=(datetime.now() - timedelta(days=days)).isoformat(),
            filter_is_subagent=False
        )

        root_agent_count = len(traces)
        total_subagents = 0
        total_subagent_calls = 0
        agents_with_subagents = 0
        max_depth = 0
        depth_dist = {}

        for trace in traces:
            subagent_count = trace.get("metadata", {}).get("subagent_count", 0)
            hierarchy_depth = trace.get("metadata", {}).get("hierarchy_depth", 0)

            total_subagent_calls += subagent_count
            if subagent_count > 0:
                agents_with_subagents += 1
                total_subagents += subagent_count

            max_depth = max(max_depth, hierarchy_depth)
            depth_dist[hierarchy_depth] = depth_dist.get(hierarchy_depth, 0) + 1

        avg_children = total_subagents / agents_with_subagents if agents_with_subagents > 0 else 0

        return HierarchyMetrics(
            total_root_agents=root_agent_count,
            total_subagent_calls=total_subagent_calls,
            average_children_per_agent=round(avg_children, 2),
            max_hierarchy_depth=max_depth,
            depth_distribution=depth_dist,
            agents_with_subagents=agents_with_subagents
        )

    # ==================== ERROR ANALYTICS ====================

    def get_error_metrics(
        self,
        days: int = 7
    ) -> ErrorMetrics:
        """Calculate comprehensive error metrics.

        Args:
            days: Number of days to analyze

        Returns:
            ErrorMetrics object with error statistics
        """
        error_summary = self.query_api.get_error_summary(days=days)

        traces = self.query_api.get_traces(
            limit=500,
            from_timestamp=(datetime.now() - timedelta(days=days)).isoformat()
        )

        total_traces = len(traces)
        error_traces = error_summary.get("total_error_traces", 0)
        error_rate = (error_traces / total_traces * 100) if total_traces > 0 else 0

        errors_by_tool = error_summary.get("errors_by_tool", {})
        errors_by_agent = error_summary.get("errors_by_agent", {})

        most_common = sorted(
            errors_by_tool.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return ErrorMetrics(
            total_error_traces=error_traces,
            error_rate_percent=round(error_rate, 2),
            errors_by_tool=errors_by_tool,
            errors_by_agent=errors_by_agent,
            most_common_errors=most_common,
            recent_errors=[]  # Would need recent error retrieval
        )

    def get_error_trends(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Identify error trends over time.

        Args:
            days: Number of days to analyze

        Returns:
            Error trend analysis
        """
        metrics = self.get_error_metrics(days=days)

        return {
            "current_error_rate": metrics.error_rate_percent,
            "most_problematic_tool": metrics.most_common_errors[0][0] if metrics.most_common_errors else None,
            "tool_with_highest_errors": max(
                metrics.errors_by_tool.items(),
                key=lambda x: x[1]
            )[0] if metrics.errors_by_tool else None,
            "agent_with_highest_errors": max(
                metrics.errors_by_agent.items(),
                key=lambda x: x[1]
            )[0] if metrics.errors_by_agent else None,
            "total_error_events": sum(metrics.errors_by_tool.values()),
            "error_distribution_by_tool": metrics.errors_by_tool
        }

    # ==================== AGENT ANALYTICS ====================

    def get_agent_summary(
        self,
        agent_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get summary statistics for an agent.

        Args:
            agent_id: Specific agent to analyze (None = all agents)
            days: Number of days to analyze

        Returns:
            Agent summary with performance metrics
        """
        traces = self.query_api.get_traces(
            limit=500,
            from_timestamp=(datetime.now() - timedelta(days=days)).isoformat(),
            filter_agent_id=agent_id
        )

        if not traces:
            return {"error": "No traces found for specified agent"}

        costs = self.query_api.get_cost_by_agent(days=days)
        agent_cost = costs.get(agent_id, 0) if agent_id else sum(costs.values())

        return {
            "agent_id": agent_id or "all",
            "trace_count": len(traces),
            "total_cost": round(agent_cost, 4),
            "average_cost_per_trace": round(agent_cost / len(traces), 6) if traces else 0,
            "error_count": sum(1 for t in traces if t.get("metadata", {}).get("has_errors")),
            "error_rate": round(
                sum(1 for t in traces if t.get("metadata", {}).get("has_errors")) / len(traces) * 100,
                2
            ) if traces else 0,
            "subagent_count": sum(
                t.get("metadata", {}).get("subagent_count", 0) for t in traces
            ),
            "is_subagent": traces[0].get("metadata", {}).get("is_subagent", False) if traces else False
        }

    # ==================== HELPER METHODS ====================

    def _get_unique_tools(self, days: int = 7) -> List[str]:
        """Get list of unique tools used in time period.

        Args:
            days: Number of days to analyze

        Returns:
            List of tool names
        """
        traces = self.query_api.get_traces(
            limit=500,
            from_timestamp=(datetime.now() - timedelta(days=days)).isoformat()
        )

        tools = set()
        for trace in traces:
            tool_breakdown = trace.get("metadata", {}).get("tool_breakdown", {})
            tools.update(tool_breakdown.keys())

        return sorted(list(tools))

    def to_json(self, obj: Any) -> str:
        """Convert dataclass or dict to JSON string.

        Args:
            obj: Object to serialize

        Returns:
            JSON string
        """
        if hasattr(obj, "__dataclass_fields__"):
            obj = asdict(obj)

        return json.dumps(obj, indent=2, default=str)


def main():
    """CLI for testing analytics."""
    import argparse
    from langfuse_query_api import LangfuseQueryAPI

    parser = argparse.ArgumentParser(description="Analytics CLI")
    parser.add_argument("command", choices=[
        "cost", "performance", "hierarchy", "errors", "agent-summary",
        "tool-comparison", "error-trends", "cost-projection"
    ], help="Analytics command")
    parser.add_argument("--agent-id", help="Agent ID for analysis")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")

    args = parser.parse_args()

    try:
        query_api = LangfuseQueryAPI(cache_ttl=0)
        analytics = Analytics(query_api)
    except ValueError as e:
        print(f"❌ {e}")
        return

    print(f"✓ Analytics ready\n")

    if args.command == "cost":
        metrics = analytics.get_cost_metrics(days=args.days)
        print(analytics.to_json(metrics))

    elif args.command == "cost-projection":
        projection = analytics.get_cost_projection(
            days_historical=args.days,
            days_forecast=30
        )
        print(json.dumps(projection, indent=2))

    elif args.command == "performance":
        metrics = analytics.get_performance_metrics(days=args.days)
        print(analytics.to_json(metrics))

    elif args.command == "tool-comparison":
        comparison = analytics.get_tool_comparison(days=args.days)
        print(json.dumps(comparison, indent=2))

    elif args.command == "hierarchy":
        metrics = analytics.get_hierarchy_metrics(days=args.days)
        print(analytics.to_json(metrics))

    elif args.command == "errors":
        metrics = analytics.get_error_metrics(days=args.days)
        print(analytics.to_json(metrics))

    elif args.command == "error-trends":
        trends = analytics.get_error_trends(days=args.days)
        print(json.dumps(trends, indent=2))

    elif args.command == "agent-summary":
        summary = analytics.get_agent_summary(
            agent_id=args.agent_id,
            days=args.days
        )
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
