# Full Bundle Example: SSO 개발 하네스 (전체 산출물 패키지)

기존 `examples/step/01~05`는 workflow.md 스니펫만 보여준다. 이 파일은 한 도메인 하네스의 **전체 산출물**(오케스트레이터 SKILL.md + 에이전트 N개 + workflow.md + findings.md 초기화 + checkpoint.json 초기화)을 **통합 패키지**로 시연한다. examples/sso-dev-flow처럼 평면 Step 나열로 도피하는 drift를 막기 위한 정본 예시.

> **사용처:** 새 하네스 구축 시 이 패키지를 참고하여 모든 산출물을 동시에 작성. 하나라도 누락 시 Zero-Tolerance Failure.

---

## 1. 도메인 분해

- **목표:** SSO 인증 기능 구현
- **작업(Stage) 분해:**
  - Stage 1: `research-plan` (요구사항 분석 + 설계, 작업 게이트 1회)
  - Stage 2: `develop-review` (구현 + QA 루프, 마지막 stage)
- **Step(하위 이슈) 분해:**
  - research-plan/research = pipeline (분석가 단독)
  - research-plan/plan = pipeline (설계가 단독)
  - develop-review/loop = producer_reviewer (개발자 ↔ QA)

---

## 2. 오케스트레이터 SKILL.md (`.codex/skills/sso-dev-flow/SKILL.md`)

```markdown
---
name: sso-dev-flow
description: SSO 인증 기능 구현 하네스. workflow.md 기반 Stage-Step 조율, findings.md·tasks.md·checkpoint.json 영속화. "SSO 구현해줘", "SAML 추가해줘", "로그인 흐름 개선" 트리거. 후속 작업("SSO 결과 수정", "재실행", "보완", "이전 결과 개선") 시에도 반드시 이 스킬 사용.
---

# Skill: SSO Dev Flow Orchestrator

## 가상 팀

| agent           | 타입   | 역할               | 출력                            |
| --------------- | ------ | ------------------ | ------------------------------- |
| @sso-researcher | 커스텀 | 요구사항·코드 분석 | \_workspace/sso/research.md     |
| @sso-planner    | 커스텀 | 아키텍처 설계      | \_workspace/sso/plan.md         |
| @go-developer   | 커스텀 | Go 코드 구현       | src/auth/\*.go                  |
| @qa-reviewer    | 커스텀 | 보안·정합성 검증   | \_workspace/sso/qa_verdict.json |

## 워크플로우

### Step 0: 컨텍스트 확인 (Durable Execution)

표준 절차 적용 — `references/orchestrator-template.md` Step 0 참조. checkpoint.json status별 분기.

### Step 1: 초기화

1. `_workspace/sso/`, `_workspace/tasks/` 디렉터리 생성.
2. workflow.md 작성 (§3 참조).
3. findings.md 초기화 (§4 참조).
4. tasks.md 초기화 (§5 참조).
5. checkpoint.json 생성 (§6 참조).
6. **workflow.md 스키마 검증** — 6 필수 필드 + 검증 가능 종료 조건 + 패턴 enum.
7. workflow.md 사이클 검증.

### Step 2: Step 실행 루프

표준 절차 — `references/orchestrator-template.md` Step 2 참조. 패턴별 호출, 종료 조건 검사, 자동/승인 전환.

### Step 3: producer_reviewer 루프 (develop-review/loop 전용)

1. @go-developer 호출 (구현).
2. @qa-reviewer 호출 (검증) → qa_verdict.json.
3. verdict=PASS → step done.
4. verdict=REJECT → findings.md `[변경 요청]` 갱신 → @go-developer 재호출.
5. iterations=3 도달 시 `Blocked` + 사용자 확인 요청.

## 에러 핸들링

Zero-Tolerance: 에이전트 실패 → 최대 2회 재시도 → 미해결 시 `task_*.json` status=blocked + 사용자 확인 요청. 임의 Skip 금지.
```

---

## 3. workflow.md (`_workspace/workflow.md`)

```markdown
<!-- 참고 패턴: research-plan=pipeline, develop-review=producer_reviewer -->
<!-- Stage = 상위 이슈(Jira Issue). Step = 하위 이슈(Jira Sub-issue). -->

## Stage 정의

### Stage 1: research-plan

- 종료 조건: 모든 step 완료
- 다음 stage: develop-review
- 사용자 승인 게이트: 필요

#### Step 1: research

- 패턴: pipeline
- 활성 에이전트: [@sso-researcher]
- 종료 조건: `_workspace/sso/research.md` 존재
- 다음 step: plan
- 최대 반복 횟수: 1

#### Step 2: plan

- 패턴: pipeline
- 활성 에이전트: [@sso-planner]
- 종료 조건: `_workspace/sso/plan.md` 존재 + `_workspace/sso/tasks_decomposed.json`의 task_count ≥ 1
- 다음 step: done
- 최대 반복 횟수: 1

### Stage 2: develop-review

- 종료 조건: 모든 step 완료
- 다음 stage: done
- 사용자 승인 게이트: 없음 (마지막 stage)

#### Step 1: loop

- 패턴: producer_reviewer
- 활성 에이전트: [@go-developer, @qa-reviewer]
- 종료 조건: `_workspace/sso/qa_verdict.json`의 verdict=PASS
- 다음 step: done
- 최대 반복 횟수: 3
```

**스키마 검증 통과 포인트:**

- 6 필수 필드 모두 존재
- 종료 조건 모두 검증 가능 술어 (파일 존재 / JSON 필드값)
- 자연어 표현(`승인`·`충분`·`완료되면`) 0건
- 패턴 enum 위반 없음

---

## 4. findings.md 초기화 (`_workspace/findings.md`)

```markdown
# Findings: SSO Dev Flow

## [공유 변수/경로]

- 작업 디렉터리: `_workspace/sso/`
- 산출물: research.md, plan.md, tasks_decomposed.json, qa_verdict.json

## [다음 단계 지침]

(Stage 1 종료 시 메인이 작성)

## [변경 요청]

(Stage 2 producer_reviewer REJECT 시 메인이 작성)
```

---

## 5. tasks.md 초기화 (`_workspace/tasks.md`)

```markdown
| ID  | 에이전트        | 작업 내용            | 상태 | Evidence | 산출물 경로                     |
| --- | --------------- | -------------------- | ---- | -------- | ------------------------------- |
| 1   | @sso-researcher | 요구사항·코드 분석   | Todo | -        | \_workspace/sso/research.md     |
| 2   | @sso-planner    | 아키텍처·태스크 분해 | Todo | -        | \_workspace/sso/plan.md         |
| 3   | @go-developer   | Go 코드 구현         | Todo | -        | src/auth/\*.go                  |
| 4   | @qa-reviewer    | 보안·정합성 검증     | Todo | -        | \_workspace/sso/qa_verdict.json |
```

---

## 6. checkpoint.json 초기화 (`_workspace/checkpoint.json`)

```json
{
  "execution_id": "20260427_140000",
  "plan_name": "sso",
  "status": "in_progress",
  "current_stage": "research-plan",
  "current_step": "research",
  "active_pattern": "pipeline",
  "stage_history": [],
  "step_history": [],
  "stage_artifacts": {},
  "handoff_chain": [],
  "tasks_snapshot": { "done": [], "current": null },
  "shared_variables": {},
  "last_updated": "20260427_140000"
}
```

---

## 7. examples/sso-dev-flow와의 비교

| 항목                  | examples/skills/sso-dev-flow (drift) | full-bundle/sso-style (정본)             |
| --------------------- | ------------------------------------ | ---------------------------------------- |
| Stage 계층            | **없음** (평면 Step 0~4)             | 2 Stage 명시                             |
| 종료 조건             | "QA 승인 시" (자연어)                | `qa_verdict.json`의 verdict=PASS         |
| 패턴 명시             | Producer-Reviewer만 한 줄            | 각 Step 블록에 enum 값                   |
| 사용자 승인 게이트    | 없음                                 | Stage 1 후 명시                          |
| 최대 반복 횟수        | "최대 3회" 본문 한 줄                | 각 Step 필드                             |
| findings.md 표준 섹션 | `[Review: 단계]` 임의 형식           | `[공유 변수/경로]`·`[변경 요청]` 등 표준 |
| task\_\*.json 영속    | 미사용                               | `_workspace/tasks/task_*.json` 표준      |

---

## 핵심 학습 포인트

1. **하나의 산출물만 작성하지 말 것** — 오케스트레이터 SKILL.md + workflow.md + findings.md + tasks.md + checkpoint.json 5종 동시 작성.
2. **workflow.md 스키마 6 필드 강제** — 누락 시 Zero-Tolerance.
3. **종료 조건 = 검증 가능 술어** — 자연어 통과 절대 금지.
4. **표준 findings.md 섹션 사용** — 임의 섹션명 금지.
5. **Stage·Step 분리 명시** — 평면 Step 1~N 나열 drift 금지.
