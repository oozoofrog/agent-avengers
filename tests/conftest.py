#!/usr/bin/env python3
"""Shared pytest fixtures for Agent Avengers tests"""

import json
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_workspace():
    """Temporary workspace directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_mission_dir(temp_workspace):
    """Temporary mission directory with structure"""
    mission_path = Path(temp_workspace) / "avengers-missions" / "test_mission_123"
    mission_path.mkdir(parents=True)
    (mission_path / "agents").mkdir()
    (mission_path / "outputs").mkdir()
    (mission_path / "logs").mkdir()

    yield mission_path


@pytest.fixture
def sample_mission():
    """Sample mission.json data"""
    return {
        "id": "test_mission_123",
        "task": "Test mission task",
        "status": "initializing",
        "created_at": "2026-02-06T12:00:00",
        "path": "/tmp/test/test_mission_123"
    }


@pytest.fixture
def sample_plan():
    """Sample execution_plan.json data"""
    return {
        "total_agents": 3,
        "total_phases": 2,
        "phases": [
            {
                "phase": 1,
                "parallel": True,
                "agents": [
                    {
                        "id": "test_agent_00",
                        "type": "researcher",
                        "emoji": "🔬",
                        "description": "Research data"
                    },
                    {
                        "id": "test_agent_01",
                        "type": "analyst",
                        "emoji": "🔍",
                        "description": "Analyze patterns"
                    }
                ]
            },
            {
                "phase": 2,
                "parallel": False,
                "agents": [
                    {
                        "id": "test_agent_02",
                        "type": "writer",
                        "emoji": "🖊️",
                        "description": "Write report"
                    }
                ]
            }
        ],
        "commands": [
            {
                "agent_id": "test_agent_00",
                "type": "spawn",
                "params": {
                    "task": "Research competitors",
                    "model": "sonnet",
                    "runTimeoutSeconds": 1800,
                    "cleanup": "keep",
                    "label": "test_agent_00"
                }
            },
            {
                "agent_id": "test_agent_01",
                "type": "spawn",
                "params": {
                    "task": "Analyze market trends",
                    "model": "opus",
                    "runTimeoutSeconds": 1200,
                    "cleanup": "keep",
                    "label": "test_agent_01"
                }
            },
            {
                "agent_id": "test_agent_02",
                "type": "send",
                "params": {
                    "label": "existing_session",
                    "message": "Write final report",
                    "timeoutSeconds": 600
                }
            }
        ]
    }


@pytest.fixture
def sample_agent_outputs():
    """Sample agent output files content"""
    return {
        "test_agent_00": "# Research Results\n\nFound important data about competitors.",
        "test_agent_01": "# Analysis\n\nMarket trends show growth in sector X.",
        "test_agent_02": "# Final Report\n\nConclusion: Opportunities in market Y."
    }


@pytest.fixture
def sample_logs():
    """Sample JSONL log entries"""
    return [
        {
            "timestamp": "2026-02-06T12:00:00",
            "event": "mission_created",
            "data": {"mission_id": "test_mission_123"}
        },
        {
            "timestamp": "2026-02-06T12:05:00",
            "event": "execution_started",
            "data": {"total_phases": 2, "total_agents": 3}
        },
        {
            "timestamp": "2026-02-06T12:10:00",
            "event": "agent_completed",
            "data": {"agent_id": "test_agent_00"}
        }
    ]
