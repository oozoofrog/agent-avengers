#!/usr/bin/env python3
"""
Agent Avengers - Utilities
공통 유틸리티 함수
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    from config import MISSION_DIR
    from exceptions import MissionNotFoundError, PlanNotFoundError, InvalidMissionError
except ImportError:
    from .config import MISSION_DIR
    from .exceptions import MissionNotFoundError, PlanNotFoundError, InvalidMissionError


def load_mission(mission_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    미션 및 실행 계획 로드

    Args:
        mission_id: 미션 ID

    Returns:
        (mission, plan) 튜플

    Note:
        plan 파일이 없으면 예외 발생 (execute.py, consolidate.py용)
    """
    mission_path = MISSION_DIR / mission_id

    try:
        with open(mission_path / "mission.json") as f:
            mission = json.load(f)
    except FileNotFoundError:
        raise MissionNotFoundError(f"미션을 찾을 수 없습니다: {mission_id}")
    except json.JSONDecodeError as e:
        raise InvalidMissionError(f"미션 파일이 유효하지 않습니다: {e}")

    try:
        with open(mission_path / "execution_plan.json") as f:
            plan = json.load(f)
    except FileNotFoundError:
        raise PlanNotFoundError(f"실행 계획을 찾을 수 없습니다: {mission_id}")
    except json.JSONDecodeError as e:
        raise InvalidMissionError(f"실행 계획 파일이 유효하지 않습니다: {e}")

    return mission, plan


def load_mission_only(mission_id: str) -> tuple[dict[str, Any], Optional[dict[str, Any]]]:
    """
    미션 로드 (plan은 Optional)

    Args:
        mission_id: 미션 ID

    Returns:
        (mission, plan) 튜플 (plan은 None일 수 있음)

    Note:
        monitor.py용 - plan 파일이 없어도 동작
    """
    mission_path = MISSION_DIR / mission_id

    try:
        with open(mission_path / "mission.json") as f:
            mission = json.load(f)
    except FileNotFoundError:
        raise MissionNotFoundError(f"미션을 찾을 수 없습니다: {mission_id}")
    except json.JSONDecodeError as e:
        raise InvalidMissionError(f"미션 파일이 유효하지 않습니다: {e}")

    plan_file = mission_path / "execution_plan.json"
    plan: Optional[dict[str, Any]] = None
    if plan_file.exists():
        try:
            with open(plan_file) as f:
                plan = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidMissionError(f"실행 계획 파일이 유효하지 않습니다: {e}")

    return mission, plan


def update_mission_status(mission_path: Path, status: str, updates: Optional[dict[str, Any]] = None) -> None:
    """
    미션 상태 업데이트

    Args:
        mission_path: 미션 디렉토리 경로
        status: 새로운 상태
        updates: 추가로 업데이트할 필드들
    """
    try:
        with open(mission_path / "mission.json") as f:
            mission = json.load(f)
    except FileNotFoundError:
        raise MissionNotFoundError(f"미션을 찾을 수 없습니다: {mission_path}")
    except json.JSONDecodeError as e:
        raise InvalidMissionError(f"미션 파일이 유효하지 않습니다: {e}")

    mission["status"] = status
    mission["updated_at"] = datetime.now().isoformat()

    if updates:
        mission.update(updates)

    with open(mission_path / "mission.json", "w") as f:
        json.dump(mission, f, indent=2, ensure_ascii=False)


def log_event(mission_path: Path, event: str, data: Optional[dict[str, Any]] = None) -> None:
    """
    이벤트 로깅

    Args:
        mission_path: 미션 디렉토리 경로
        event: 이벤트 이름
        data: 이벤트 데이터
    """
    log_file = mission_path / "logs" / "execution.jsonl"

    entry: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "data": data or {}
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
