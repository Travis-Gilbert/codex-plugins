---
description: Verify a deployment is live and responding correctly. Checks health endpoints, page loads, and basic functionality.
allowed-tools: Bash, Read, Glob
argument-hint: <url-or-project-name>
---

1. Determine the URL to check:
   - If the user gave a URL, use it.
   - If the user named a project, infer the URL from context
     (check for CNAME, vercel.json, railway config, env files).
   - If ambiguous, ask.

2. Run verification:
   - `curl -sI <url>` for HTTP status and headers.
   - Check for 200 OK (or 301/302 if redirect is expected).
   - Check response time from headers.
   - If it is a Django app, try `<url>/admin/` as a smoke test.
   - If it is a Next.js app, check that the page returns HTML
     (not a build error page).

3. Report:
   - Status code
   - Response time
   - Any error signals (5xx, timeout, connection refused)
   - Whether the deployment appears healthy or needs attention

4. If the deployment is not responding, suggest debugging steps:
   - Check the deploy logs (Vercel dashboard, `railway logs`)
   - Check for environment variable issues
   - Check for build failures
