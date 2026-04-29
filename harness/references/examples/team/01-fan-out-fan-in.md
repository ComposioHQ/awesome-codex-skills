# 예시 1: 리서치 팀 (Fan-out/Fan-in 패턴)

## 팀 아키텍처

주제 하나를 4개 전문 영역으로 팬아웃해 병렬 조사한 뒤, 메인 에이전트가 팬인 통합한다.

## 에이전트 구성

| 에이전트               | 유형    | sandbox_mode  | 산출물                                    |
| ---------------------- | ------- | ------------- | ----------------------------------------- |
| @official-researcher   | Analyst | `read-only`   | `_workspace/{plan_name}/01_official.md`   |
| @media-researcher      | Analyst | `read-only`   | `_workspace/{plan_name}/01_media.md`      |
| @community-researcher  | Analyst | `read-only`   | `_workspace/{plan_name}/01_community.md`  |
| @background-researcher | Analyst | `read-only`   | `_workspace/{plan_name}/01_background.md` |

## 오케스트레이터 워크플로우

```
Phase 0: _workspace/ + checkpoint.json 존재 여부 확인 → 실행 모드 결정:
         - checkpoint.json 존재 + status: "in_progress" → 중단 지점 재개(Resume)
           workflow.md 읽기 → current_stage, current_step 복원
         - checkpoint.json 존재 + status: "completed" → 완료 상태.
           사용자 요청이 부분 수정이면 부분재실행, 새 입력이면 새 실행으로 분기. Resume 금지.
         - _workspace/ 미존재 또는 checkpoint.json 미존재 → 신규 실행 (Phase 1로 진행)
Phase 1: 사용자 입력 분석
         workflow.md 생성:
           Stage 1: competitor-research / 사용자 승인 게이트: 없음
           Step 1: research / 패턴: fan_out_fan_in / 활성 에이전트: [4명] / 다음 step: done
         checkpoint.json 생성 (current_stage: "competitor-research", current_step: "research",
                            active_pattern: "fan_out_fan_in", status: "in_progress")
         tasks.md 4개 조사 작업 등록
         findings.md 초기화: [핵심 통찰], [핵심 키워드], [공유 변수/경로], [데이터 충돌] 섹션 생성
Phase 2: [Step 실행 루프 — Stage competitor-research / Step research]
         단일 응답 턴에서 @official/@media/@community/@background를
         병렬 배치 호출
         - 각 에이전트 프롬프트에 findings.md의 [핵심 키워드]·[공유 변수/경로] 주입
Phase 3: 각 산출물을 `cat`으로 수집
         - 산출물 파일 미존재(에이전트 실패) → 최대 2회 재시도(총 3회).
           3회 후에도 미생성 → Blocked, 사용자 확인 요청으로 수동 개입 요청. 임의 Skip 금지.
         - 수집 성공 → findings.md [데이터 충돌]에 상충 기록
         - 상충 정보는 교차 영역(예: media 발견 투자 뉴스 ↔ background 경쟁사)을
           메인 에이전트가 findings.md에 병기하고, 필요 시 해당 에이전트를 재호출
           (최대 2회 재시도(총 3회). 그래도 상충 미해결 → 출처 병기 후 진행, findings.md [데이터 충돌]에 미해결 표시)
         Step research 종료 조건 충족 → checkpoint.json 갱신:
           - step_history에 "research" completed_at 기록
           - stage_history에 "competitor-research" completed_at 기록
           - current_stage·current_step: "done", status: "completed", last_updated: 현재 타임스탬프
         사용자 승인 게이트: 없음 → 워크플로우 자동 완료
Phase 4: 통합 보고서 _workspace/{plan_name}/final/research_report.md 생성 (상충 정보는 출처 병기)
Phase 5: 사용자 보고, _workspace/ 보존
```

## 브로커 중개 패턴 (SendMessage 대체)

Claude Code에서 `official → media → background`로 SendMessage가 오갔던 부분은 Codex CLI에서 다음처럼 변환된다:

```
@official 산출물(_workspace/{plan_name}/01_official.md) 완료
  → 메인 에이전트가 `cat`으로 확인
  → findings.md [공유 변수/경로]에 "official의 공식 발표 X는 media 맥락에서 재검증 필요" 추가
  → @media 호출 시 프롬프트에 findings.md의 해당 섹션을 요약 주입
```
