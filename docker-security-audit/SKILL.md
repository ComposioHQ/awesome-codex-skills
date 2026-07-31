---
name: docker-security-audit
description: Audit Dockerfile and docker-compose configurations for root user vulnerabilities, unpinned base images, exposed secrets, and multi-stage build optimizations. Use when inspecting or hardening container builds.
---

# Docker Security Audit

Audit container configurations to detect security vulnerabilities, enforce principle of least privilege, and optimize build layers.

## Audit Checklist

### 1. Non-Root User Execution
Check if the container runs as `root`:
- Ensure a non-root user is created and declared via `USER <username>` before runtime directives.
- Example fix:
  ```dockerfile
  RUN addgroup -S appgroup && adduser -S appuser -G appgroup
  USER appuser
  ```

### 2. Base Image Pinning & Hardening
- Avoid floating `latest` tags (e.g., `FROM node:latest`).
- Recommend specific version tags or digest SHAs (e.g., `FROM node:20.18-alpine`).
- Prefer minimal base images (Alpine, Distroless) to reduce vulnerability surface area.

### 3. Secret Leak Prevention
- Check for hardcoded API keys, tokens, or passwords in `ENV` or `ARG` directives.
- Ensure secrets are passed via BuildKit secret mounts or runtime environment variables:
  ```dockerfile
  RUN --mount=type=secret,id=api_key ./build.sh
  ```

### 4. Multi-Stage Build Optimization
- Separate build dependencies from runtime dependencies.
- Ensure build tools (compilers, dev dependencies) are discarded in final stage artifacts.

### 5. Healthcheck & Exposed Ports
- Verify `HEALTHCHECK` directive is present to allow orchestration monitoring.
- Ensure only necessary ports are exposed (`EXPOSE <port>`).
