# Output formats

## When to produce tables

Use a structured table/list when the user says: `table`, `CSV`, `shareable`, `doc`, `for colleagues`, `links`, `examples`, `segments`, `per competitor`, `export`, `copy`, or asks for multiple creatives grouped by segment/category/competitor.

## Table requirements

Every creative/content row should include:

- Group / segment (if any)
- Competitor / account
- Platform/source
- Hook or angle
- Format
- Key metrics returned by the tool
- Why it matters
- HookRadar creative link (`hookradar_url`)
- Download link (`download_url`) only when requested

If the UI supports copy/export widgets, use them. If not, include a Markdown table and an additional fenced CSV block when the user asks for CSV/copyable output.

## Distribution rule

If the user asks for `N per segment`, `N per competitor`, or `N per category`, satisfy each group independently. Do not return a single global top-N unless the user asked for global top-N.

## Good concise table columns

`Segment | Example | Competitor | Platform | Hook/angle | Signal | Why it works | HookRadar link`

For organic trend tables:

`Trend | Account | Platform | Plays/views | Trending rate | Hook | Creative mechanic | HookRadar link`

For paid ad tables:

`Angle | Advertiser | Format | Status | Launch date | Signal/proxy | Hook | HookRadar link`
