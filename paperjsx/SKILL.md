---
name: paperjsx
description: Generate PPTX presentations from structured JSON using PaperJSX, and guard DOCX, XLSX, and PDF requests until their packages are installable.
---

# PaperJSX Document Generation

Generate professional documents from JSON layout specs. PaperJSX is generation-only — it creates new files, it does not edit existing ones.

The standalone npm path is currently verified for PPTX only. For DOCX, XLSX, and PDF, check package metadata before attempting an install or render.

## Triggers

Use this skill when the user asks to:
- Create a presentation or generate slides
- Make a PPTX or PowerPoint file
- Create a Word document or DOCX
- Generate an Excel spreadsheet with charts
- Create a JSON to PPTX, JSON to DOCX, or JSON to XLSX file
- Generate a PDF invoice, report, or chart document

## Install

Install the standalone PPTX package:

```bash
npm install @paperjsx/json-to-pptx
```

Before using DOCX, XLSX, PDF, or the MCP server packages, verify that their published dependencies no longer contain `workspace:*` entries:

```bash
npm view @paperjsx/json-to-docx@latest dependencies --json
npm view @paperjsx/json-to-xlsx@latest dependencies --json
npm view @paperjsx/json-to-pdf@latest dependencies --json
npm view @paperjsx/mcp-server@latest dependencies --json
```

If any dependency value is `workspace:*`, do not run `npm install` for that package in the user's project. Tell the user that the requested PaperJSX format is not currently installable as a standalone npm package, and offer PPTX generation or another document-generation path instead.

If PaperJSX MCP tools are already connected in the tool catalog, you may use those tools directly. The metadata check above is only for installing packages yourself.

## How it works

1. Build a JSON layout spec matching the schema in `references/json-schema.md`
2. Write a Node.js script that passes the JSON to the PaperJSX engine
3. Run the script to generate the output file
4. Validate the output file exists and is non-zero bytes

Do **not** write imperative PaperJSX API code. The execution model is always: JSON spec in, document file out.

## Example: PPTX generation

```javascript
import { PaperEngine } from "@paperjsx/json-to-pptx";
import fs from "node:fs";

const spec = {
  type: "Document",
  meta: { title: "Q4 Review" },
  slides: [
    {
      type: "Slide",
      children: [
        { type: "Text", content: "Q4 2025 Business Review", style: { fontSize: 36, bold: true } }
      ]
    }
  ]
};

const buffer = await PaperEngine.render(spec);
fs.writeFileSync("presentation.pptx", buffer);
console.log("Generated presentation.pptx");
```

## Guarded formats

For DOCX, XLSX, and PDF requests, follow this order:

1. Use connected PaperJSX MCP tools if they are available.
2. If no MCP tools are available, run the npm metadata check from the install section.
3. Only install and call a format package when the metadata check shows concrete dependency versions.
4. If the package still references `workspace:*`, stop before writing generation code and explain the packaging limitation to the user.

## Validation

After generating any file, always verify:

```javascript
import fs from "node:fs";

const stats = fs.statSync("output.pptx");
if (stats.size === 0) {
  throw new Error("Generated file is empty");
}
console.log(`Output file: ${stats.size} bytes`);
```

If the engine throws an error, surface the full error message to the user.

## Schema reference

See `references/json-schema.md` for the complete JSON layout spec schema. Some schemas may describe formats whose standalone npm packages are not currently installable; apply the guarded-format workflow before using those package APIs.
