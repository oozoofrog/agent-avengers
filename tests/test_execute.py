#!/usr/bin/env python3
"""Tests for execute.py"""

import json
import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from execute import (
    generate_openclaw_commands,
    save_execution_script,
)
from exceptions import MissionNotFoundError


class TestGenerateOpenclawCommands:
    """Test OpenClaw command generation"""

    def test_spawn_command_generation(self, sample_plan):
        """Test generating spawn commands"""
        commands = generate_openclaw_commands(sample_plan)

        assert len(commands) == 2  # 2 phases

        # Phase 1: parallel with 2 spawn commands
        phase1 = commands[0]
        assert phase1["phase"] == 1
        assert phase1["parallel"] is True
        assert len(phase1["commands"]) == 2

        # Check first spawn command
        cmd0 = phase1["commands"][0]
        assert cmd0["type"] == "spawn"
        assert cmd0["agent_id"] == "test_agent_00"
        assert "sessions_spawn" in cmd0["code"]
        assert "Research competitors" in cmd0["code"]
        assert '"sonnet"' in cmd0["code"]
        assert "1800" in cmd0["code"]

    def test_send_command_generation(self, sample_plan):
        """Test generating send commands"""
        commands = generate_openclaw_commands(sample_plan)

        # Phase 2: sequential with 1 send command
        phase2 = commands[1]
        assert phase2["phase"] == 2
        assert phase2["parallel"] is False
        assert len(phase2["commands"]) == 1

        # Check send command
        cmd = phase2["commands"][0]
        assert cmd["type"] == "send"
        assert cmd["agent_id"] == "test_agent_02"
        assert "sessions_send" in cmd["code"]
        assert "existing_session" in cmd["code"]
        assert "Write final report" in cmd["code"]
        assert "600" in cmd["code"]

    def test_parallel_flag_preservation(self, sample_plan):
        """Test that parallel flags are preserved"""
        commands = generate_openclaw_commands(sample_plan)

        assert commands[0]["parallel"] is True
        assert commands[1]["parallel"] is False

    def test_empty_plan(self):
        """Test handling empty plan"""
        plan = {"phases": [], "commands": []}
        commands = generate_openclaw_commands(plan)

        assert commands == []

    def test_agent_without_command(self):
        """Test handling agent with no matching command"""
        plan = {
            "phases": [
                {
                    "phase": 1,
                    "parallel": False,
                    "agents": [{"id": "missing_agent", "type": "researcher"}]
                }
            ],
            "commands": []
        }

        commands = generate_openclaw_commands(plan)

        assert len(commands) == 1
        assert len(commands[0]["commands"]) == 0


class TestSaveExecutionScript:
    """Test execution script saving"""

    def test_save_script_creates_file(self, temp_mission_dir, sample_plan):
        """Test that script file is created"""
        commands = generate_openclaw_commands(sample_plan)
        script_path = save_execution_script(commands, temp_mission_dir)

        assert script_path.exists()
        assert script_path.name == "execute_commands.md"

    def test_script_content_structure(self, temp_mission_dir, sample_plan):
        """Test script file content structure"""
        commands = generate_openclaw_commands(sample_plan)
        script_path = save_execution_script(commands, temp_mission_dir)

        content = script_path.read_text()

        # Check headers
        assert "# Avengers Execute Commands" in content
        assert "## Phase 1 (병렬)" in content
        assert "## Phase 2 (순차)" in content

        # Check agent sections
        assert "### test_agent_00" in content
        assert "### test_agent_01" in content
        assert "### test_agent_02" in content

        # Check code blocks
        assert "```javascript" in content
        assert "sessions_spawn" in content
        assert "sessions_send" in content

    def test_script_returns_path(self, temp_mission_dir, sample_plan):
        """Test that function returns correct path"""
        commands = generate_openclaw_commands(sample_plan)
        script_path = save_execution_script(commands, temp_mission_dir)

        assert isinstance(script_path, Path)
        assert script_path.parent == temp_mission_dir
        assert script_path.name == "execute_commands.md"


class TestLoadMissionError:
    """Test load_mission error handling"""

    def test_missing_mission_directory(self, temp_workspace):
        """Test error when mission directory doesn't exist"""
        os.environ["AVENGERS_WORKSPACE"] = temp_workspace

        import importlib
        import execute
        importlib.reload(execute)

        # load_mission will raise MissionNotFoundError
        with pytest.raises(MissionNotFoundError):
            execute.load_mission("nonexistent_mission")

    def test_missing_mission_json(self, temp_workspace):
        """Test error when mission.json doesn't exist"""
        os.environ["AVENGERS_WORKSPACE"] = temp_workspace

        mission_dir = Path(temp_workspace) / "avengers-missions" / "test"
        mission_dir.mkdir(parents=True)

        import importlib
        import execute
        importlib.reload(execute)

        with pytest.raises(MissionNotFoundError):
            execute.load_mission("test")

    def test_missing_execution_plan(self, temp_workspace, sample_mission):
        """Test error when execution_plan.json doesn't exist"""
        os.environ["AVENGERS_WORKSPACE"] = temp_workspace

        mission_dir = Path(temp_workspace) / "avengers-missions" / "test"
        mission_dir.mkdir(parents=True)

        # Create mission.json but not execution_plan.json
        mission_file = mission_dir / "mission.json"
        mission_file.write_text(json.dumps(sample_mission))

        import importlib
        import execute
        importlib.reload(execute)

        # Will raise MissionNotFoundError because execution_plan.json is missing
        from exceptions import PlanNotFoundError
        with pytest.raises((MissionNotFoundError, PlanNotFoundError)):
            execute.load_mission("test")


class TestIntegration:
    """Integration tests for execute.py"""

    def test_full_execution_workflow(self, temp_workspace, sample_mission, sample_plan):
        """Test complete execution workflow"""
        # Setup mission directory
        mission_dir = Path(temp_workspace) / "avengers-missions" / "test_mission_123"
        mission_dir.mkdir(parents=True)
        (mission_dir / "logs").mkdir()

        # Create mission and plan files
        sample_mission["path"] = str(mission_dir)
        (mission_dir / "mission.json").write_text(json.dumps(sample_mission))
        (mission_dir / "execution_plan.json").write_text(json.dumps(sample_plan))

        # Set environment variable and reload modules
        os.environ["AVENGERS_WORKSPACE"] = temp_workspace

        import importlib
        import config
        import utils
        import execute
        importlib.reload(config)
        importlib.reload(utils)
        importlib.reload(execute)

        # Load mission
        mission, plan = execute.load_mission("test_mission_123")

        assert mission["id"] == "test_mission_123"
        assert plan["total_agents"] == 3

        # Generate commands
        commands = generate_openclaw_commands(plan)

        assert len(commands) == 2
        assert commands[0]["parallel"] is True
        assert commands[1]["parallel"] is False

        # Save script
        script_path = save_execution_script(commands, mission_dir)

        assert script_path.exists()
        content = script_path.read_text()
        assert "sessions_spawn" in content
        assert "sessions_send" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
