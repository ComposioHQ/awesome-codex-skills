# HookRadar MCP workflows


## Actual tool names only

The names in this document are the public HookRadar MCP contract. Use only the listed tool names. If the desired behavior is not represented by a listed MCP tool, explain the intent and compose the closest available listed tools; do not name internal platform functions, legacy agent functions, or imagined tools.

## Tool map

**Teams and context**
- `list_teams()` ? find available HookRadar brand slugs.
- `create_team(name)` ? create a new brand when the user has none.
- `get_team_info(team)` ? plan, limits, usage balance.
- `get_brand_context(team)` ? counts and whether the workspace is empty.
- `list_sources(team)` ? tracked Meta pages, TikTok advertisers, organic accounts/queries.

**Read creatives and content**
- `get_meta_ads(team, page_id, format, status, sort, page, limit)` ? Meta ads for one tracked page.
- `get_tiktok_ads(team, search, advertiser_id, sort, page, limit)` ? TikTok ads.
- `get_tiktok_organic(team, sort, search, content_type, time_range, page, limit)` ? TikTok organic videos.
- `get_instagram_organic(team, sort, search, content_type, time_range, page, limit)` ? Instagram organic content.
- `search(team, query)` ? compact cross-source search, useful for finding IDs but not enough for deep answers.
- `get_reports(team, report_id?)` ? list reports or fetch a full report.

**AI analysis**
- `get_meta_ad_analysis(team, creative_id)`
- `get_tiktok_ads_analysis(team, ad_id)`
- `get_organic_analysis(team, video_id, platform)`
- If status is `not_found`, start analysis with `analyze_meta_ads`, `analyze_tiktok_ads`, `analyze_organic`, or unified `analyze_asset`.

**Add sources / launch long jobs**
- `add_meta_competitor(team, name, page_id | ad_library_url)`
- `add_tiktok_advertiser(team, ad_id, label?)` where `ad_id` is the TikTok advertiser/business id.
- `add_organic_account(team, handle, platform, label?, url?)`
- `add_organic_query(team, query, platform)`
- `start_report(team, page_ids, type?)`
- `get_task_status(team, root_id)` for parse/analyze tasks only. Reports are checked with `get_reports(report_id=...)`.

## Query patterns

### ?Show top creatives across competitors?
1. `list_sources(team)`.
2. For Meta: call `get_meta_ads` for each relevant `page_id`, usually `sort=active_first` or `longest_running`, `status=all`, `limit=20-50`.
3. For organic: call organic tools with `sort=top_trending` or `most_views` depending on the question.
4. Merge/rank in the answer using returned metrics. For paid Meta trend hunting, prefer active status, running days, same-content variants, recency, and analysis hooks over raw EU impressions alone.
5. Include `hookradar_url` per row.

### ?Analyze this asset / transcript / scene breakdown?
1. Get the asset from the relevant read tool or use the ID the user supplied.
2. Call the relevant `get_*_analysis`.
3. If `not_found`, start `analyze_*` and poll briefly via `get_task_status`.
4. Read analysis again. If still missing, say analysis is still running; do not fabricate transcript/scenes.

### ?Add source and show results?
1. Call the matching `add_*` tool.
2. If `started`, explain the source was added and data is collecting. Poll only briefly.
3. Read results only after data exists. Empty immediately after adding means ?not ready yet?, not ?no results?.

## Link policy

Always surface HookRadar links first:

- Creative page: `hookradar_url`
- Analysis page: `analysis_url`
- Media download: `download_url`

Do not use `fb_ad_link`, `detail_url`, `post_url`, or CDN URLs as primary user-facing links unless HookRadar URLs are absent and you clearly mark them as fallback.
