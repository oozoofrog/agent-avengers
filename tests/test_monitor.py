#!/usr/bin/env python3
"""Tests for monitor.py"""

import json
import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from monitor import (
    check_agent_outputs,
    read_logs,
    print_status,
)
from exceptions import MissionNotFoundError


class TestCheckAgentOutputs:
    """Test agent output checking"""

    def test_all_outputs_completed(self, temp_mission_dir, sample_plan, sample_agent_outputs):
        """Test when all agent outputs exist"""
        outputs_dir = temp_mission_dir / "outputs"

        # Create output files
        for agent_id, content in sample_agent_outputs.items():
            (outputs_dir / f"{agent_id}.md").write_text(content)

        results = check_agent_outputs(temp_mission_dir, sample_plan)

        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)
        assert all(r["output_size"] > 0 for r in results)

    def test_some_outputs_pending(self, temp_mission_dir, sample_plan):
        """Test when some outputs are missing"""
        outputs_dir = temp_mission_dir / "outputs"

        # Create only one output file
        (outputs_dir / "test_agent_00.md").write_text("Research complete")

        results = check_agent_outputs(temp_mission_dir, sample_plan)

        assert len(results) == 3
        assert results[0]["status"] == "completed"
        assert results[1]["status"] == "pending"
        assert results[2]["status"] == "pending"

    def test_no_outputs(self, temp_mission_dir, sample_plan):
        """Test when no outputs exist"""
        results = check_agent_outputs(temp_mission_dir, sample_plan)

        assert len(results) == 3
        assert all(r["status"] == "pending" for r in results)
        assert all(r["output_size"] == 0 for r in results)

    def test_output_file_paths(self, temp_mission_dir, sample_plan):
        """Test that output file paths are correct"""
        results = check_agent_outputs(temp_mission_dir, sample_plan)

        assert "test_agent_00.md" in results[0]["output_file"]
        assert "test_agent_01.md" in results[1]["output_file"]
        assert "test_agent_02.md" in results[2]["output_file"]

    def test_none_plan_handling(self, temp_mission_dir):
        """Test graceful handling when plan is None"""
        results = check_agent_outputs(temp_mission_dir, None)

        assert results == []

    def test_empty_commands_in_plan(self, temp_mission_dir):
        """Test handling plan with no commands"""
        plan = {"commands": []}
        results = check_agent_outputs(temp_mission_dir, plan)

        assert results == []


class TestReadLogs:
    """Test log reading"""

    def test_read_existing_logs(self, temp_mission_dir, sample_logs):
        """Test reading existing log file"""
        log_file = temp_mission_dir / "logs" / "execution.jsonl"

        # Write sample logs
        with open(log_file, "w") as f:
            for entry in sample_logs:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        logs = read_logs(temp_mission_dir)

        assert len(logs) == 3
        assert logs[0]["event"] == "mission_created"
        assert logs[1]["event"] == "execution_started"
        assert logs[2]["event"] == "agent_completed"

    def test_read_with_limit(self, temp_mission_dir, sample_logs):
        """Test log reading with limit"""
        log_file = temp_mission_dir / "logs" / "execution.jsonl"

        with open(log_file, "w") as f:
            for entry in sample_logs:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        logs = read_logs(temp_mission_dir, limit=2)

        assert len(logs) == 2
        # Should get last 2 logs
        assert logs[0]["event"] == "execution_started"
        assert logs[1]["event"] == "agent_completed"

    def test_read_nonexistent_log_file(self, temp_mission_dir):
        """Test reading when log file doesn't exist"""
        logs = read_logs(temp_mission_dir)

        assert logs == []

    def test_read_empty_log_file(self, temp_mission_dir):
        """Test reading empty log file"""
        log_file = temp_mission_dir / "logs" / "execution.jsonl"
        log_file.write_text("")

        logs = read_logs(temp_mission_dir)

        assert logs == []

    def test_skip_empty_lines(self, temp_mission_dir):
        """Test that empty lines are skipped"""
        log_file = temp_mission_dir / "logs" / "execution.jsonl"

        with open(log_file, "w") as f:
            f.write(json.dumps({"event": "test1"}) + "\n")
            f.write("\n")  # Empty line
            f.write(json.dumps({"event": "test2"}) + "\n")

        logs = read_logs(temp_mission_dir)

        assert len(logs) == 2
        assert logs[0]["event"] == "test1"
        assert logs[1]["event"] == "test2"

    def test_default_limit(self, temp_mission_dir):
        """Test default limit of 20"""
        log_file = temp_mission_dir / "logs" / "execution.jsonl"

        # Create 25 log entries
        with open(log_file, "w") as f:
            for i in range(25):
                f.write(json.dumps({"event": f"event_{i}"}) + "\n")

        logs = read_logs(temp_mission_dir)

        assert len(logs) == 20
        # Should get last 20 (events 5-24)
        assert logs[0]["event"] == "event_5"
        assert logs[-1]["event"] == "event_24"


class TestPrintStatus:
    """Test status printing"""

    def test_print_mission_info(self, capsys, sample_mission, sample_plan):
        """Test mission info printing"""
        # agent_results must not be empty to avoid ZeroDivisionError in monitor.py
        agent_results = [
            {"agent_id": "test_agent_00", "status": "pending", "output_size": 0}
        ]
        logs = []

        print_status(sample_mission, sample_plan, agent_results, logs)

        captured = capsys.readouterr()
        output = captured.out

        assert "test_mission_123" in output
        assert sample_mission["status"] in output
        assert sample_mission["created_at"] in output

    def test_print_agent_progress(self, capsys, sample_mission, sample_plan):
        """Test agent progress display"""
        agent_results = [
            {"agent_id": "test_agent_00", "status": "completed", "output_size": 100},
            {"agent_id": "test_agent_01", "status": "completed", "output_size": 200},
            {"agent_id": "test_agent_02", "status": "pending", "output_size": 0}
        ]
        logs = []

        print_status(sample_mission, sample_plan, agent_results, logs)

        captured = capsys.readouterr()
        output = captured.out

        assert "2/3" in output  # 2 completed out of 3
        assert "67%" in output  # 67% completion
        assert "✅" in output  # Completed icon
        assert "⏳" in output  # Pending icon

    def test_print_progress_bar(self, capsys, sample_mission, sample_plan):
        """Test progress bar rendering"""
        agent_results = [
            {"agent_id": "test_agent_00", "status": "completed", "output_size": 100},
            {"agent_id": "test_agent_01", "status": "pending", "output_size": 0},
            {"agent_id": "test_agent_02", "status": "pending", "output_size": 0}
        ]
        logs = []

        print_status(sample_mission, sample_plan, agent_results, logs)

        captured = capsys.readouterr()
        output = captured.out

        # Should have progress bar
        assert "[" in output
        assert "]" in output
        assert "█" in output  # Filled part
        assert "░" in output  # Empty part

    def test_print_phase_breakdown(self, capsys, sample_mission, sample_plan):
        """Test phase-by-phase agent breakdown"""
        agent_results = [
            {"agent_id": "test_agent_00", "status": "completed", "output_size": 100},
            {"agent_id": "test_agent_01", "status": "completed", "output_size": 200},
            {"agent_id": "test_agent_02", "status": "pending", "output_size": 0}
        ]
        logs = []

        print_status(sample_mission, sample_plan, agent_results, logs)

        captured = capsys.readouterr()
        output = captured.out

        assert "Phase 1:" in output
        assert "Phase 2:" in output
        assert "🔬" in output  # Researcher emoji
        assert "🔍" in output  # Analyst emoji
        assert "🖊️" in output  # Writer emoji

    def test_print_recent_logs(self, capsys, sample_mission, sample_plan, sample_logs):
        """Test recent logs display (max 5)"""
        # agent_results must not be empty to avoid ZeroDivisionError
        agent_results = [
            {"agent_id": "test_agent_00", "status": "pending", "output_size": 0}
        ]

        print_status(sample_mission, sample_plan, agent_results, sample_logs)

        captured = capsys.readouterr()
        output = captured.out

        assert "최근 로그" in output
        assert "mission_created" in output
        assert "execution_started" in output

    def test_print_completion_message(self, capsys, sample_mission, sample_plan):
        """Test completion message when all done"""
        agent_results = [
            {"agent_id": "test_agent_00", "status": "completed", "output_size": 100},
            {"agent_id": "test_agent_01", "status": "completed", "output_size": 200},
            {"agent_id": "test_agent_02", "status": "completed", "output_size": 300}
        ]
        logs = []

        print_status(sample_mission, sample_plan, agent_results, logs)

        captured = capsys.readouterr()
        output = captured.out

        assert "모든 에이전트 완료" in output
        assert "결과 통합" in output
        assert "consolidate.py" in output

    def test_print_in_progress_message(self, capsys, sample_mission, sample_plan):
        """Test in-progress message when not all done"""
        agent_results = [
            {"agent_id": "test_agent_00", "status": "completed", "output_size": 100},
            {"agent_id": "test_agent_01", "status": "pending", "output_size": 0},
            {"agent_id": "test_agent_02", "status": "pending", "output_size": 0}
        ]
        logs = []

        print_status(sample_mission, sample_plan, agent_results, logs)

        captured = capsys.readouterr()
        output = captured.out

        assert "진행 중" in output
        assert "새로고침" in output
        assert "monitor.py" in output

    def test_none_plan_graceful_handling(self, capsys, sample_mission):
        """Test graceful handling when plan is None"""
        agent_results = []
        logs = []

        print_status(sample_mission, None, agent_results, logs)

        captured = capsys.readouterr()
        output = captured.out

        # Should still show mission info
        assert "test_mission_123" in output
        # But no agent progress
        assert "진행률" not in output


class TestIntegration:
    """Integration tests for monitor.py"""

    def test_full_monitoring_workflow(self, temp_workspace, sample_mission, sample_plan, sample_agent_outputs, sample_logs):
        """Test complete monitoring workflow"""
        # Setup mission directory
        mission_dir = Path(temp_workspace) / "avengers-missions" / "test_mission_123"
        mission_dir.mkdir(parents=True)
        outputs_dir = mission_dir / "outputs"
        outputs_dir.mkdir()
        logs_dir = mission_dir / "logs"
        logs_dir.mkdir()

        # Create mission file
        sample_mission["path"] = str(mission_dir)
        (mission_dir / "mission.json").write_text(json.dumps(sample_mission))
        (mission_dir / "execution_plan.json").write_text(json.dumps(sample_plan))

        # Create output files
        for agent_id, content in sample_agent_outputs.items():
            (outputs_dir / f"{agent_id}.md").write_text(content)

        # Create log file
        log_file = logs_dir / "execution.jsonl"
        with open(log_file, "w") as f:
            for entry in sample_logs:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Set environment variable and reload modules
        os.environ["AVENGERS_WORKSPACE"] = temp_workspace

        import importlib
        import config
        import utils
        import monitor
        importlib.reload(config)
        importlib.reload(utils)
        importlib.reload(monitor)

        # Load mission
        mission, plan = monitor.load_mission("test_mission_123")

        assert mission["id"] == "test_mission_123"
        assert plan["total_agents"] == 3

        # Check agent outputs
        agent_results = check_agent_outputs(mission_dir, plan)

        assert len(agent_results) == 3
        assert all(r["status"] == "completed" for r in agent_results)

        # Read logs
        logs = read_logs(mission_dir)

        assert len(logs) == 3
        assert logs[0]["event"] == "mission_created"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
