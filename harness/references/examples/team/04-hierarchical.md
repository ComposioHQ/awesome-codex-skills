# 예시 4: 풀스택 앱 개발 (Hierarchical Delegation 패턴)

## 팀 아키텍처

최상위 아키텍트가 프로젝트를 프론트엔드·백엔드 서브 프로젝트로 분해하고, 각 팀 리드가 다시 자신의 서브에이전트를 조율한다.

## 계층 구조

```
@project-architect (Top)
  ├── @frontend-team-lead (Mid) — UI/UX, 컴포넌트, 상태 관리
  │     ├── @ui-designer
  │     └── @state-engineer
  └── @backend-team-lead (Mid) — API, DB, 인프라
        ├── @api-designer
        └── @db-engineer
```

## 에이전트 파일 전문 예시: `.codex/agents/frontend-team-lead.toml`

```toml
name = "frontend-team-lead"
description = "프론트엔드 아키텍처 및 구현 전문가. UI 컴포넌트 설계와 상태 관리를 전담. 프론트엔드 구조 설계·구현·리팩토링 요청 시 반드시 이 에이전트를 선택."
model = "gpt-5.3-codex"
sandbox_mode = "workspace-write"
model_reasoning_effort = "high"

developer_instructions = """

# Frontend Team Lead

## 핵심 역할

1. 아키텍트의 설계를 기반으로 UI 명세서 작성
2. React/Next.js 컴포넌트 구조 설계 및 구현
3. 프론트엔드 테스트 코드 작성
4. @ui-designer·@state-engineer의 산출물을 통합하는 중간 조율

## 협업 프로토콜 (Codex CLI)

- 상위: @project-architect가 findings.md에 기록한 요구사항을 입력으로 받는다.
- 하위: @ui-designer·@state-engineer에게 **직접 지시할 수 없다**.
  필요한 하위 작업은 `task_frontend-team-lead_{id}.json`에 기록하고, 메인 에이전트가 수집·통합 후 해당 에이전트들을 호출하도록 한다.
- 산출물은 `_workspace/frontend/` 하위에 정리하며,
  @backend-team-lead와의 API 계약은 findings.md [공유 변수/경로]에 기록한다.

## 에러 핸들링

- 아키텍트 명세 불명확 시 사용자 확인 요청으로 요구사항 재확인. 임의 해석 금지.
- 하위 에이전트(@ui-designer·@state-engineer) 산출물 검수 실패 시 task*{agent}*{id}.json에 재작업 지시 기록 후 메인 에이전트에 위임.
- 3회 재작업 후에도 기준 미달 → findings.md [데이터 충돌]에 미달 내용 기록, Blocked 판정. 메인 에이전트가 사용자 확인 요청.
"""
```

## 오케스트레이터 워크플로우

```
Phase 0: (예시 1과 동일 — 상태 확인·Resume·신규 실행 분기)
Phase 1: findings.md 초기화: [공유 변수/경로]·[변경 요청]·[데이터 충돌] 섹션 생성
         ① @project-architect 호출 → 전체 설계 _workspace/{plan_name}/00_architecture.md
           → findings.md [공유 변수/경로]에 프론트/백엔드 API 계약 요약
         ② architect 완료 후 설계 결과 기반으로 workflow.md 생성:
           Stage 1: feature-development / 사용자 승인 게이트: 없음
           Step 1: design / 패턴: hierarchical / 활성 에이전트: [@frontend-team-lead, @backend-team-lead] / 다음 step: implement
           Step 2: implement / 패턴: hierarchical / 활성 에이전트: [@ui-designer, @state-engineer, @api-designer, @db-engineer] / 다음 step: done
         ③ checkpoint.json 생성 (current_stage: "feature-development", current_step: "design",
                            active_pattern: "hierarchical", status: "in_progress")
         tasks.md 초기화
Phase 2: [Step 실행 루프 — Stage feature-development / Step design]
         @frontend-team-lead / @backend-team-lead를
         병렬 배치 호출
         - 각 호출 프롬프트에 findings.md [공유 변수/경로]의 프론트/백엔드 API 계약 요약 주입
         → 각자 자기 영역 설계 완료 + 필요한 하위 작업을 task_{agent}_{id}.json에 기록
         → 메인 에이전트가 두 파일 수집 후 tasks.md에 원자적 통합 (동시 쓰기 충돌 방지)
         Step "design" 종료 조건 충족
         checkpoint.json 갱신: current_step → "implement", active_pattern → "hierarchical" (유지)
                            step_history에 "design" completed_at 기록, last_updated: 현재 타임스탬프
Phase 3: [Step 실행 루프 — Stage feature-development / Step implement]
         메인 에이전트가 tasks.md를 읽어 @ui-designer·@state-engineer·
         @api-designer·@db-engineer를 subagent spawn으로 순차/병렬 호출
         (의존관계 없는 작업은 병렬, 의존관계 있으면 순차)
         → 산출물은 각 팀 리드가 통합 검수
         → 검수 실패 시 해당 에이전트 재호출 (최대 2회 재시도(총 3회))
         → 3회 후에도 실패 → Blocked, 사용자 확인 요청으로 수동 개입 요청
         종료 조건: tasks.md의 모든 항목 상태 = Done + 각 팀 리드 검수 통과 → Step "implement" 충족
         → stage "feature-development" 완료 (Phase 4 교차 검증 후 최종 확정)
Phase 4: @project-architect가 최종 산출물을 교차 검증
         - 검증 통과 → checkpoint.json 갱신:
           step_history에 "implement" completed_at, stage_history에 "feature-development" completed_at
           current_stage·current_step: "done", status: "completed", last_updated: 현재 타임스탬프
         - 검증 실패 → 실패 영역(프론트/백엔드)을 findings.md [변경 요청]에 기록 후 해당 팀 리드 재호출, 최대 2회 재시도(총 3회)
         - 재검증 후에도 실패 → Blocked, 사용자 확인 요청으로 수동 판단 요청
Phase 5: 사용자 보고, _workspace/ 보존
```

계층적 위임에서는 **중간 리드가 직접 하위 호출을 하지 않는다**. 모든 호출은 메인 에이전트가 tasks.md를 통해 트리거한다.

**Supervisor와의 차이:** 단일 계층(감독자→동종 워커)이 아닌 2단계 계층(아키텍트→팀 리드→전문 워커)으로, 도메인이 이질적인 팀에 적합.
