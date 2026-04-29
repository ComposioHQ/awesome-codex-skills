# 예시 5: 시스템 디버깅 및 장애 대응 팀 (Handoff + Persistence 패턴)

## 팀 아키텍처

문제를 분류하는 트리아지 에이전트가 로그를 분석하고, 분석 결과에 따라 가장 적합한 수정 전문가에게 직접 제어권을 넘긴다(Handoff). 대규모 로그 분석 중 중단될 경우에 대비해 체크포인트를 관리한다(Persistence).

## 에이전트 구성

| 에이전트          | 유형    | 핵심 역할                       | sandbox_mode      |
| ----------------- | ------- | ------------------------------- | ----------------- |
| @incident-triage  | Analyst | 원인 분석 및 전문가 추천        | `read-only`       |
| @db-fixer         | Coder   | DB 쿼리 및 스키마 수정          | `workspace-write` |
| @logic-fixer      | Coder   | 애플리케이션 비즈니스 로직 수정 | `workspace-write` |
| @security-patcher | Coder   | 취약점 패치 및 보안 설정        | `workspace-write` |

## 오케스트레이터 워크플로우

```
Phase 0: _workspace/ + checkpoint.json 존재 여부 확인 → 실행 모드 결정:
         - checkpoint.json 존재 + status: "in_progress" → findings.md의 [공유 변수/경로]에서
           "마지막 분석 로그 라인" 확인 후 그 지점부터 재개 (Persistence)
           workflow.md 읽기 → current_stage, current_step 복원
         - checkpoint.json 존재 + status: "completed" → 이전 분석 완료 상태.
           사용자 요청이 부분 수정이면 부분 재실행, 새 장애면 새 실행으로 분기. Resume 금지.
         - _workspace/ 미존재 또는 checkpoint.json 미존재 → 신규 분석 시작 (Phase 1로 진행)
Phase 1: workflow.md 생성:
           Stage 1: incident-resolution / 사용자 승인 게이트: 없음
           Step 1: triage / 패턴: handoff / 활성 에이전트: [@incident-triage] / 다음 step: fix
           Step 2: fix / 패턴: producer_reviewer / 활성 에이전트: [동적 결정] / 다음 step: done
         checkpoint.json 생성 (current_stage: "incident-resolution", current_step: "triage",
                            active_pattern: "handoff", status: "in_progress")
         tasks.md 초기화 (fix 작업 등록용)
         findings.md [공유 변수/경로]·[데이터 충돌] 초기화
Phase 2: [Step 실행 루프 — Stage incident-resolution / Step triage]
         @incident-triage 호출 → 수 기가바이트의 로그 및 스택 트레이스 스캔
         - 분석 결과: "DB 연결 타임아웃 발견"
         - 응답 끝에 핸드오프 신호 삽입:
           `[NEXT_AGENT: @db-fixer] 사유: Connection Pool 고갈 및 Slow Query 확인됨.`
         오케스트레이터가 [NEXT_AGENT] 파싱:
         - 파싱 성공 → handle_handoff(@db-fixer) 호출:
                        - checkpoint.json의 handoff_chain 확인 (현재: [])
                        - 순환 없음 + 3단계 미초과 → handoff_chain: ["@db-fixer"] 갱신
                        - current_step → "fix", active_pattern → "producer_reviewer" 갱신
                        - step_history에 "triage" completed_at 기록, last_updated: 현재 타임스탬프
                        - @db-fixer 즉시 호출. 프롬프트에 트리아지 분석 요약 + 로그 위치 주입
         - 파싱 실패 ([NEXT_AGENT] 미포함) → 사용자 확인 요청으로 전문가 선택 요청
         - 순환/3단계 초과 → handle_handoff()가 사용자 확인 요청 + HALT (참조: orchestrator-procedures.md)
Phase 3: [Step 실행 루프 — Stage incident-resolution / Step fix]
         지정 에이전트(@db-fixer 등)가 수정 수행 후 @incident-triage에게 재검증 요청 (Fix Loop, 최대 2회 재시도(총 3회))
         - 종료 조건(성공): @incident-triage 응답에 [NEXT_AGENT] 없음 + "이상 없음" 또는 "수정 확인" 명시
         - 종료 조건(실패): 3회 후에도 [NEXT_AGENT] 재반환 또는 에러 지속
           → Blocked, 사용자 확인 요청으로 수동 개입 요청. 임의 PASS 절대 금지.
         step "fix" 종료 조건 충족 → stage "incident-resolution" 완료
         checkpoint.json 갱신:
           - step_history에 "fix" completed_at 기록
           - stage_history에 "incident-resolution" completed_at 기록
           - current_stage·current_step: "done", status: "completed", last_updated: 현재 타임스탬프
           - handoff_chain: [] (Step 전환 시 초기화)
Phase 4: 장애 대응 보고서 _workspace/{plan_name}/final/incident_report.md 생성
Phase 5: 사용자 보고, _workspace/ 보존
```

## 협업 프로토콜 예시: `@incident-triage.md`

```markdown
## 핸드오프 가이드 (Codex CLI)

작업 완료 시 다음 규칙에 따라 전문가를 추천하라.

- SQL/DB 에러·커넥션 타임아웃·슬로우 쿼리 발견 시: `[NEXT_AGENT: @db-fixer]`
- 403/401/인증·권한 에러 발견 시: `[NEXT_AGENT: @security-patcher]`
- 성능 이슈(DB 외 애플리케이션 레벨 병목): `[NEXT_AGENT: @logic-fixer]`
- 그 외 비즈니스 로직 오류: `[NEXT_AGENT: @logic-fixer]`
- 복수 원인 동시 발견 시: 가장 심각한 원인 기준으로 1개 선택 후 사유에 나머지 원인 병기

## 영속성 가이드

로그 분석 중 컨텍스트 한도에 도달할 경우, 현재까지 읽은 마지막 파일 경로와 라인 번호를
`_workspace/findings.md`의 [공유 변수/경로] 섹션에 기록하여 다음 턴에서 이어서 읽을 수 있게 하라.

## 에러 핸들링

- 로그 파일 접근 불가(권한·경로 오류) → 사용자 확인 요청으로 올바른 경로 요청. 임의 경로 추측 금지.
- 원인 특정 불가(에러 패턴 없음) → 분석 불가 사유를 findings.md [데이터 충돌]에 기록 후 사용자 확인 요청으로 추가 컨텍스트 요청.
- 재검증 시 동일 에러 반복(Fix Loop 3회 초과) → 재반환 없이 Blocked 판정. 메인 에이전트가 사용자 확인 요청 호출.
```
