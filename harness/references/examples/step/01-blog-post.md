# 예시 1: 병렬 수집 후 검토 루프 (블로그 포스트 작성)

작업(Stage) 분해: `gather`(자료 수집 작업) → `write`(작성 작업). Step(=Task) 패턴: gather/research = fan_out_fan_in, write/draft-review = producer_reviewer.

## workflow.md

```markdown
<!-- 참고 패턴: gather=fan_out_fan_in, write=producer_reviewer -->

## Stage 정의

### Stage 1: gather
- 종료 조건: 모든 step 완료
- 다음 stage: write
- 사용자 승인 게이트: 필요

#### Step 1: research
- 패턴: fan_out_fan_in
- 활성 에이전트: [@researcher-trend, @researcher-data, @researcher-case]
- 종료 조건: `_workspace/research/task_trend.json`, `task_data.json`, `task_case.json` 모두 status=done
- 다음 step: done
- 최대 반복 횟수: 1

### Stage 2: write
- 종료 조건: 모든 step 완료
- 다음 stage: done
- 사용자 승인 게이트: 없음 (마지막 stage)

#### Step 1: draft-review
- 패턴: producer_reviewer
- 활성 에이전트: [@writer, @editor]
- 종료 조건: `_workspace/editor_verdict.json`의 verdict=PASS 또는 iterations ≥ 3
- 다음 step: done
- 최대 반복 횟수: 3
```

## 데이터 흐름

```
gather/research:     @researcher-* → _workspace/research/{topic}.md (병렬)
write/draft-review:  메인이 research/*.md 요약 → @writer에 주입
                     @writer → _workspace/draft.md
                     @editor → _workspace/editor_verdict.json
                     verdict=REJECT → @writer 재호출 (findings 업데이트 포함)
```
