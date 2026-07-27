# 예시 5: 다중 Stage 다중 Step — 제품 개발 라이프사이클 (Jira Story × Sub-issue)

상위 이슈(Stage) 3개, 각 Stage 내 하위 이슈(Step) 2~3개. 풀 라이프사이클 시연 — 발견·구현·검증 상위 이슈가 각자 다중 하위 이슈로 분해되며 Stage 사이에는 사용자 승인 게이트 발동.

작업(Stage) 분해: `discovery`(발견 작업) → `build`(구현 작업) → `validate`(검증 작업).
Step(하위 이슈) 패턴: market-research=fan_out_fan_in, requirements=pipeline, design=pipeline, implement=supervisor, code-review=producer_reviewer, parallel-qa=fan_out_fan_in, release-notes=pipeline.

## workflow.md

```markdown
<!-- 참고 패턴: discovery=fan_out+pipeline, build=pipeline+supervisor+producer_reviewer, validate=fan_out+pipeline -->
<!-- Stage = 상위 이슈(Jira Issue). Step = 하위 이슈(Jira Sub-issue). -->

## Stage 정의

### Stage 1: discovery

- 종료 조건: 모든 step 완료
- 다음 stage: build
- 사용자 승인 게이트: 필요

#### Step 1: market-research

- 패턴: fan_out_fan_in
- 활성 에이전트: [@trend-researcher, @competitor-researcher, @user-researcher]
- 종료 조건: `_workspace/discovery/task_trend.json`, `task_competitor.json`, `task_user.json` 모두 status=done
- 다음 step: requirements
- 최대 반복 횟수: 1

#### Step 2: requirements

- 패턴: pipeline
- 활성 에이전트: [@requirements-analyst]
- 종료 조건: `_workspace/discovery/requirements.md` 존재
- 다음 step: done
- 최대 반복 횟수: 1

### Stage 2: build

- 종료 조건: 모든 step 완료
- 다음 stage: validate
- 사용자 승인 게이트: 필요

#### Step 1: design

- 패턴: pipeline
- 활성 에이전트: [@architect]
- 종료 조건: `_workspace/build/architecture.md` 존재
- 다음 step: implement
- 최대 반복 횟수: 1

#### Step 2: implement

- 패턴: supervisor
- 활성 에이전트: [@coder-1, @coder-2, @coder-3]
- 종료 조건: `_workspace/build/tasks/task_*.json` 모두 status=done (메인이 동적 배치)
- 다음 step: code-review
- 최대 반복 횟수: 1

#### Step 3: code-review

- 패턴: producer_reviewer
- 활성 에이전트: [@reviewer, @coder-1, @coder-2, @coder-3]
- 종료 조건: `_workspace/build/review_verdict.json`의 verdict=PASS
- 다음 step: done
- 최대 반복 횟수: 3

### Stage 3: validate

- 종료 조건: 모든 step 완료
- 다음 stage: done
- 사용자 승인 게이트: 없음 (마지막 stage)

#### Step 1: parallel-qa

- 패턴: fan_out_fan_in
- 활성 에이전트: [@security-reviewer, @perf-reviewer, @compat-reviewer]
- 종료 조건: `_workspace/validate/task_security.json`, `task_perf.json`, `task_compat.json` 모두 status=done
- 다음 step: release-notes
- 최대 반복 횟수: 1

#### Step 2: release-notes

- 패턴: pipeline
- 활성 에이전트: [@doc-writer]
- 종료 조건: `_workspace/validate/RELEASE_NOTES.md` 존재
- 다음 step: done
- 최대 반복 횟수: 1
```

## 데이터 흐름

```
discovery/market-research:  3 researcher 병렬 → research/{topic}.md
discovery/requirements:     @requirements-analyst → requirements.md
                            ──[Stage 게이트: 사용자 승인]──
build/design:               @architect: requirements.md → architecture.md
build/implement:            메인이 architecture.md → tasks.md(서브태스크 N개) →
                            @coder-* 3명 동적 배치 (supervisor 패턴)
build/code-review:          @reviewer 검토 → REJECT 시 해당 @coder-* 재호출 (loop)
                            ──[Stage 게이트: 사용자 승인]──
validate/parallel-qa:       3 reviewer 병렬 → 각 task_*.json
validate/release-notes:     @doc-writer: 모든 산출물 종합 → RELEASE_NOTES.md
```

## 핵심 패턴 포인트

**3 상위 이슈 × 7 하위 이슈**: 각 상위 이슈(Stage)가 자체 다중 하위 이슈(Step)로 분해. Stage 사이 사용자 승인 게이트 2회(`discovery → build`, `build → validate`) 발동, Stage 내 Step 전환은 자동.

**패턴 7종 중 5종 사용**: fan_out_fan_in / pipeline / supervisor / producer_reviewer 결합 — 한 워크플로우에서 다양한 task 성격 표현. expert_pool·hierarchical·handoff는 미사용 (도메인상 부적합).

**`build/implement` supervisor**: workflow.md 작성 시점에 서브태스크 수 미정 — 메인이 architecture.md 분석 후 런타임에 tasks.md 생성·동적 배치. 활성 에이전트 풀(`@coder-1~3`)만 선언, 실제 할당은 동적.
