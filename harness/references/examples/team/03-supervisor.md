# 예시 3: 코드 마이그레이션 팀 (Supervisor 패턴)

## 팀 아키텍처

감독자가 대상 파일 목록을 배치로 나누어 워커들에게 동적으로 할당한다. Codex CLI에서는 `tasks.md`가 공유 작업 목록 역할을 하며, 메인 에이전트가 배치 할당·재할당을 담당한다.

## 에이전트 구성

| 에이전트              | 유형      | sandbox_mode      | 역할                     |
| --------------------- | --------- | ----------------- | ------------------------ |
| @migration-supervisor | Architect | `read-only`       | 파일 분석·배치 분해      |
| @migrator-1~N         | Coder     | `workspace-write` | 할당된 배치 마이그레이션 |

## 오케스트레이터 워크플로우

```
Phase 0: (예시 1과 동일 — 상태 확인·Resume·신규 실행 분기)
Phase 1: ① @migration-supervisor 호출
           → 대상 파일 목록 수집 + 복잡도 추정 (파일 크기·import 수·의존성)
           → tasks.md에 N개 배치로 등록 (우선순위·복잡도 필드 포함; 순서는 오케스트레이터가 tasks.md 상태를 읽어 수동 제어)
         ② supervisor 완료 후 배치 수(N) 확정 → workflow.md 생성:
           Stage 1: code-migration / 사용자 승인 게이트: 없음
           Step 1: migrate / 패턴: supervisor / 활성 에이전트: [@migrator-1~N] / 다음 step: test
           Step 2: test / 패턴: pipeline / 활성 에이전트: [메인] / 다음 step: done
         ③ checkpoint.json 생성 (current_stage: "code-migration", current_step: "migrate",
                            active_pattern: "supervisor", status: "in_progress")
         findings.md [공유 변수/경로]·[데이터 충돌] 초기화
Phase 2: [Step 실행 루프 — Stage code-migration / Step migrate]
         메인 에이전트가 tasks.md를 읽어 가용 워커 수만큼 배치 할당
         - 단일 응답 턴에서 @migrator-1 / @migrator-2 / @migrator-3를
           병렬 배치 호출
         - 각 프롬프트에 할당 배치의 파일 목록·성공 기준 명시
         - 워커 완료 → 산출물 `cat`으로 확인
           - 성공 → tasks.md 상태 Todo→Done, 남은 배치 중 우선순위 최상을 즉시 재할당
           - 실패 → findings.md [데이터 충돌]에 원인 기록, 최대 2회 재시도 (총 3회)
           - 3회 후에도 실패 → Blocked 처리, 사용자 확인 요청으로 대체 경로 질의. 임의 Skip 절대 금지.
         모든 배치 Done → step "migrate" 종료 조건 충족
         checkpoint.json 갱신: current_step → "test", active_pattern → "pipeline"
                            step_history에 "migrate" completed_at 기록, last_updated: 현재 타임스탬프
Phase 3: [Step 실행 루프 — Stage code-migration / Step test]
         통합 테스트 실행 (셸)
         → 실패 시 영향 범위 분석 후 해당 배치만 재실행 (최대 2회 재시도(총 3회))
         → 3회 후에도 실패 → Blocked 처리, 사용자 확인 요청으로 수동 대응 요청. 임의 완료 처리 금지.
         step "test" 종료 조건 충족 → stage "code-migration" 완료
         checkpoint.json 갱신:
           - step_history에 "test" completed_at 기록
           - stage_history에 "code-migration" completed_at 기록
           - current_stage·current_step: "done", status: "completed", last_updated: 현재 타임스탬프
Phase 4: 마이그레이션 완료 보고서 _workspace/{plan_name}/final/migration_report.md 생성
Phase 5: 사용자 보고, _workspace/ 보존
```

**팬아웃과의 차이:** 작업이 사전 고정이 아니라 **런타임에 동적 할당**된다. `tasks.md`의 `[상태]` 필드가 claim 메커니즘을 대신한다.
