# 🦸 Agent Avengers 프로젝트 개선 로드맵

**팀:** agent-avengers-review  
**분석 일자:** 2026-02-07  
**참여 전문가:** architect, code-quality, test-engineer, documentation, devops

---

## 📊 현재 상태 요약

| 영역 | 상태 | 주요 문제 | 우선순위 |
|------|------|----------|----------|
| **아키텍처** | ⚠️ 주의 | 파일 기반 상태 분산, 실행 계층 외부 의존 | High |
| **코드 품질** | ⚠️ 주의 | 중복 코드 심각 (4개 파일), SOLID 위반 | High |
| **테스트** | ❌ 부족 | execute.py, monitor.py 미테스트 (~30% 커버리지) | High |
| **문서화** | ⚠️ 주의 | SKILL.md와 구현 불일치, API 문서 부재 | Medium |
| **DevOps** | ❌ 없음 | CI/CD, Docker, 패키징 미구현 | Medium |

---

## 🎯 핵심 발견 사항

### 1. 아키텍처 문제
- **파이프라인 패턴**은 적절하지만 **파일 I/O 중복**이 심각
- `load_mission()` 함수가 4개 파일에 중복 존재
- **실행 계층의 외부 의존**: execute.py가 실제 실행하지 않고 코드만 출력
- 상태가 4개 파일에 분산되어 일관성 문제

### 2. 코드 품질 문제
- **DRY 원칙 위반**: 동일한 유틸리티 함수 4중 중복
- **Type Hints** 부분적 사용
- **Test Coverage**: execute.py, monitor.py는 0%
- **의존성 주입** 없음: 테스트 어려움

### 3. 문서화 문제
- README에는 없는 기능(team_manager 등)이 실제로는 구현됨
- **문서-구현 불일치** 존재
- API 사용법 문서 부재

---

## 🚀 개선 로드맵

### Phase 1: 기반 다지기 (Week 1-2) - **즉시 시작**

#### 1.1 공통 모듈 추출 (P0)
**목표:** 중복 코드 제거, 유지보수성 향상

```
scripts/
├── __init__.py
├── config.py          # WORKSPACE, MISSION_DIR 등 상수
├── utils.py           # load_mission, update_mission_status, log_event
├── core.py            # Mission, Agent 데이터 클래스
├── models.py          # Pydantic 모델
├── assemble.py        # 리팩토링된 로직만
├── execute.py         # 리팩토링된 로직만
├── consolidate.py     # 리팩토링된 로직만
└── monitor.py         # 리팩토링된 로직만
```

**세부 작업:**
- [ ] `config.py` 생성: 모든 상수 중앙화
- [ ] `utils.py` 생성: 공통 함수 추출
- [ ] 4개 스크립트에서 중복 제거 및 import로 변경
- [ ] 기존 테스트가 통과하는지 확인

**예상 소요:** 4-6시간  
**영향도:** 전체 파일

#### 1.2 execute.py & monitor.py 테스트 작성 (P0)
**목표:** 테스트 커버리지 70% 이상 달성

**세부 작업:**
- [ ] `conftest.py` 생성: 공통 fixture 정의
- [ ] `test_execute.py` 작성: generate_openclaw_commands 테스트
- [ ] `test_monitor.py` 작성: check_agent_outputs, read_logs 테스트
- [ ] pytest-cov 설정

**예상 소요:** 1-2일  
**성공 기준:** 커버리지 70%+

#### 1.3 문서-구현 동기화 (P1)
**목표:** 문서와 실제 구현 일치

**세부 작업:**
- [ ] README 업데이트: Agent Teams 기능 반영
- [ ] API 사용법 문서 작성
- [ ] SKILL.md 검토 및 업데이트

**예상 소요:** 4시간

---

### Phase 2: 아키텍처 개선 (Week 3-4)

#### 2.1 중앙집중식 상태 관리 (P1)
**목표:** SQLite 기반 상태 관리로 일관성 확보

**현재:**
```python
# 4개 파일이 각각 JSON 파일 읽고 씀
with open(mission_path / "mission.json") as f:
    mission = json.load(f)
```

**개선 후:**
```python
from core import StateManager
state = StateManager(mission_id)
mission = state.get_mission()
state.update_status("running")
```

**세부 작업:**
- [ ] `StateManager` 클래스 설계
- [ ] SQLite 스키마 설계
- [ ] 기존 JSON 마이그레이션 경로 제공
- [ ] 트랜잭션 지원 구현

**예상 소요:** 2-3일  
**난이도:** Medium

#### 2.2 Type Hints 강화 (P1)
**목표:** 전체 코드베이스 타입 안전성 확보

**세부 작업:**
- [ ] `dict`, `list` → `dict[str, Any]`, `list[dict[str, Any]]`로 구체화
- [ ] `Optional`, `Union` 사용
- [ ] mypy 설정 및 검증

**예상 소요:** 1일

#### 2.3 예외 처리 개선 (P1)
**목표:** 견고한 에러 핸들링

**세부 작업:**
- [ ] 커스텀 예외 클래스 정의 (`AvengersException`)
- [ ] 구체적 예외 타입 처리 (`PermissionError`, `JSONDecodeError`)
- [ ] 에러 로깅 강화

**예상 소요:** 1일

---

### Phase 3: 고급 기능 (Week 5-6)

#### 3.1 재시도 및 회복 메커니즘 (P2)
**목표:** LLM API 실패 시 자동 복구

**세부 작업:**
- [ ] `@retry` 데코레이터 구현 (exponential backoff)
- [ ] Circuit breaker 패턴 구현
- [ ] 실패한 에이전트 자동 재시도

**예상 소요:** 2일

#### 3.2 모의 실행 (Dry-run) (P2)
**목표:** 실제 실행 전 계획 검증

**세부 작업:**
- [ ] `--dry-run` 플래그 구현
- [ ] 의존성 사이클 감지
- [ ] 예상 소요 시간 계산

**예상 소요:** 1일

#### 3.3 DevOps 기반 마련 (P2)
**목표:** 배포 및 운영 자동화

**세부 작업:**
- [ ] Dockerfile 작성
- [ ] GitHub Actions CI/CD 설정
- [ ] PyPI 패키징 (`setup.py` 또는 `pyproject.toml`)
- [ ] pre-commit hooks 설정 (black, isort, mypy)

**예상 소요:** 2일

---

## 📋 우선순위별 작업 목록

### P0 (즉시) - 기술 부채 해결
1. ✅ **공통 모듈 추출** (config.py, utils.py)
   - 중복 코드 제거
   - 예상: 4-6시간

2. ✅ **execute.py & monitor.py 테스트**
   - 커버리지 70% 목표
   - 예상: 1-2일

### P1 (단기) - 품질 개선
3. **중앙집중식 상태 관리** (SQLite)
   - 일관성 및 성능 향상
   - 예상: 2-3일

4. **Type Hints 강화**
   - mypy 적용
   - 예상: 1일

5. **예외 처리 개선**
   - 커스텀 예외, 에러 로깅
   - 예상: 1일

6. **문서화 개선**
   - README, API 문서
   - 예상: 4시간

### P2 (중기) - 고급 기능
7. **재시도 메커니즘**
   - 자동 복구
   - 예상: 2일

8. **Dry-run 모드**
   - 계획 검증
   - 예상: 1일

9. **DevOps 기반**
   - CI/CD, Docker, PyPI
   - 예상: 2일

---

## 🔧 구체적인 구현 가이드

### 공통 모듈 구조

```python
# scripts/config.py
import os
from pathlib import Path

WORKSPACE = Path(os.environ.get(
    "AVENGERS_WORKSPACE", 
    Path.home() / ".openclaw" / "workspace"
))
MISSION_DIR = WORKSPACE / "avengers-missions"

AGENT_TYPES = {
    "researcher": {"emoji": "🔬", "model": "sonnet", "timeout": 1800},
    # ...
}
```

```python
# scripts/utils.py
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any

def load_mission(mission_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """미션 및 실행 계획 로드."""
    mission_path = MISSION_DIR / mission_id
    
    with open(mission_path / "mission.json") as f:
        mission = json.load(f)
    
    with open(mission_path / "execution_plan.json") as f:
        plan = json.load(f)
    
    return mission, plan

def update_mission_status(
    mission_path: Path, 
    status: str, 
    updates: Dict[str, Any] = None
) -> None:
    """미션 상태 업데이트."""
    # 구현...
```

---

## ✅ 성공 기준 (Definition of Done)

### Phase 1 완료 기준
- [ ] `load_mission()` 함수가 4개 파일에서 제거되고 utils.py에서 import됨
- [ ] 테스트 커버리지 70% 이상
- [ ] 모든 테스트 통과
- [ ] 문서와 구현 일치

### Phase 2 완료 기준
- [ ] SQLite 기반 StateManager 동작
- [ ] mypy 오류 0개
- [ ] 커스텀 예외 처리 적용

### Phase 3 완료 기준
- [ ] 재시도 메커니즘 동작 확인
- [ ] `--dry-run` 플래그 동작
- [ ] CI/CD 파이프라인 동작
- [ ] PyPI 패키지 배포

---

## 🎉 예상 성과

### 개선 전
- 중복 코드: 4개 파일에 동일 함수 존재
- 테스트 커버리지: ~30%
- 상태 관리: 파일 기반 (경쟁 조건 위험)
- 문서-구현 불일치

### 개선 후
- 중복 코드: 0 (공통 모듈화)
- 테스트 커버리지: 80%+
- 상태 관리: SQLite (트랜잭션 지원)
- 문서-구현 일치
- PyPI 설치 지원: `pip install agent-avengers`

---

## 📝 결론

**즉시 시작할 작업:**
1. `scripts/utils.py` 생성하여 중복 함수 추출
2. `test_execute.py`, `test_monitor.py` 작성
3. README 업데이트

**장기적으로 고려할 작업:**
- SQLite 기반 상태 관리 (Phase 2)
- PyPI 패키징 (Phase 3)

**리스크:**
- 중앙집중식 상태 관리 전환 시 기존 데이터 마이그레이션 필요
- 하지만 기존 JSON 형식 유지하면서 단계적으로 전환 가능

---

**분석 완료** 🎉  
**다음 단계:** Phase 1 작업 시작 (공통 모듈 추출)
