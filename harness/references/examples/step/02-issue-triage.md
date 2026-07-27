# 예시 2: 분류 → 전문가 분석 → 검토 (이슈 트리아지)

작업(Stage) 분해: `triage`(분류·분석 작업) → `review`(검토 작업). Step(=Task) 패턴: triage/classification=expert_pool, triage/analysis=pipeline, review/report=producer_reviewer.

## workflow.md

```markdown
<!-- 참고 패턴: triage=expert_pool+pipeline, review=producer_reviewer -->

## Stage 정의

### Stage 1: triage
- 종료 조건: 모든 step 완료
- 다음 stage: review
- 사용자 승인 게이트: 필요

#### Step 1: classification
- 패턴: expert_pool
- 활성 에이전트: [@bug-analyst, @perf-analyst, @security-analyst]
- 종료 조건: `_workspace/triage/selected_expert.json` 존재
- 다음 step: analysis
- 최대 반복 횟수: 1

#### Step 2: analysis
- 패턴: pipeline
- 활성 에이전트: [@선택된_전문가]  <!-- 심볼릭 플레이스홀더. Step 진입 시 오케스트레이터가 checkpoint.json의 shared_variables.selected_expert 필드를 읽어 실제 에이전트명으로 치환. workflow.md 수정 없음. -->
- 종료 조건: `_workspace/triage/analysis.md` 존재
- 다음 step: done
- 최대 반복 횟수: 1

### Stage 2: review
- 종료 조건: 모든 step 완료
- 다음 stage: done
- 사용자 승인 게이트: 없음 (마지막 stage)

#### Step 1: report
- 패턴: producer_reviewer
- 활성 에이전트: [@report-writer, @tech-lead]
- 종료 조건: `_workspace/review/final_report.md` 존재 + `_workspace/review/approval.json`의 approved=true
- 다음 step: done
- 최대 반복 횟수: 2
```

## 데이터 흐름

```
triage/classification: 메인이 이슈 유형 분류 → selected_expert.json 생성
triage/analysis:       selected_expert.json 기반 적합한 @*-analyst 1개 호출
                       → _workspace/triage/analysis.md
review/report:         @report-writer가 analysis.md 읽고 보고서 초안 작성
                       @tech-lead → 승인 또는 수정 요청
```

## 심볼릭 플레이스홀더 처리

`[@선택된_전문가]`는 런타임에 오케스트레이터가 치환한다.

```
Step 2(analysis) 진입 시:
  1. checkpoint.json의 shared_variables.selected_expert 읽기
  2. 해당 에이전트명으로 subagent spawn 호출
  3. workflow.md 파일 자체는 수정하지 않음
```
