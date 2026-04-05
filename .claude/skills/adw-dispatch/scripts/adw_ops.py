#!/usr/bin/env python3
"""
ADW Operations Module

Core operations for ADW dispatch routing.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List


class ExecutionMode(Enum):
    """ADW execution modes"""
    LOCAL_HAIKU = "local"
    GITHUB_ACTIONS_OPUS = "github"
    AUTO = "auto"


@dataclass
class TaskEstimate:
    """Task complexity estimate"""
    task: str
    estimated_tokens: int
    files_touched: int
    complexity_level: str  # "low", "medium", "high"
    recommended_mode: ExecutionMode
    reasoning: str


@dataclass
class DispatchResult:
    """Result of ADW dispatch"""
    success: bool
    mode: ExecutionMode
    task: str
    message: str
    workflow_run_url: Optional[str] = None
    worktree_path: Optional[str] = None
    error: Optional[str] = None


def load_settings() -> Dict[str, Any]:
    """Load skill settings from config file"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {}


def estimate_complexity(task: str, settings: Optional[Dict] = None) -> TaskEstimate:
    """
    Estimate task complexity based on keywords and heuristics.

    Args:
        task: Task description
        settings: Optional settings override

    Returns:
        TaskEstimate with complexity analysis
    """
    if settings is None:
        settings = load_settings()

    factors = settings.get("complexity_factors", {})
    keywords_high = factors.get("keywords_high", [])
    keywords_medium = factors.get("keywords_medium", [])
    keywords_low = factors.get("keywords_low", [])
    base_tokens = factors.get("base_tokens_per_file", 2000)

    task_lower = task.lower()

    # Determine complexity level
    complexity_level = "medium"
    multiplier = 1.5

    if any(kw in task_lower for kw in keywords_high):
        complexity_level = "high"
        multiplier = factors.get("multiplier_high", 3.0)
    elif any(kw in task_lower for kw in keywords_low):
        complexity_level = "low"
        multiplier = factors.get("multiplier_low", 0.5)
    elif any(kw in task_lower for kw in keywords_medium):
        complexity_level = "medium"
        multiplier = factors.get("multiplier_medium", 1.5)

    # Estimate files touched based on task scope
    words = task.split()
    files_touched = 1
    if len(words) > 20:
        files_touched = 3
    if len(words) > 50:
        files_touched = 5
    if "all" in task_lower or "entire" in task_lower:
        files_touched = 10

    # Calculate estimated tokens
    estimated_tokens = int(base_tokens * files_touched * multiplier)

    # Determine recommended mode
    routing = settings.get("routing", {})
    haiku_threshold = routing.get("haiku_threshold", 5000)
    opus_threshold = routing.get("opus_threshold", 20000)

    if estimated_tokens < haiku_threshold:
        recommended_mode = ExecutionMode.LOCAL_HAIKU
        reasoning = f"Low complexity ({estimated_tokens} tokens < {haiku_threshold})"
    elif estimated_tokens > opus_threshold:
        recommended_mode = ExecutionMode.GITHUB_ACTIONS_OPUS
        reasoning = f"High complexity ({estimated_tokens} tokens > {opus_threshold})"
    elif files_touched <= 2 and complexity_level != "high":
        recommended_mode = ExecutionMode.LOCAL_HAIKU
        reasoning = f"Limited scope ({files_touched} files, {complexity_level} complexity)"
    else:
        recommended_mode = ExecutionMode.GITHUB_ACTIONS_OPUS
        reasoning = f"Moderate+ complexity requiring multi-context reasoning"

    return TaskEstimate(
        task=task,
        estimated_tokens=estimated_tokens,
        files_touched=files_touched,
        complexity_level=complexity_level,
        recommended_mode=recommended_mode,
        reasoning=reasoning
    )


def dispatch_local(task: str, working_dir: Optional[str] = None) -> DispatchResult:
    """
    Dispatch ADW to local Haiku execution.

    Args:
        task: Task to execute
        working_dir: Working directory

    Returns:
        DispatchResult
    """
    settings = load_settings()
    local_config = settings.get("local_execution", {})

    if working_dir is None:
        working_dir = local_config.get("working_dir") or os.getcwd()

    model = local_config.get("model", "claude-haiku-4-5-20251001")
    max_turns = local_config.get("max_turns", 50)

    try:
        # Build Claude CLI command
        cmd = [
            "claude",
            "-p", task,
            "--model", model,
            "--dangerously-skip-permissions",
            "--max-turns", str(max_turns)
        ]

        print(f"Executing local ADW with Haiku...")
        print(f"Task: {task[:100]}...")
        print(f"Model: {model}")
        print(f"Working dir: {working_dir}")

        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            return DispatchResult(
                success=True,
                mode=ExecutionMode.LOCAL_HAIKU,
                task=task,
                message=f"Local execution completed successfully",
            )
        else:
            return DispatchResult(
                success=False,
                mode=ExecutionMode.LOCAL_HAIKU,
                task=task,
                message=f"Local execution failed",
                error=result.stderr
            )

    except subprocess.TimeoutExpired:
        return DispatchResult(
            success=False,
            mode=ExecutionMode.LOCAL_HAIKU,
            task=task,
            message="Local execution timed out",
            error="Execution exceeded 10 minute timeout"
        )
    except Exception as e:
        return DispatchResult(
            success=False,
            mode=ExecutionMode.LOCAL_HAIKU,
            task=task,
            message="Local execution error",
            error=str(e)
        )


def dispatch_github(task: str, working_dir: Optional[str] = None) -> DispatchResult:
    """
    Dispatch ADW to GitHub Actions for Opus execution.

    Args:
        task: Task to execute
        working_dir: Working directory for context

    Returns:
        DispatchResult with workflow URL
    """
    settings = load_settings()
    gh_config = settings.get("github_actions", {})

    repo = gh_config.get("repo", "gblack686/consulting-co")
    workflow = gh_config.get("workflow", "adw-plan-build-review.yml")
    branch = gh_config.get("branch", "main")

    try:
        # Trigger GitHub Actions workflow
        cmd = [
            "gh", "workflow", "run", workflow,
            "--repo", repo,
            "--ref", branch,
            "-f", f"task={task}",
            "-f", f"working_dir={working_dir or '.'}"
        ]

        print(f"Triggering GitHub Actions ADW...")
        print(f"Task: {task[:100]}...")
        print(f"Workflow: {workflow}")
        print(f"Repo: {repo}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            workflow_url = f"https://github.com/{repo}/actions"
            return DispatchResult(
                success=True,
                mode=ExecutionMode.GITHUB_ACTIONS_OPUS,
                task=task,
                message=f"GitHub Actions workflow triggered",
                workflow_run_url=workflow_url
            )
        else:
            return DispatchResult(
                success=False,
                mode=ExecutionMode.GITHUB_ACTIONS_OPUS,
                task=task,
                message="Failed to trigger GitHub Actions",
                error=result.stderr
            )

    except Exception as e:
        return DispatchResult(
            success=False,
            mode=ExecutionMode.GITHUB_ACTIONS_OPUS,
            task=task,
            message="GitHub Actions dispatch error",
            error=str(e)
        )


def auto_route(task: str, working_dir: Optional[str] = None, force_mode: Optional[str] = None) -> DispatchResult:
    """
    Automatically route task to appropriate execution mode.

    Args:
        task: Task to execute
        working_dir: Working directory
        force_mode: Optional mode override ("local" or "github")

    Returns:
        DispatchResult
    """
    # Handle force mode
    if force_mode:
        if force_mode.lower() == "local":
            return dispatch_local(task, working_dir)
        elif force_mode.lower() == "github":
            return dispatch_github(task, working_dir)

    # Estimate complexity
    estimate = estimate_complexity(task)

    print(f"\n{'='*60}")
    print(f"ADW Routing Analysis")
    print(f"{'='*60}")
    print(f"Task: {task[:80]}...")
    print(f"Estimated tokens: {estimate.estimated_tokens}")
    print(f"Files touched: {estimate.files_touched}")
    print(f"Complexity: {estimate.complexity_level}")
    print(f"Recommended: {estimate.recommended_mode.value}")
    print(f"Reasoning: {estimate.reasoning}")
    print(f"{'='*60}\n")

    # Route based on recommendation
    if estimate.recommended_mode == ExecutionMode.LOCAL_HAIKU:
        return dispatch_local(task, working_dir)
    else:
        return dispatch_github(task, working_dir)


if __name__ == "__main__":
    # Quick test
    test_tasks = [
        "Fix typo in README",
        "Add user authentication with JWT",
        "Refactor entire database layer for PostgreSQL migration"
    ]

    for task in test_tasks:
        estimate = estimate_complexity(task)
        print(f"\nTask: {task}")
        print(f"  Tokens: {estimate.estimated_tokens}")
        print(f"  Complexity: {estimate.complexity_level}")
        print(f"  Recommended: {estimate.recommended_mode.value}")
        print(f"  Reasoning: {estimate.reasoning}")
