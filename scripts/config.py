#!/usr/bin/env python3
"""
Agent Avengers - Configuration
공통 설정 및 상수
"""

import os
from pathlib import Path
from typing import Any

# 워크스페이스 경로
WORKSPACE: str = os.environ.get("AVENGERS_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
MISSION_DIR: Path = Path(WORKSPACE) / "avengers-missions"

# 에이전트 타입 정의
AGENT_TYPES: dict[str, dict[str, Any]] = {
    "researcher": {
        "emoji": "🔬",
        "model": "sonnet",
        "timeout": 1800,
        "keywords": ["조사", "리서치", "검색", "수집", "분석"]
    },
    "analyst": {
        "emoji": "🔍",
        "model": "opus",
        "timeout": 1200,
        "keywords": ["분석", "패턴", "인사이트", "평가"]
    },
    "writer": {
        "emoji": "🖊️",
        "model": "sonnet",
        "timeout": 900,
        "keywords": ["작성", "문서", "리포트", "콘텐츠", "글"]
    },
    "coder": {
        "emoji": "💻",
        "model": "opus",
        "timeout": 2400,
        "keywords": ["코드", "개발", "구현", "API", "프로그래밍"]
    },
    "reviewer": {
        "emoji": "✅",
        "model": "opus",
        "timeout": 600,
        "keywords": ["검토", "리뷰", "피드백", "확인"]
    },
    "integrator": {
        "emoji": "🔧",
        "model": "sonnet",
        "timeout": 900,
        "keywords": ["통합", "병합", "조합", "최종"]
    }
}
