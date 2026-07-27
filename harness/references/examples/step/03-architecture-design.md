# 예시 3: 순차 설계 후 병렬 검증 (아키텍처 설계)

작업(Stage) 분해: `design`(설계 작업, 3 task) → `validate`(검증 작업, 1 task). Step(=Task) 패턴: design Stage 3 Step 모두 pipeline, validate/parallel-review=fan_out_fan_in.

## workflow.md

```markdown
<!-- 참고 패턴: design=pipeline(다단계), validate=fan_out_fan_in -->

## Stage 정의

### Stage 1: design
- 종료 조건: 모든 step 완료
- 다음 stage: validate
- 사용자 승인 게이트: 필요

#### Step 1: requirements
- 패턴: pipeline
- 활성 에이전트: [@requirements-analyst]
- 종료 조건: `_workspace/design/requirements.md` 존재
- 다음 step: architecture
- 최대 반복 횟수: 1

#### Step 2: architecture
- 패턴: pipeline
- 활성 에이전트: [@architect]
- 종료 조건: `_workspace/design/architecture.md` 존재
- 다음 step: api-design
- 최대 반복 횟수: 1

#### Step 3: api-design
- 패턴: pipeline
- 활성 에이전트: [@api-designer]
- 종료 조건: `_workspace/design/api_spec.md` 존재
- 다음 step: done
- 최대 반복 횟수: 1

### Stage 2: validate
- 종료 조건: 모든 step 완료
- 다음 stage: done
- 사용자 승인 게이트: 없음 (마지막 stage)

#### Step 1: parallel-review
- 패턴: fan_out_fan_in
- 활성 에이전트: [@security-reviewer, @perf-reviewer, @compat-reviewer]
- 종료 조건: `_workspace/validation/task_security.json`, `task_perf.json`, `task_compat.json` 모두 status=done
- 다음 step: done
- 최대 반복 횟수: 1
```

## 데이터 흐름

```
design/requirements:      @requirements-analyst → requirements.md
design/architecture:      @architect: requirements.md 읽고 → architecture.md
design/api-design:        @api-designer: architecture.md 읽고 → api_spec.md
validate/parallel-review: 세 reviewer가 api_spec.md + architecture.md 병렬 검토
                          메인이 세 리뷰 결과 통합 → 최종 보고
```

## 핵심 패턴 포인트

Stage 내 Step 3개(requirements → architecture → api-design)가 모두 **pipeline(순차)**이므로 각 Step 종료 후 자동 전환된다. 사용자 승인 게이트는 `design` → `validate` Stage 전환 시점 1회만 발동.
