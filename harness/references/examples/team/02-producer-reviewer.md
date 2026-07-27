# 예시 2: 웹툰 제작 팀 (Producer-Reviewer 패턴)

## 팀 아키텍처

생성자(artist)와 검증자(reviewer)가 짧은 루프로 산출물을 정제한다. 메인 에이전트가 리뷰 리포트를 해석해 재생성 루프를 제어한다.

## 에이전트 구성

| 에이전트          | 유형     | 역할             | sandbox_mode      | 스킬                                  |
| ----------------- | -------- | ---------------- | ----------------- | ------------------------------------- |
| @webtoon-artist   | Coder    | 패널 이미지 생성 | `workspace-write` | `generate-webtoon`                    |
| @webtoon-reviewer | Reviewer | 품질 검수        | `workspace-write` | `review-webtoon`, `fix-webtoon-panel` |

## 에이전트 파일 전문 예시: `.codex/agents/webtoon-reviewer.toml`

````toml
name = "webtoon-reviewer"
description = "웹툰 패널의 품질을 검수하는 전문가. 구도·캐릭터 일관성·텍스트 가독성·연출을 평가. 웹툰 QA·검수·재작업 요청 시 반드시 이 에이전트를 선택."
model = "gpt-5.3-codex"
sandbox_mode = "workspace-write"
model_reasoning_effort = "high"

developer_instructions = """

# Webtoon Reviewer — 웹툰 품질 검수 전문가

웹툰 패널의 품질을 검수하는 전문가. 시각적 완성도·스토리 전달력·캐릭터 일관성을 기준으로 평가한다.

## 핵심 역할

1. 각 패널의 구도와 시각적 완성도 평가
2. 캐릭터 외형의 패널 간 일관성 검증
3. 말풍선 텍스트의 가독성과 배치 평가
4. 전체 에피소드의 연출 흐름과 페이싱 검토

## 작업 원칙

- PASS / FIX / REDO 3단계로 명확히 판정
- FIX는 부분 수정 가능, REDO는 전면 재생성 필요
- 주관적 취향이 아닌 객관적 기준(일관성·가독성·구도)으로 판단

## 입력/출력 프로토콜

- 입력: `_workspace/{plan_name}/panels/` 디렉토리의 패널 이미지들
- 출력: `_workspace/{plan_name}/review_report.md`
- 형식:

```

## Panel {N}

- 판정: PASS | FIX | REDO
- 사유: [구체적 이유]
- 수정 지시: [FIX/REDO인 경우 구체적 수정 방향]

```

## 협업 프로토콜 (Codex CLI)

- @webtoon-artist에게 직접 지시할 수 없다. 모든 수정 요청은
  `_workspace/{plan_name}/review_report.md`에 기록하며, 메인 에이전트가
  해당 리포트를 findings.md [변경 요청]으로 요약한 뒤 artist를 재호출한다.

## 에러 핸들링

- 이미지 로드 실패 시 해당 패널을 REDO로 판정
- 3회 재생성 후에도 REDO인 패널은 **Blocked 처리 후 사용자 확인 요청으로 사용자 개입 요청. 임의 PASS 처리 절대 금지.**
- 판정 기준이 모호하면 사용자 확인 요청으로 레퍼런스 이미지를 요청
"""
````

## 오케스트레이터 워크플로우

```
Phase 0: (예시 1과 동일 — 상태 확인·Resume·신규 실행 분기)
Phase 1: 사용자 입력(에피소드 명세) 분석
         workflow.md 생성:
           Stage 1: webtoon-episode / 사용자 승인 게이트: 없음
           Step 1: produce / 패턴: producer_reviewer / 활성 에이전트: [@webtoon-artist, @webtoon-reviewer] / 다음 step: done
         checkpoint.json 생성 (current_stage: "webtoon-episode", current_step: "produce",
                            active_pattern: "producer_reviewer", status: "in_progress")
         tasks.md 패널 작업 등록, findings.md [공유 변수/경로]·[변경 요청] 초기화
Phase 2: [Step 실행 루프 — Stage webtoon-episode / Step produce]
         @webtoon-artist 호출 → _workspace/{plan_name}/panels/*.png 생성
         @webtoon-reviewer 호출 → _workspace/{plan_name}/review_report.md 생성
         메인 에이전트가 review_report.md 파싱:
         - FIX/REDO 패널 → 수정 지시를 findings.md [변경 요청]에 기록 → @webtoon-artist 재호출
           (FIX: 부분 수정, REDO: 전면 재생성)
         - 1회차 검수 후 REDO 패널이 전체의 50% 이상이면 재호출 전 사용자 확인 요청으로 프롬프트 재조정 제안
         - FIX+REDO 합산 재호출 최대 2회 재시도(총 3회). 초과 시 Blocked → 사용자 확인 요청
         루프 탈출 조건: 모든 패널 PASS → Phase 3으로 전환
Phase 3: 최종 PASS 집계 → step "produce" 종료 조건 충족
         checkpoint.json 갱신:
           - step_history에 "produce" completed_at 기록
           - stage_history에 "webtoon-episode" completed_at 기록
           - current_stage·current_step: "done", status: "completed", last_updated: 현재 타임스탬프
         사용자 승인 게이트: 없음 → 워크플로우 자동 완료
Phase 4: 최종 에피소드 _workspace/{plan_name}/final/episode.md 생성
         (Blocked 패널은 사용자 확인 요청 승인 후 사용자 결정에 따라 포함·제외 처리)
Phase 5: 사용자 보고, _workspace/ 보존
```
