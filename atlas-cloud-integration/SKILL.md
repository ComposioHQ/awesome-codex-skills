---
name: atlas-cloud-integration
description: Integrate Atlas Cloud into Codex workflows. Use when adding Atlas Cloud as an OpenAI-compatible LLM provider, wiring async image or video generation, uploading media inputs, or verifying live Atlas model schemas before implementation.
---

# Atlas Cloud Integration

## Overview

Use this skill to add Atlas Cloud support to codebases, agents, and Codex
workflows without guessing API details. Atlas Cloud has two API surfaces:

- LLM chat: `https://api.atlascloud.ai/v1`
- Image, video, prediction polling, and uploads: `https://api.atlascloud.ai/api/v1`

Always read the API key from `ATLASCLOUD_API_KEY`. Never commit API keys,
tokens, generated bearer headers, screenshots containing secrets, or sample
payloads with real credentials.

## When to Use

Use this skill when the task involves:

- Adding an Atlas Cloud provider to an existing OpenAI-compatible client.
- Implementing image or video generation through Atlas Cloud's async media API.
- Uploading local media so it can be used as an image/video model input.
- Choosing Atlas model IDs or request parameters for code, tests, docs, or examples.
- Reviewing an existing Atlas integration for stale model IDs, guessed fields, or missing polling.

Do not use it for unrelated local-only inference code, model-weight utilities, or
projects where there is no real provider/configuration surface to integrate.

## Core Workflow

### 1. Discover Models Live

Before writing model IDs or request fields:

```bash
curl -s https://api.atlascloud.ai/api/v1/models
```

Use only models where `display_console` is `true`. For the selected model,
fetch the `schema` URL from the model entry and inspect:

```text
components.schemas.Input.properties
```

Only send fields that appear in that schema. If a field is absent, do not send
it, even if another model or old example used it.

### 2. Add LLM Chat Through OpenAI-Compatible Clients

When the project already uses the OpenAI SDK, add Atlas Cloud as configuration
instead of creating a custom chat client:

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.ATLASCLOUD_API_KEY,
  baseURL: "https://api.atlascloud.ai/v1",
});
```

Keep model selection configurable. Do not bake in a model ID unless the target
project already pins defaults in provider presets.

### 3. Add Image And Video Through The Media API

Image and video generation are asynchronous. Submit once, then poll.

```typescript
const mediaBaseUrl = "https://api.atlascloud.ai/api/v1";

const submitResponse = await fetch(`${mediaBaseUrl}/model/generateImage`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.ATLASCLOUD_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: selectedModel,
    prompt,
    ...schemaCheckedParams,
  }),
});
```

For video, use `/model/generateVideo`. After submission, poll:

```typescript
const predictionResponse = await fetch(
  `${mediaBaseUrl}/model/prediction/${predictionId}`,
  {
    headers: {
      Authorization: `Bearer ${process.env.ATLASCLOUD_API_KEY}`,
    },
  },
);
```

Handle these terminal states:

- success: `completed`, `succeeded`
- failure: `failed`, `error`, `cancelled`, `canceled`

Add a timeout. Retry polling GET requests if needed, but do not blindly retry
generation POST requests because they can create duplicate billable jobs.

### 4. Upload Media Inputs

For local image or media inputs, upload the file first:

```text
POST https://api.atlascloud.ai/api/v1/model/uploadMedia
```

Use the returned URL only for model schema fields that explicitly accept media
URLs. Treat uploaded files as temporary generation inputs, not permanent
storage.

## Common Rationalizations

"The example model worked before, so it is safe to hard-code."

Model catalogs and schemas change. Fetch the live model list and schema in the
same implementation session.

"The LLM endpoint and media endpoint are interchangeable."

They are not. LLM chat is OpenAI-compatible. Image, video, upload, and polling
use the media API.

"A README mention is enough."

If the repository has provider code, registry entries, presets, or configuration
hooks, integrate there first. Documentation should describe a working path, not
replace it.

## Red Flags

- Model IDs or parameters are copied from memory instead of live schema discovery.
- API keys are committed, logged, included in examples, or embedded in tests.
- Media generation posts to `/v1/chat/completions`.
- Polling never times out or ignores failed jobs.
- Request code retries generation POST requests automatically.
- Code sends fields like `image_size`, `ratio`, `aspect_ratio`, or `resolution`
  without checking the selected model schema.
- The change adds sponsor text, logo walls, credits, partner claims, or other
  promotional content instead of a functional integration.

## Verification

Before finishing:

1. Confirm `ATLASCLOUD_API_KEY` is the only API key path.
2. Confirm every model ID came from a live model-list response.
3. Confirm every request field exists in the selected model schema.
4. Run the narrow provider, adapter, or workflow tests.
5. Run type checks or compilation for the touched language.
6. Test the missing-key path.
7. Confirm async media jobs handle success, failure, and timeout states.
