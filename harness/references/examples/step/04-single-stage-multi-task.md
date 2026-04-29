# 예시 4: 단일 Stage(상위 이슈) 다중 Step(하위 이슈) — 조사 → 구현 → 리뷰

상위 이슈(Stage) 1개에 하위 이슈(Step) 3개를 두는 사례. **Jira Issue → Sub-issue** 모델 시연: 하나의 deliverable("기능 구현") 상위 이슈 안에서 하위 이슈별로 서로 다른 패턴 사용.

상위 이슈(Stage) 분해: `feature-build`(기능 구현, 하위 이슈 3개). Step(하위 이슈) 패턴: research=fan_out_fan_in, implement=pipeline, review=producer_reviewer.

## workflow.md

```markdown
<!-- 참고 패턴: research=fan_out_fan_in, implement=pipeline, review=producer_reviewer -->
<!-- Stage = 상위 이슈(Jira Issue). Step = 하위 이슈(Jira Sub-issue). -->

## Stage 정의

### Stage 1: feature-build
- 종료 조건: 모든 step 완료
- 다음 stage: done
- 사용자 승인 게이트: 없음 (단일 stage)

#### Step 1: research
<!-- 하위 이슈: 라이브러리·API 자료 병렬 수집 -->
- 패턴: fan_out_fan_in
- 활성 에이전트: [@api-researcher, @lib-researcher, @example-researcher]
- 종료 조건: `_workspace/research/task_api.json`, `task_lib.json`, `task_example.json` 모두 status=done
- 다음 step: implement
- 최대 반복 횟수: 1

#### Step 2: implement
<!-- 하위 이슈: 조사 결과 기반 코드 구현 -->
- 패턴: pipeline
- 활성 에이전트: [@coder]
- 종료 조건: `_workspace/build/feature.ts` 존재 + `_workspace/build/test.ts` 존재
- 다음 step: review
- 최대 반복 횟수: 1

#### Step 3: review
<!-- 하위 이슈: 코드 리뷰 루프 (PASS 시 종료) -->
- 패턴: producer_reviewer
- 활성 에이전트: [@coder, @reviewer]
- 종료 조건: `_workspace/build/review_verdict.json`의 verdict=PASS
- 다음 step: done
- 최대 반복 횟수: 3
```

## 데이터 흐름

```
feature-build/research:  @*-researcher 3명 병렬 → _workspace/research/{topic}.md
                         메인이 task_*.json 모두 done 확인 후 자동 전환
feature-build/implement: @coder가 research/*.md 읽고 → feature.ts + test.ts 생성
                         pipeline 단일 task → 자동 전환
feature-build/review:    @reviewer가 코드·테스트 검토 → review_verdict.json
                         verdict=REJECT → @coder 재호출 (findings.md의 [변경 요청] 주입)
                         verdict=PASS → step done → stage done
```

## 핵심 패턴 포인트

**1 상위 이슈 / 3 하위 이슈**: 하나의 deliverable("기능 구현") 상위 이슈 안에서 하위 이슈가 성격별로 분해된다 — 조사(병렬)·구현(순차)·리뷰(루프). 각 하위 이슈가 독립 패턴을 갖되, Stage 게이트는 1회(전체 상위 이슈 완료 시점)만 발동.

**Step 자동 전환만 발생**: `feature-build` Stage 내 3 Step 모두 종료 조건 충족 시 사용자 개입 없이 자동 전진. Stage 끝(`다음 stage: done`)이라 Stage 승인 게이트도 없음 — 완전 자동 흐름.

**패턴 다양성**: 한 상위 이슈(Stage) 안에서 fan_out_fan_in → pipeline → producer_reviewer가 순차 결합. Jira Issue → Sub-issue 모델의 표현력 시연.
