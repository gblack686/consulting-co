#!/usr/bin/env python3
"""
Trace builder for converting event sequences into Langfuse observations.
Phase 2: Multi-Event Trace Construction
"""

import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ToolInvocation:
    """Represents a matched PreToolUse/PostToolUse pair."""
    tool_name: str
    sequence_number: int
    pre_event: Dict[str, Any]
    post_event: Dict[str, Any]
    latency_ms: int
    input_data: Dict[str, Any]
    output_data: str
    status: str = "success"
    error_message: Optional[str] = None


class TraceBuilder:
    """Build Langfuse trace from event sequence."""

    def __init__(self, session_id: str, events: List[Dict[str, Any]]):
        """Initialize trace builder.

        Args:
            session_id: Unique session identifier
            events: List of buffered hook events
        """
        self.session_id = session_id
        self.events = sorted(events, key=lambda e: self._get_timestamp(e))
        self.tool_pairs = self._match_tool_events()

        # PHASE 3: Detect parent-child relationships
        self.parent_session_id = self._detect_parent_session()
        self.subagent_calls = self._detect_subagent_calls()
        self.hierarchy_depth = self._calculate_hierarchy_depth()

        # PHASE 4: Enhanced metadata
        self.agent_id = self._generate_agent_id()
        self.source_app = self._detect_source_app()
        self.has_errors = self._detect_errors()

    def _get_timestamp(self, event: Dict) -> float:
        """Extract and convert timestamp to float for sorting.

        Args:
            event: Event dict

        Returns:
            Timestamp as float (epoch seconds)
        """
        ts = event.get("timestamp", datetime.now().isoformat())
        try:
            if isinstance(ts, str):
                # Parse ISO format
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                return dt.timestamp()
            return float(ts)
        except Exception:
            return 0.0

    def _match_tool_events(self) -> List[ToolInvocation]:
        """Match PreToolUse with PostToolUse events.

        Returns:
            List of ToolInvocation pairs
        """
        pre_events = [e for e in self.events if e.get("hook_event_type") == "PreToolUse"]
        post_events = [e for e in self.events if e.get("hook_event_type") == "PostToolUse"]

        pairs = []
        used_post_indices = set()

        for pre_event in pre_events:
            pre_ts = self._get_timestamp(pre_event)

            # Find matching PostToolUse (next one chronologically that hasn't been used)
            matching_post = None
            matching_post_idx = None

            for idx, post_event in enumerate(post_events):
                if idx in used_post_indices:
                    continue

                post_ts = self._get_timestamp(post_event)
                if post_ts > pre_ts:
                    matching_post = post_event
                    matching_post_idx = idx
                    break

            if matching_post:
                used_post_indices.add(matching_post_idx)

                # Extract tool details
                pre_payload = pre_event.get("hook_data", {})
                post_payload = post_event.get("hook_data", {})

                tool_name = pre_payload.get("tool_name", "unknown")
                latency_ms = int((self._get_timestamp(matching_post) - pre_ts) * 1000)

                # Check for errors
                is_error = post_payload.get("error") is not None
                error_msg = post_payload.get("error")

                tool_inv = ToolInvocation(
                    tool_name=tool_name,
                    sequence_number=len(pairs) + 1,
                    pre_event=pre_event,
                    post_event=matching_post,
                    latency_ms=max(latency_ms, 0),  # Ensure non-negative
                    input_data=pre_payload.get("input", {}),
                    output_data=str(post_payload.get("output", ""))[:500],  # Truncate
                    status="error" if is_error else "success",
                    error_message=error_msg
                )
                pairs.append(tool_inv)

        return pairs

    def get_user_prompts(self) -> List[Dict[str, Any]]:
        """Extract user prompt events.

        Returns:
            List of user prompt event dicts
        """
        return [e for e in self.events if e.get("hook_event_type") == "UserPromptSubmit"]

    def get_subagent_events(self) -> List[Dict[str, Any]]:
        """Extract subagent execution events.

        Returns:
            List of subagent event dicts
        """
        return [e for e in self.events if e.get("hook_event_type") == "SubagentStop"]

    def _generate_agent_id(self) -> str:
        """Generate display-friendly agent ID.

        PHASE 4: Agent Identity Tracking

        Format: {source_app}:{session_id[:8]}

        Returns:
            Agent ID string
        """
        source = self._detect_source_app()
        short_session = self.session_id[:8] if len(self.session_id) > 8 else self.session_id
        return f"{source}:{short_session}"

    def _detect_source_app(self) -> str:
        """Detect source application/project from events.

        PHASE 4: Source Application Tracking

        Returns:
            Source app name (default: "claude-code")
        """
        for event in self.events:
            # Check hook data for source_app
            source = event.get("hook_data", {}).get("source_app")
            if source:
                return source

            # Check in event metadata
            if "source_app" in event:
                return event.get("source_app")

        # Fallback to session prefix
        if self.session_id.startswith("session_"):
            return "claude-code"

        return "claude-code"

    def _detect_errors(self) -> bool:
        """Detect if any tool or subagent calls failed.

        PHASE 4: Error Tracking

        Returns:
            True if any errors detected, False otherwise
        """
        # Check for tool errors
        for tool_inv in self.tool_pairs:
            if tool_inv.status == "error" or tool_inv.error_message:
                return True

        # Check for subagent errors
        for call in self.subagent_calls:
            if call.get("error") or call.get("status") == "error":
                return True

        # Check for PostToolUse errors in raw events
        for event in self.events:
            if event.get("hook_event_type") == "PostToolUse":
                if event.get("hook_data", {}).get("error"):
                    return True

        return False

    def _detect_parent_session(self) -> Optional[str]:
        """Detect if this is a subagent by finding parent_session_id in events.

        PHASE 3: Subagent Detection

        Returns:
            Parent session ID if this is a subagent, None otherwise
        """
        for event in self.events:
            event_data = event.get("hook_data", {})

            # Check for parent_session_id in hook data
            parent_id = event_data.get("parent_session_id")
            if parent_id:
                return parent_id

            # Check in event metadata
            if "parent_session_id" in event:
                return event.get("parent_session_id")

        return None

    def _detect_subagent_calls(self) -> List[Dict[str, Any]]:
        """Detect subagent invocations from SubagentStop events.

        PHASE 3: Subagent Call Detection

        Returns:
            List of subagent call details
        """
        subagent_calls = []

        for event in self.events:
            if event.get("hook_event_type") == "SubagentStop":
                event_data = event.get("hook_data", {})

                call_info = {
                    "subagent_session_id": event_data.get("subagent_session_id", "unknown"),
                    "timestamp": event.get("timestamp"),
                    "purpose": event_data.get("purpose", ""),
                    "outcome": event_data.get("outcome", ""),
                    "status": event_data.get("status", "completed"),
                    "duration_ms": event_data.get("duration_ms", 0),
                    "error": event_data.get("error")
                }
                subagent_calls.append(call_info)

        return subagent_calls

    def _calculate_hierarchy_depth(self, max_depth: int = 10) -> int:
        """Calculate hierarchy depth (0 = root, 1+ = subagent nesting).

        PHASE 3: Hierarchy Tracking

        Args:
            max_depth: Maximum depth to check (safety limit)

        Returns:
            Depth in the agent hierarchy
        """
        # If this has a parent, it's at least depth 1
        if self.parent_session_id:
            # Try to load parent events and check their depth
            # For now, just return 1 (could be enhanced to recursively check)
            return 1

        return 0

    def get_event_summary(self) -> Dict[str, Any]:
        """Get summary of events for this session.

        Returns:
            Summary dict with event counts and types
        """
        event_types = {}
        for event in self.events:
            event_type = event.get("hook_event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            "total_events": len(self.events),
            "event_types": event_types,
            "tool_invocations": len(self.tool_pairs),
            "user_prompts": len(self.get_user_prompts()),
            "subagent_events": len(self.get_subagent_events()),
            # PHASE 3: Subagent hierarchy info
            "is_subagent": self.parent_session_id is not None,
            "parent_session_id": self.parent_session_id,
            "hierarchy_depth": self.hierarchy_depth,
            "subagent_calls": len(self.subagent_calls),
            # PHASE 4: Enhanced metadata
            "agent_id": self.agent_id,
            "source_app": self.source_app,
            "has_errors": self.has_errors
        }

    def build_observations(self) -> List[Dict[str, Any]]:
        """Build Langfuse observations from events.

        This implements Phase 2: Transform events into observations.

        Returns:
            List of observation dicts ready for Langfuse
        """
        observations = []

        # OBSERVATION 1: User prompts
        for prompt_event in self.get_user_prompts():
            prompt_data = prompt_event.get("hook_data", {})
            prompt_text = prompt_data.get("user_input", "")

            observation = {
                "type": "SPAN",
                "name": "user-prompt",
                "input": prompt_text[:5000],  # Truncate
                "metadata": {
                    "event_type": "UserPromptSubmit",
                    "timestamp": prompt_event.get("timestamp"),
                    "source_event_id": prompt_event.get("hook_data", {}).get("event_id", "unknown")
                }
            }
            observations.append(observation)

        # OBSERVATION 2: Tool invocations
        for tool_inv in self.tool_pairs:
            observation = {
                "type": "SPAN",
                "name": f"tool-{tool_inv.tool_name}-{tool_inv.sequence_number}",
                "input": json.dumps(tool_inv.input_data)[:500],
                "output": tool_inv.output_data,
                "metadata": {
                    "event_type": "ToolInvocation",
                    "tool_name": tool_inv.tool_name,
                    "sequence_number": tool_inv.sequence_number,
                    "latency_ms": tool_inv.latency_ms,
                    "status": tool_inv.status,
                    "error_message": tool_inv.error_message,
                    "start_timestamp": tool_inv.pre_event.get("timestamp"),
                    "end_timestamp": tool_inv.post_event.get("timestamp"),
                    # PHASE 4: Agent context
                    "agent_id": self.agent_id,
                    "source_app": self.source_app
                }
            }
            observations.append(observation)

        # OBSERVATION 3: Subagent executions
        for subagent_event in self.get_subagent_events():
            subagent_data = subagent_event.get("hook_data", {})
            subagent_session_id = subagent_data.get("subagent_session_id", "unknown")

            observation = {
                "type": "SPAN",
                "name": f"subagent-{subagent_session_id[:12]}",
                "metadata": {
                    "event_type": "SubagentExecution",
                    "subagent_session_id": subagent_session_id,
                    "parent_session_id": self.session_id,
                    "child_trace_id": subagent_session_id,  # Link to child trace
                    "hierarchy_depth": 1,
                    "purpose": subagent_data.get("purpose", ""),
                    "outcome": subagent_data.get("outcome", ""),
                    "status": subagent_data.get("status", "completed"),
                    "timestamp": subagent_event.get("timestamp"),
                    # PHASE 4: Agent context
                    "agent_id": self.agent_id,
                    "source_app": self.source_app
                }
            }
            observations.append(observation)

        return observations

    def print_summary(self) -> None:
        """Pretty print trace builder summary."""
        summary = self.get_event_summary()

        print("\n" + "="*60)
        print(f"🔨 TRACE BUILDER: {self.session_id[:16]}...")
        print("="*60)
        print(f"Total Events: {summary['total_events']}")

        # PHASE 4: Show agent identity
        print(f"Agent ID: {summary['agent_id']}")
        print(f"Source: {summary['source_app']}")
        if summary['has_errors']:
            print(f"⚠️  ERRORS DETECTED in this trace")

        # PHASE 3: Show hierarchy info
        if summary['is_subagent']:
            print(f"⚠️  SUBAGENT TRACE (depth={summary['hierarchy_depth']})")
            print(f"   Parent: {summary['parent_session_id'][:16]}...")
        else:
            print(f"✓ ROOT AGENT TRACE")

        print(f"\nEvent Types:")
        for event_type, count in summary['event_types'].items():
            print(f"  {event_type}: {count}")

        print(f"\nObservations to Create:")
        print(f"  User Prompts: {summary['user_prompts']}")
        print(f"  Tool Invocations: {summary['tool_invocations']}")
        print(f"  Subagent Executions: {summary['subagent_events']}")

        if self.tool_pairs:
            print(f"\nTool Breakdown:")
            tool_names = {}
            for tool in self.tool_pairs:
                tool_names[tool.tool_name] = tool_names.get(tool.tool_name, 0) + 1
            for tool_name, count in tool_names.items():
                print(f"  {tool_name}: {count}")

        # PHASE 3: Show subagent calls
        if self.subagent_calls:
            print(f"\nSubagent Calls: {len(self.subagent_calls)}")
            for i, call in enumerate(self.subagent_calls, 1):
                print(f"  {i}. {call['subagent_session_id'][:12]}...")
                if call.get('purpose'):
                    print(f"     Purpose: {call['purpose'][:50]}")
                if call.get('error'):
                    print(f"     Error: {call['error'][:50]}")

        print()


def main():
    """CLI for trace builder debugging."""
    import sys
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Trace builder utilities")
    parser.add_argument("command", choices=["analyze", "export"], help="Command")
    parser.add_argument("--session-id", required=True, help="Session ID")
    parser.add_argument("--events-file", help="Events JSON file")
    parser.add_argument("--output", help="Output file for observations")

    args = parser.parse_args()

    # Load events
    if args.events_file:
        with open(args.events_file, 'r') as f:
            events = json.load(f)
    else:
        # Try to load from default buffer location
        buffer_file = Path.home() / ".claude" / "logs" / f"event_buffer_{args.session_id}.json"
        if not buffer_file.exists():
            print(f"❌ No event buffer found for {args.session_id}")
            sys.exit(1)
        with open(buffer_file, 'r') as f:
            events = json.load(f)

    builder = TraceBuilder(args.session_id, events)

    if args.command == "analyze":
        builder.print_summary()
        observations = builder.build_observations()
        print(f"Generated {len(observations)} observations")

    elif args.command == "export":
        if not args.output:
            print("Error: --output required for export")
            sys.exit(1)
        observations = builder.build_observations()
        with open(args.output, 'w') as f:
            json.dump(observations, f, indent=2)
        print(f"✓ Exported {len(observations)} observations to {args.output}")


if __name__ == "__main__":
    main()
