#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "langfuse>=3.0",
#     "python-dotenv",
#     "requests",
#     "pandas",
#     "numpy",
#     "cachetools",
# ]
# ///
"""
Langfuse Query API - High-level query interface for dashboard analytics.
Wraps Langfuse SDK with filtered queries, aggregations, and caching.

Phase 5A: Query Foundation for custom dashboards and analytics.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import cachetools
import hashlib

try:
    from langfuse import Langfuse
except ImportError:
    print("Error: Langfuse SDK not installed. Install with: pip install langfuse")
    exit(1)


# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)


class LangfuseQueryCache:
    """Cache layer for expensive queries with TTL and invalidation."""

    def __init__(self, ttl_seconds: int = 300):
        self.cache = cachetools.TTLCache(maxsize=100, ttl=ttl_seconds)
        self.enabled = True

    def get_key(self, query_type: str, filters: Dict[str, Any]) -> str:
        """Generate cache key from query type and filters."""
        key_str = f"{query_type}:{json.dumps(filters, sort_keys=True, default=str)}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, query_type: str, filters: Dict[str, Any]) -> Optional[Any]:
        """Get value from cache if enabled."""
        if not self.enabled:
            return None
        key = self.get_key(query_type, filters)
        return self.cache.get(key)

    def set(self, query_type: str, filters: Dict[str, Any], value: Any) -> None:
        """Set value in cache if enabled."""
        if not self.enabled:
            return
        key = self.get_key(query_type, filters)
        self.cache[key] = value

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def disable(self) -> None:
        """Disable caching for debugging."""
        self.enabled = False

    def enable(self) -> None:
        """Enable caching."""
        self.enabled = True


class LangfuseQueryAPI:
    """High-level query interface for Langfuse data."""

    def __init__(self, cache_ttl: int = 300):
        """Initialize query API with Langfuse client.

        Args:
            cache_ttl: Cache TTL in seconds (0 = disabled)
        """
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.base_url = os.getenv("LANGFUSE_BASE_URL", "http://localhost:3000")

        if not self.public_key or not self.secret_key:
            raise ValueError("LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY required in .env")

        self.client = Langfuse(
            public_key=self.public_key,
            secret_key=self.secret_key,
            host=self.base_url
        )

        self.cache = LangfuseQueryCache(ttl_seconds=cache_ttl)

    # ==================== TRACE QUERIES ====================

    def get_traces(
        self,
        limit: int = 100,
        from_timestamp: Optional[str] = None,
        to_timestamp: Optional[str] = None,
        filter_agent_id: Optional[str] = None,
        filter_source_app: Optional[str] = None,
        filter_has_errors: Optional[bool] = None,
        filter_is_subagent: Optional[bool] = None,
        filter_project: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get filtered traces from Langfuse.

        Args:
            limit: Maximum number of traces to return
            from_timestamp: ISO format start time
            to_timestamp: ISO format end time
            filter_agent_id: Filter by agent_id (e.g., "claude-code:session_a")
            filter_source_app: Filter by source_app
            filter_has_errors: Filter by error status
            filter_is_subagent: Filter by subagent flag
            filter_project: Filter by project name

        Returns:
            List of trace dictionaries
        """
        filters = {
            "agent_id": filter_agent_id,
            "source_app": filter_source_app,
            "has_errors": filter_has_errors,
            "is_subagent": filter_is_subagent,
            "project": filter_project,
        }

        # Check cache
        cached = self.cache.get("get_traces", filters)
        if cached is not None:
            return cached

        try:
            # Build filter conditions
            langfuse_filters = []

            if filter_agent_id:
                langfuse_filters.append(
                    {"key": "metadata.agent_id", "value": filter_agent_id}
                )
            if filter_source_app:
                langfuse_filters.append(
                    {"key": "metadata.source_app", "value": filter_source_app}
                )
            if filter_has_errors is not None:
                langfuse_filters.append(
                    {"key": "metadata.has_errors", "value": filter_has_errors}
                )
            if filter_is_subagent is not None:
                langfuse_filters.append(
                    {"key": "metadata.is_subagent", "value": filter_is_subagent}
                )
            if filter_project:
                langfuse_filters.append(
                    {"key": "metadata.project", "value": filter_project}
                )

            # Query traces
            response = self.client.get_traces(
                limit=limit,
                filter=langfuse_filters if langfuse_filters else None
            )

            traces = [
                {
                    "id": t.id,
                    "name": t.name,
                    "timestamp": t.timestamp,
                    "metadata": t.metadata or {},
                    "observations_count": len(t.observations) if hasattr(t, 'observations') else 0
                }
                for t in (response.data if hasattr(response, 'data') else response)
            ]

            # Cache result
            self.cache.set("get_traces", filters, traces)

            return traces

        except Exception as e:
            print(f"❌ Error querying traces: {e}")
            return []

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a single trace by ID.

        Args:
            trace_id: Trace ID to retrieve

        Returns:
            Trace dictionary or None if not found
        """
        try:
            trace = self.client.get_trace(trace_id)
            if not trace:
                return None

            return {
                "id": trace.id,
                "name": trace.name,
                "timestamp": trace.timestamp,
                "metadata": trace.metadata or {},
                "observations": [
                    {
                        "id": o.id,
                        "type": o.type,
                        "name": o.name,
                        "input": o.input,
                        "output": o.output,
                        "metadata": o.metadata or {},
                        "start_time": o.start_time,
                        "end_time": o.end_time,
                        "duration_ms": self._calc_duration(o.start_time, o.end_time),
                        "usage": o.usage if hasattr(o, 'usage') else None
                    }
                    for o in (trace.observations or [])
                ]
            }
        except Exception as e:
            print(f"❌ Error retrieving trace {trace_id}: {e}")
            return None

    # ==================== COST ANALYTICS ====================

    def get_cost_by_project(
        self,
        days: int = 30
    ) -> Dict[str, float]:
        """Get cost breakdown by project.

        Args:
            days: Number of days to analyze

        Returns:
            Dict mapping project name to cost in USD
        """
        filters = {"days": days}
        cached = self.cache.get("get_cost_by_project", filters)
        if cached is not None:
            return cached

        from_time = (datetime.now() - timedelta(days=days)).isoformat()

        traces = self.get_traces(
            limit=1000,
            from_timestamp=from_time
        )

        cost_by_project = {}

        for trace in traces:
            project = trace.get("metadata", {}).get("project", "Unknown")

            # Estimate cost from token usage
            if "usage" in trace.get("metadata", {}):
                usage = trace["metadata"]["usage"]
                cost = self._estimate_cost(usage)
                cost_by_project[project] = cost_by_project.get(project, 0) + cost

        self.cache.set("get_cost_by_project", filters, cost_by_project)
        return cost_by_project

    def get_cost_by_agent(
        self,
        days: int = 30
    ) -> Dict[str, float]:
        """Get cost breakdown by agent.

        Args:
            days: Number of days to analyze

        Returns:
            Dict mapping agent_id to cost in USD
        """
        filters = {"days": days}
        cached = self.cache.get("get_cost_by_agent", filters)
        if cached is not None:
            return cached

        from_time = (datetime.now() - timedelta(days=days)).isoformat()

        traces = self.get_traces(
            limit=1000,
            from_timestamp=from_time
        )

        cost_by_agent = {}

        for trace in traces:
            agent_id = trace.get("metadata", {}).get("agent_id", "Unknown")

            # Sum costs from all observations
            total_cost = 0
            if "observations_count" in trace:
                # Rough estimate: ~$0.01 per tool call
                total_cost = trace["observations_count"] * 0.01

            cost_by_agent[agent_id] = cost_by_agent.get(agent_id, 0) + total_cost

        self.cache.set("get_cost_by_agent", filters, cost_by_agent)
        return cost_by_agent

    # ==================== TOOL ANALYTICS ====================

    def get_tool_latency_stats(
        self,
        tool_name: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get latency statistics for tools.

        Args:
            tool_name: Filter by specific tool (None = all tools)
            days: Number of days to analyze

        Returns:
            Dict with latency stats (min, max, mean, p50, p95, p99)
        """
        filters = {"tool_name": tool_name, "days": days}
        cached = self.cache.get("get_tool_latency_stats", filters)
        if cached is not None:
            return cached

        from_time = (datetime.now() - timedelta(days=days)).isoformat()
        traces = self.get_traces(limit=500, from_timestamp=from_time)

        latencies = []

        for trace in traces:
            trace_detail = self.get_trace(trace["id"])
            if not trace_detail:
                continue

            for obs in trace_detail.get("observations", []):
                obs_tool = obs.get("metadata", {}).get("tool_name")

                if tool_name and obs_tool != tool_name:
                    continue

                if obs.get("duration_ms"):
                    latencies.append(obs["duration_ms"])

        if not latencies:
            return {"count": 0, "error": "No tool invocations found"}

        latencies.sort()

        stats = {
            "tool_name": tool_name or "All",
            "count": len(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "mean_ms": sum(latencies) / len(latencies),
            "p50_ms": latencies[len(latencies) // 2],
            "p95_ms": latencies[int(len(latencies) * 0.95)],
            "p99_ms": latencies[int(len(latencies) * 0.99)]
        }

        self.cache.set("get_tool_latency_stats", filters, stats)
        return stats

    def get_tool_error_rate(
        self,
        tool_name: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get error rate for tools.

        Args:
            tool_name: Filter by specific tool (None = all tools)
            days: Number of days to analyze

        Returns:
            Dict with error statistics
        """
        filters = {"tool_name": tool_name, "days": days}
        cached = self.cache.get("get_tool_error_rate", filters)
        if cached is not None:
            return cached

        from_time = (datetime.now() - timedelta(days=days)).isoformat()
        traces = self.get_traces(limit=500, from_timestamp=from_time)

        tool_stats = {}

        for trace in traces:
            trace_detail = self.get_trace(trace["id"])
            if not trace_detail:
                continue

            for obs in trace_detail.get("observations", []):
                obs_tool = obs.get("metadata", {}).get("tool_name")

                if tool_name and obs_tool != tool_name:
                    continue

                if not obs_tool:
                    continue

                if obs_tool not in tool_stats:
                    tool_stats[obs_tool] = {"total": 0, "errors": 0}

                tool_stats[obs_tool]["total"] += 1

                if obs.get("metadata", {}).get("status") == "error":
                    tool_stats[obs_tool]["errors"] += 1

        result = {}
        for tool, stats in tool_stats.items():
            error_rate = (stats["errors"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result[tool] = {
                "total_calls": stats["total"],
                "error_count": stats["errors"],
                "error_rate_percent": round(error_rate, 2)
            }

        self.cache.set("get_tool_error_rate", filters, result)
        return result

    # ==================== HIERARCHY ANALYTICS ====================

    def get_hierarchy_tree(
        self,
        root_session_id: str
    ) -> Dict[str, Any]:
        """Build hierarchical tree for a root session and its subagents.

        Args:
            root_session_id: Root session ID to start from

        Returns:
            Hierarchical tree structure
        """
        def build_tree(session_id: str, depth: int = 0) -> Dict[str, Any]:
            trace = self.get_trace(session_id)
            if not trace:
                return {"id": session_id, "not_found": True}

            node = {
                "id": session_id,
                "name": trace.get("name", "Unknown"),
                "depth": depth,
                "metadata": trace.get("metadata", {}),
                "children": []
            }

            # Find subagent calls
            for obs in trace.get("observations", []):
                if obs.get("metadata", {}).get("event_type") == "SubagentExecution":
                    child_id = obs.get("metadata", {}).get("child_trace_id")
                    if child_id:
                        child_node = build_tree(child_id, depth + 1)
                        node["children"].append(child_node)

            return node

        return build_tree(root_session_id)

    def get_hierarchy_depth_distribution(
        self,
        days: int = 7
    ) -> Dict[int, int]:
        """Get distribution of hierarchy depths.

        Args:
            days: Number of days to analyze

        Returns:
            Dict mapping depth → count of traces at that depth
        """
        filters = {"days": days}
        cached = self.cache.get("get_hierarchy_depth_distribution", filters)
        if cached is not None:
            return cached

        from_time = (datetime.now() - timedelta(days=days)).isoformat()
        traces = self.get_traces(
            limit=500,
            from_timestamp=from_time,
            filter_is_subagent=False  # Only root agents
        )

        distribution = {}
        for trace in traces:
            depth = trace.get("metadata", {}).get("hierarchy_depth", 0)
            distribution[depth] = distribution.get(depth, 0) + 1

        self.cache.set("get_hierarchy_depth_distribution", filters, distribution)
        return distribution

    # ==================== ERROR ANALYTICS ====================

    def get_error_summary(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get summary of errors in the system.

        Args:
            days: Number of days to analyze

        Returns:
            Error statistics and breakdown
        """
        filters = {"days": days}
        cached = self.cache.get("get_error_summary", filters)
        if cached is not None:
            return cached

        from_time = (datetime.now() - timedelta(days=days)).isoformat()
        traces = self.get_traces(
            limit=500,
            from_timestamp=from_time,
            filter_has_errors=True
        )

        error_by_tool = {}
        error_by_agent = {}

        for trace in traces:
            trace_detail = self.get_trace(trace["id"])
            if not trace_detail:
                continue

            agent_id = trace.get("metadata", {}).get("agent_id", "Unknown")

            for obs in trace_detail.get("observations", []):
                if obs.get("metadata", {}).get("status") == "error":
                    tool = obs.get("metadata", {}).get("tool_name", "unknown")
                    error_msg = obs.get("metadata", {}).get("error_message", "unknown")

                    error_by_tool[tool] = error_by_tool.get(tool, 0) + 1
                    error_by_agent[agent_id] = error_by_agent.get(agent_id, 0) + 1

        result = {
            "total_error_traces": len(traces),
            "errors_by_tool": error_by_tool,
            "errors_by_agent": error_by_agent,
            "most_problematic_tool": max(error_by_tool, key=error_by_tool.get) if error_by_tool else None,
            "most_problematic_agent": max(error_by_agent, key=error_by_agent.get) if error_by_agent else None
        }

        self.cache.set("get_error_summary", filters, result)
        return result

    # ==================== HELPER METHODS ====================

    @staticmethod
    def _calc_duration(start_time: Any, end_time: Any) -> Optional[int]:
        """Calculate duration in milliseconds between two timestamps."""
        if not start_time or not end_time:
            return None

        try:
            if isinstance(start_time, str):
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            else:
                start = start_time

            if isinstance(end_time, str):
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            else:
                end = end_time

            delta = (end - start).total_seconds() * 1000
            return int(max(delta, 0))
        except Exception:
            return None

    @staticmethod
    def _estimate_cost(usage: Dict[str, int]) -> float:
        """Estimate cost from token usage.

        Uses Claude 3.5 Sonnet pricing as baseline.
        """
        # Claude 3.5 Sonnet pricing (as of Nov 2025)
        COST_PER_1M_INPUT = 3.00  # $3 per 1M input tokens
        COST_PER_1M_OUTPUT = 15.00  # $15 per 1M output tokens

        input_tokens = usage.get("input", 0)
        output_tokens = usage.get("output", 0)

        input_cost = (input_tokens / 1_000_000) * COST_PER_1M_INPUT
        output_cost = (output_tokens / 1_000_000) * COST_PER_1M_OUTPUT

        return input_cost + output_cost


def main():
    """CLI for testing query API."""
    import argparse

    parser = argparse.ArgumentParser(description="Langfuse Query API CLI")
    parser.add_argument("command", choices=[
        "list-traces", "get-trace", "cost-by-project", "cost-by-agent",
        "tool-stats", "tool-errors", "hierarchy-tree", "error-summary",
        "test-connection", "validate-metadata"
    ], help="Query command")
    parser.add_argument("--trace-id", help="Trace ID for get-trace")
    parser.add_argument("--agent-id", help="Agent ID filter")
    parser.add_argument("--source-app", help="Source app filter")
    parser.add_argument("--tool-name", help="Tool name filter")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    parser.add_argument("--limit", type=int, default=10, help="Limit results")

    args = parser.parse_args()

    try:
        query_api = LangfuseQueryAPI(cache_ttl=0)  # Disable cache for CLI
    except ValueError as e:
        print(f"❌ {e}")
        return

    print(f"✓ Connected to Langfuse: {query_api.base_url}")
    print()

    if args.command == "test-connection":
        traces = query_api.get_traces(limit=1)
        if traces:
            print(f"✓ Query successful, found {len(traces)} traces")
        else:
            print("✓ Connection OK, no traces found")

    elif args.command == "list-traces":
        traces = query_api.get_traces(
            limit=args.limit,
            filter_agent_id=args.agent_id,
            filter_source_app=args.source_app
        )
        print(f"Found {len(traces)} traces:")
        for trace in traces:
            print(f"  {trace['id'][:12]}... {trace.get('name', 'Unknown')}")

    elif args.command == "get-trace":
        if not args.trace_id:
            print("Error: --trace-id required")
            return
        trace = query_api.get_trace(args.trace_id)
        if trace:
            print(json.dumps(trace, indent=2, default=str))
        else:
            print(f"Trace {args.trace_id} not found")

    elif args.command == "cost-by-project":
        costs = query_api.get_cost_by_project(days=args.days)
        print(f"Cost by project (last {args.days} days):")
        for project, cost in sorted(costs.items(), key=lambda x: x[1], reverse=True):
            print(f"  {project}: ${cost:.4f}")

    elif args.command == "cost-by-agent":
        costs = query_api.get_cost_by_agent(days=args.days)
        print(f"Cost by agent (last {args.days} days):")
        for agent, cost in sorted(costs.items(), key=lambda x: x[1], reverse=True):
            print(f"  {agent}: ${cost:.4f}")

    elif args.command == "tool-stats":
        stats = query_api.get_tool_latency_stats(tool_name=args.tool_name, days=args.days)
        print(f"Tool latency stats (last {args.days} days):")
        print(json.dumps(stats, indent=2))

    elif args.command == "tool-errors":
        errors = query_api.get_tool_error_rate(tool_name=args.tool_name, days=args.days)
        print(f"Tool error rates (last {args.days} days):")
        for tool, stats in errors.items():
            print(f"  {tool}: {stats['error_rate_percent']}% error rate ({stats['error_count']}/{stats['total_calls']})")

    elif args.command == "error-summary":
        summary = query_api.get_error_summary(days=args.days)
        print(f"Error summary (last {args.days} days):")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
