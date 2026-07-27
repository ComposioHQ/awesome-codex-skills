#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import path from "node:path";

const usage = `Usage:
  node scripts/publish-html2link.mjs <file> [--slug <slug> --update-token <token>]
  node scripts/publish-html2link.mjs --delete --slug <slug> --update-token <token>

Environment:
  HTML2LINK_BASE_URL   Defaults to https://html2link.dev
  HTML2LINK_API_TOKEN  Optional bearer token for authenticated uploads
`;

function readArgs(argv) {
  const args = {
    file: null,
    slug: null,
    updateToken: null,
    delete: false,
    help: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const value = argv[i];
    if (value === "--help" || value === "-h") {
      args.help = true;
    } else if (value === "--delete") {
      args.delete = true;
    } else if (value === "--slug") {
      args.slug = argv[++i] ?? null;
    } else if (value === "--update-token") {
      args.updateToken = argv[++i] ?? null;
    } else if (!args.file) {
      args.file = value;
    } else {
      throw new Error(`Unexpected argument: ${value}`);
    }
  }

  return args;
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();
  let body;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = text;
  }

  if (!response.ok) {
    const detail = typeof body === "string" ? body : JSON.stringify(body);
    throw new Error(`html2link request failed (${response.status}): ${detail}`);
  }

  return body;
}

async function upload({ file, slug, updateToken, baseUrl, apiToken }) {
  if (!file) {
    throw new Error("Missing file path.");
  }

  const absolutePath = path.resolve(file);
  const bytes = await readFile(absolutePath);
  const form = new FormData();
  form.append("file", new Blob([bytes]), path.basename(absolutePath));

  if (slug) {
    form.append("slug", slug);
  }
  if (updateToken) {
    form.append("updateToken", updateToken);
  }

  const headers = {};
  if (apiToken) {
    headers.Authorization = `Bearer ${apiToken}`;
  }

  return requestJson(`${baseUrl}/api/upload`, {
    method: "POST",
    headers,
    body: form,
  });
}

async function deleteLink({ slug, updateToken, baseUrl, apiToken }) {
  if (!slug || !updateToken) {
    throw new Error("Deleting a link requires --slug and --update-token.");
  }

  const headers = { "Content-Type": "application/json" };
  if (apiToken) {
    headers.Authorization = `Bearer ${apiToken}`;
  }

  return requestJson(`${baseUrl}/api/upload`, {
    method: "DELETE",
    headers,
    body: JSON.stringify({ slug, updateToken }),
  });
}

async function main() {
  const args = readArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write(usage);
    return;
  }

  const baseUrl = (process.env.HTML2LINK_BASE_URL || "https://html2link.dev").replace(/\/+$/, "");
  const apiToken = process.env.HTML2LINK_API_TOKEN || "";
  const result = args.delete
    ? await deleteLink({ ...args, baseUrl, apiToken })
    : await upload({ ...args, baseUrl, apiToken });

  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error.message}\n\n${usage}`);
  process.exit(1);
});
