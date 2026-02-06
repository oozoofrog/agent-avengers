# 🦸 Agent Avengers 프로젝트 개선 로드맵

**팀:** agent-avengers-review  
**분석 일자:** 2026-02-07  
**참여 전문가:** architect, code-quality, test-engineer, documentation, devops

---

## 📊 현재 상태 요약

| 영역 | 상태 | 비고 | 우선순위 |
|------|------|------|----------|
| **아키텍처** | ✅ 개선됨 | 공통 모듈 추출 완료, 중복 제거 | - |
| **코드 품질** | ✅ 개선됨 | 타입 힌트 전체 적용, 커스텀 예외 도입 | - |
| **테스트** | ✅ 개선됨 | 27 → 60개 테스트, 전체 스크립트 커버 | - |
| **문서화** | ⚠️ 주의 | SKILL.md와 구현 불일치, API 문서 부재 | Medium |
| **DevOps** | ❌ 없음 | CI/CD, Docker, 패키징 미구현 | Medium |

---

## 🎯 핵심 발견 사항

### 1. ~~아키텍처 문제~~ → ✅ 해결됨 (2026-02-07)
- ~~`load_mission()` 함수가 4개 파일에 중복 존재~~ → `utils.py`로 통합
- ~~파일 I/O 중복이 심각~~ → `config.py`, `utils.py`로 공통 모듈 추출
- **실행 계층의 외부 의존**: execute.py가 실제 실행하지 않고 코드만 출력 (설계 의도)

### 2. ~~코드 품질 문제~~ → ✅ 해결됨 (2026-02-07)
- ~~**DRY 원칙 위반**: 동일한 유틸리티 함수 4중 중복~~ → 공통 모듈로 통합
- ~~**Type Hints** 부분적 사용~~ → 전체 함수에 구체적 타입 힌트 적용
- ~~**Test Coverage**: execute.py, monitor.py는 0%~~ → 60개 테스트 (전체 스크립트 커버)
- ~~**예외 처리** 부재~~ → `exceptions.py` 커스텀 예외 계층 도입

### 3. 문서화 문제 (미해결)
- README에는 없는 기능(team_manager 등)이 실제로는 구현됨
- **문서-구현 불일치** 존재
- API 사용법 문서 부재

---

## 🚀 개선 로드맵

### Phase 1: 기반 다지기 — ✅ 완료 (2026-02-07)

#### 1.1 공통 모듈 추출 (P0) — ✅ 완료
**결과:** 중복 코드 제거, 공통 모듈화 달성

```
scripts/
├── __init__.py        # 패키지 초기화
├── config.py          # WORKSPACE, MISSION_DIR, AGENT_TYPES 상수
├── utils.py           # load_mission, load_mission_only, update_mission_status, log_event
├── exceptions.py      # AvengersError, MissionNotFoundError, PlanNotFoundError, InvalidMissionError
├── assemble.py        # 태스크 분해 로직 (중복 제거됨)
├── execute.py         # 실행 명령어 생성 (중복 제거됨)
├── consolidate.py     # 결과 통합 (중복 제거됨)
└── monitor.py         # 모니터링 (중복 제거됨)
```

- [x] `config.py` 생성: 모든 상수 중앙화
- [x] `utils.py` 생성: 공통 함수 추출
- [x] `exceptions.py` 생성: 커스텀 예외 계층
- [x] 4개 스크립트에서 중복 제거 및 import로 변경
- [x] 기존 테스트 27개 통과 확인

#### 1.2 execute.py & monitor.py 테스트 작성 (P0) — ✅ 완료
**결과:** 테스트 27개 → 60개, 전체 스크립트 커버

- [x] `conftest.py` 생성: 공통 fixture 6개 정의
- [x] `test_execute.py` 작성: 12개 테스트 (generate_openclaw_commands, save_execution_script, load_mission 에러 등)
- [x] `test_monitor.py` 작성: 21개 테스트 (check_agent_outputs, read_logs, print_status 등)

#### 1.3 타입 힌트 및 예외 처리 (Phase 2에서 앞당겨 완료) — ✅ 완료
- [x] 전체 함수에 구체적 타입 힌트 적용 (`dict[str, Any]`, `Optional`, `tuple` 등)
- [x] 커스텀 예외 클래스 도입 (`AvengersError` 계층)
- [x] `FileNotFoundError` → `MissionNotFoundError`/`PlanNotFoundError` 래핑
- [x] `json.JSONDecodeError` → `InvalidMissionError` 래핑

#### 1.4 문서-구현 동기화 (P1) — 미완료
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
# utils.py에서 공통 함수로 JSON 파일 읽고 씀
from utils import load_mission
mission, plan = load_mission(mission_id)
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

#### ~~2.2 Type Hints 강화 (P1)~~ → ✅ Phase 1에서 완료
#### ~~2.3 예외 처리 개선 (P1)~~ → ✅ Phase 1에서 완료

#### 2.2 mypy 정적 분석 도입 (P1)
**목표:** 타입 검증 자동화

**세부 작업:**
- [ ] mypy 설정 (`mypy.ini` 또는 `pyproject.toml`)
- [ ] mypy 오류 0개 달성
- [ ] CI에 mypy 검증 추가

**예상 소요:** 반나절

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

### P0 (즉시) - 기술 부채 해결 — ✅ 모두 완료
1. ✅ **공통 모듈 추출** (config.py, utils.py, exceptions.py)
2. ✅ **execute.py & monitor.py 테스트** (33개 신규, 총 60개)
3. ✅ **타입 힌트 전체 적용** (dict[str, Any] 등 구체화)
4. ✅ **커스텀 예외 처리** (AvengersError 계층)

### P1 (단기) - 품질 개선
5. **문서화 개선**
   - README, API 문서, SKILL.md 동기화
   - 예상: 4시간

6. **중앙집중식 상태 관리** (SQLite)
   - 일관성 및 성능 향상
   - 예상: 2-3일

7. **mypy 정적 분석 도입**
   - 타입 검증 자동화
   - 예상: 반나절

### P2 (중기) - 고급 기능
8. **재시도 메커니즘**
   - 자동 복구
   - 예상: 2일

9. **Dry-run 모드**
   - 계획 검증
   - 예상: 1일

10. **DevOps 기반**
    - CI/CD, Docker, PyPI
    - 예상: 2일

---

## ✅ 성공 기준 (Definition of Done)

### Phase 1 완료 기준 — ✅ 달성
- [x] `load_mission()` 함수가 4개 파일에서 제거되고 utils.py에서 import됨
- [x] 테스트 60개 전체 통과 (27 → 60)
- [x] 전체 함수에 타입 힌트 적용
- [x] 커스텀 예외 처리 적용
- [ ] 문서와 구현 일치 (미완료)

### Phase 2 완료 기준
- [ ] SQLite 기반 StateManager 동작
- [ ] mypy 오류 0개

### Phase 3 완료 기준
- [ ] 재시도 메커니즘 동작 확인
- [ ] `--dry-run` 플래그 동작
- [ ] CI/CD 파이프라인 동작
- [ ] PyPI 패키지 배포

---

## 🎉 Phase 1 성과 (2026-02-07 완료)

| 항목 | Before | After |
|------|--------|-------|
| 중복 코드 | 4개 파일에 동일 함수 | **0** (공통 모듈화) |
| 테스트 수 | 27개 | **60개** (+122%) |
| 타입 힌트 | 부분적 | **전체 함수 적용** |
| 예외 처리 | bare FileNotFoundError | **커스텀 예외 계층** |
| 공통 모듈 | 없음 | **config.py, utils.py, exceptions.py** |

---

## 📝 다음 단계

**즉시 가능한 작업:**
1. 문서-구현 동기화 (README, SKILL.md)

**단기 과제:**
- SQLite 기반 상태 관리 (Phase 2)
- mypy 정적 분석 도입

**장기 과제:**
- 재시도 메커니즘, Dry-run 모드 (Phase 3)
- CI/CD, Docker, PyPI 패키징 (Phase 3)

**리스크:**
- 중앙집중식 상태 관리 전환 시 기존 데이터 마이그레이션 필요
- 하지만 기존 JSON 형식 유지하면서 단계적으로 전환 가능

---

**Phase 1 완료** 🎉 (2026-02-07)
**다음 단계:** 문서화 개선 또는 Phase 2 진행
