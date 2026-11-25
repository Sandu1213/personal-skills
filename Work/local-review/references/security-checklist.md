# Security checklist

Reached from the “Inputs and trust boundaries” row of the hotspot sweep whenever step 2 lists a non-empty **attack surface** for a `required` unit. Check every class below against every attack-surface item it can reach; group items that one guard settles.

| Class | Every reachable item keeps |
| --- | --- |
| Injection | SQL, JPQL or native queries, shell commands, templates, headers, log lines, and file paths built from input go through parameters, allowlists, or escaping, never string concatenation |
| Output encoding (XSS) | input rendered as HTML, markdown, or rich text is escaped or sanitized; raw-HTML sinks (`dangerouslySetInnerHTML`, WebView HTML, markdown with HTML enabled) receive sanitized content only |
| Authentication | every protected operation, webhook, and internal callback verifies the caller (session or token, signature, shared secret) before acting |
| Authorization (IDOR) | every operation taking an object id checks that the caller may access that object and its tenant, not only that the caller is signed in; request bodies cannot set ownership, role, price, or entitlement fields |
| CSRF | every state-changing route reachable with cookie authentication verifies a CSRF token or the request's `Origin`, or accepts only non-simple requests (a required custom header or an enforced JSON content type) under a restrictive CORS policy; `SameSite` is defense in depth, never the guard by itself (`SameSite=None` offers none) |
| Race (TOCTOU) | read-then-write on a shared record holds a lock, a unique constraint, or a conditional update that covers the shared invariant on every write path; an idempotency key only deduplicates replays of one request |
| Session | tokens expire and are revoked on logout and credential change; no fixation; cookies carry Secure, HttpOnly, and SameSite |
| Cryptography and secrets | tokens and capability ids (share links, invite and reset codes) come from a secure random source; algorithms are current; signatures and tokens compare in constant time; secrets stay out of code, logs, client bundles, and error responses |
| Information disclosure | error responses carry no stack traces or internals; logs carry no secrets, tokens, or personal data (emails, names, audio, transcripts) beyond what the logging policy allows; where ids are guessable, responses do not reveal whether another user's object exists; presigned URLs are short-lived and scoped to one object |
| Outbound requests | URLs built from input are allowlisted (SSRF); TLS verification stays on; every call has a timeout |
| Redirects and navigation | redirect targets and deep-link or in-app navigation destinations taken from input are relative or allowlisted (open redirect) |
| Denial of service | loops, queries, pagination, uploads, recursion, and batch sizes are bounded; expensive operations are rate-limited; retries back off |
| Business logic | state machines reject illegal transitions; arithmetic on amounts, durations, and counts cannot overflow or lose precision; quotas and entitlements hold under retries, parallel requests, and client-supplied values |

Report one line per class: `clean` with the guard and its location, `finding` with the finding id, or `n/a` with the reason no item can reach it. A class whose guard the change leaves untouched cites that guard once without re-auditing its internals; its coverage of every new item is still checked. A class marked clean without a named guard is unchecked, and an unchecked class is an unchecked cell of the sweep. With no attack surface in a `required` unit, say so and list no classes.

Name the CWE on a confirmed security finding when one fits (CWE-639 for IDOR, CWE-89 for SQL injection, CWE-532 for personal data in logs); it names the defect class the sibling sweep searches for.
