---
name: html2link-publish
description: Publish generated artifacts to html2link.dev and return short shareable URLs. Use when Codex or another agent creates an HTML file, static site ZIP, PDF, Markdown document, spreadsheet, DOCX, or PPTX and needs to give the user a browser-friendly link instead of only a local file path or attachment.
---

# html2link Publish

## Overview

Use html2link to turn local artifacts into short links that open directly in a browser. Prefer this skill after creating a report, prototype, dashboard, presentation, document, static site, or other deliverable that the user may want to view or share.

## Supported Inputs

- `.html`, `.htm`
- `.zip` static sites that contain `index.html`; archives with one top-level folder are normalized by html2link
- `.pdf`
- `.md`, `.markdown`
- `.xlsx`, `.xls`, `.csv`
- `.docx`
- `.pptx`

## Publish Workflow

1. Write the artifact to a stable local file path.
2. If the artifact is a static site, package it as a ZIP with `index.html` at the root when possible.
3. Upload the file with `scripts/publish-html2link.mjs` or an equivalent `curl` request.
4. Return only the public `url` field to the user unless they ask for API details.
5. Treat `updateToken` as private. Store or show it only when the user explicitly wants to update or delete the same link later.

## Script

Run the bundled script from the skill directory or with an absolute path:

```bash
node scripts/publish-html2link.mjs /absolute/path/to/report.html
```

The script prints the JSON API response. It reads these optional environment variables:

- `HTML2LINK_BASE_URL`: Defaults to `https://html2link.dev`
- `HTML2LINK_API_TOKEN`: Bearer token for files over the anonymous limit

Update an existing link:

```bash
node scripts/publish-html2link.mjs /absolute/path/to/report.html --slug a1B2c3D4 --update-token keep-this-private
```

Delete a link:

```bash
node scripts/publish-html2link.mjs --delete --slug a1B2c3D4 --update-token keep-this-private
```

## Direct API

Upload with multipart field `file`:

```bash
curl -F "file=@/absolute/path/to/report.html" https://html2link.dev/api/upload
```

For files above 1 MB, include a signed-in user's API token:

```bash
curl -H "Authorization: Bearer $HTML2LINK_API_TOKEN" -F "file=@/absolute/path/to/report.pptx" https://html2link.dev/api/upload
```

Successful response:

```json
{
  "slug": "a1B2c3D4",
  "updateToken": "keep-this-private",
  "url": "https://html2link.dev/x/a1B2c3D4",
  "kind": "html",
  "size": "42 KB",
  "updated": false
}
```

Update an existing link:

```bash
curl -F "slug=a1B2c3D4" -F "updateToken=keep-this-private" -F "file=@/absolute/path/to/report.html" https://html2link.dev/api/upload
```

Delete an existing link:

```bash
curl -X DELETE -H "Content-Type: application/json" -d '{"slug":"a1B2c3D4","updateToken":"keep-this-private"}' https://html2link.dev/api/upload
```

## Limits And Errors

- Anonymous uploads are free up to 1 MB.
- Authenticated uploads are supported up to 100 MB.
- If the API returns `requiresLogin: true`, tell the user the file is over the anonymous limit and needs authenticated publishing with `HTML2LINK_API_TOKEN`.
- If upload fails, report the HTTP status and response body. Do not invent a link.
- If publishing sensitive or private material, confirm that the user wants a public share link before uploading.

## User Response

Keep the response concise:

```text
Published: https://html2link.dev/x/a1B2c3D4
```

Mention the local file path only when it is useful for follow-up work.
