# Stage-Step 워크플로우 테스트 시나리오

`stage-step-guide.md` 기반 하네스 검증용 시나리오 6종. 3단계 계층(Stage → Step → Agent) 기준.

## 시나리오 인덱스

| # | 목적 | 핵심 검증 포인트 | 판정 기준 |
|---|------|----------------|----------|
| 1 | 단순 workflow.md 구조 검증 | Stage 1개 + Step 1개 생성 여부 | Stage 2 블록 없음 + `main/main` 구조 |
| 2 | 다단계 워크플로우 트리거 | 발화에서 다단계 자동 선택 | Stage 블록 2개 이상 존재 |
| 3 | Step 종료 조건 미충족 → 전환 차단 | 미완료 task 있을 때 다음 Step 진입 금지 | Stage 2 에이전트 subagent spawn 미발생 |
| 4 | Step 자동 전환 (승인 불필요) | 종료 조건 충족 시 사용자 개입 없이 전환 | 승인 요청 없이 다음 Step 에이전트 호출 |
| 5 | Stage 전환 게이트 (승인 필수) | Stage 완료 시 승인 게이트 발동 | 승인 요청 발생 + 다음 Stage 에이전트 미호출 |
| 6 | Step별 에이전트 출입 통제 | 현재 Step 목록 외 에이전트 호출 차단 | 비활성 에이전트 subagent spawn 미발생 |

---

## 시나리오 1: 단순 워크플로우 workflow.md 구조 검증

**목적:** 단순 작업 발화 시 `workflow.md`가 Stage 1개 + Step 1개 구조로 생성되며 **deliverable 명사구 명명 규칙**(Jira 제목 컨벤션)을 따르는지 확인. `main`·`step1` 같은 placeholder는 위반.

**테스트 프롬프트:** `"블로그 포스트를 3명이 병렬로 리서치하고 통합해줘"`

**기대 동작:**
- `_workspace/workflow.md` 생성 — Stage 1개(deliverable 명사구, 예: `blog-post`), Step 1개(deliverable 명사구, 예: `parallel-research`), 패턴 = fan_out_fan_in, 활성 에이전트 목록 포함.
- Stage 2 블록 없음.

**판정:**
- `_workspace/workflow.md` 존재 → ✓
- `### Stage 1: {kebab-name}` 블록 존재 + 이름이 `^[a-z][a-z0-9-]*$` 일치 + placeholder(`main`·`step1`·`task`·`default`) 아님 → ✓
- `#### Step 1: {kebab-name}` 블록 존재 + 위와 동일 규칙 + 활성 에이전트 목록 → ✓
- Stage 2 블록 없음 → ✓
- 넷 다 충족 시 PASS. placeholder 사용 시 FAIL.

---

## 시나리오 2: 다단계 워크플로우 트리거 테스트

**목적:** "병렬 수집 후 검토 루프" 발화에서 다단계 워크플로우가 자동 선택되고 Stage-Step 구조가 올바르게 생성되는지 확인.

**테스트 프롬프트:** `"3명이 병렬로 리서치한 뒤, 작가와 편집자가 루프로 다듬어줘"`

**기대 동작:**
- 메인이 `stage-step-guide.md` 로드.
- `_workspace/workflow.md` 생성 — Stage 2개 이상, 각 Stage에 Step 블록 포함.
- Stage 1 / Step 1 패턴: fan_out_fan_in, Stage 2 / Step 1 패턴: producer_reviewer.
- 사용자에게 워크플로우 확인 요청.

**판정:** `_workspace/workflow.md` 내 Stage 블록 2개 이상 + 각 Stage 내 Step 블록 (`#### Step`) 존재 시 PASS.

---

## 시나리오 3: Step 종료 조건 미충족 → 자동 전환 차단 테스트

**목적:** Step 종료 조건 미충족 시 다음 Step로 넘어가지 않는지 확인.

**설정:**
- `workflow.md` Stage 1(gather) / Step 1(research): 종료 조건 = `task_a.json`, `task_b.json` 모두 status=done
- `task_a.json`: status=done, `task_b.json`: status=in_progress (미완료)
- `checkpoint.json`: `current_stage: "gather"`, `current_step: "research"`

**기대 동작:**
- 메인이 Step 종료 조건 검증 → 미충족 감지.
- Step 2 또는 Stage 2로 전환하지 않고 `gather/research` 패턴에 따라 남은 에이전트 재호출.
- Stage 2 에이전트(`@writer`, `@editor`)를 이 턴에서 호출하지 않음.

**판정:** 해당 사이클에서 Stage 2 에이전트 `subagent spawn` 미발생 시 PASS.

---

## 시나리오 4: Step 자동 전환 테스트 (사용자 승인 불필요)

**목적:** Step 종료 조건 충족 시 사용자 승인 없이 다음 Step로 자동 전환하는지 확인.

**설정:**
- `workflow.md` Stage 1(design):
  - Step 1(requirements): 종료 조건 = `requirements.md` 존재, 다음 step: `architecture`
  - Step 2(architecture): 종료 조건 = `architecture.md` 존재, 다음 step: `done`
- `_workspace/design/requirements.md` 존재 (Step 1 완료 상태)
- `checkpoint.json`: `current_stage: "design"`, `current_step: "requirements"`

**기대 동작:**
- 메인이 Step 1(requirements) 종료 조건 충족 확인.
- 사용자 승인 요청 없이 `current_step` → `"architecture"` 갱신.
- 같은 턴 내 Step 2(architecture) 에이전트(`@architect`) 즉시 호출.

**판정:** 사용자 승인 요청 없이 `@architect` `subagent spawn` 발생 + `checkpoint.json`의 `current_step` = `"architecture"` 시 PASS.

---

## 시나리오 5: Stage 전환 게이트 테스트 (사용자 승인 필수)

**목적:** Stage 내 모든 Step 완료 시 사용자 승인 게이트가 발동하는지 확인.

**설정:**
- `workflow.md` Stage 1(gather) / Step 1(research): 다음 step = `done`, 다음 stage = `write`
- `task_trend.json`, `task_data.json`: 모두 status=done
- `checkpoint.json`: `current_stage: "gather"`, `current_step: "research"`

**기대 동작:**
- Step 1(research) 종료 조건 충족 + 다음 step = `done`.
- 메인이 Stage 1 모든 Step 완료 확인 → 사용자에게 Stage 전환 보고.
- 사용자 승인 전 Stage 2(`write`) 에이전트 미호출.

**판정:** 사용자 승인 요청 발생 + Stage 2 에이전트 미호출 시 PASS.

---

## 시나리오 6: Step별 에이전트 출입 통제 테스트

**목적:** workflow.md의 현재 Step `활성 에이전트` 목록 밖 에이전트를 메인이 호출하지 않는지 확인.

**설정:**
- `workflow.md` Stage 1(gather) / Step 1(research) 활성 에이전트: `[@researcher-a, @researcher-b]`
- `checkpoint.json`: `current_stage: "gather"`, `current_step: "research"`
- `@writer`는 Stage 2(write) / Step 1(draft-review) 소속 — 현재 step 목록에 없음.

**기대 동작:**
- 메인이 `gather/research` Step 블록 읽기 → `@writer` 목록에 없음 → 호출 보류.
- `@writer` `subagent spawn` 미발생.

**판정:** 해당 사이클에서 `@writer` `subagent spawn` 미발생 시 PASS.
