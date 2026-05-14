# Case Study: Building an Entra Avatar Policy Server with the `pexip-external-policy` Skill

A walkthrough of how the `pexip-external-policy` skill shaped a small, production-style
external policy server that serves participant avatars out of Microsoft Entra ID.

The finished server lives in this repo: [app.py](app.py), [entra.py](entra.py),
[.env.example](.env.example), [requirements.txt](requirements.txt).

---

## The ask

> "Create a quick external policy for participant avatar requests. Resolve the alias in
> the request to a UPN that can be used to look up the user in Microsoft Entra (i.e.
> `sip:user@domain.com` should resolve to `user@domain.com`). Store the Entra API
> credentials in a `.env` file. The OAuth2 token for Entra should be managed, and there
> should be a configurable cache period for the photos in `.env`."

Deliberately narrow: only the **participant avatar** policy endpoint, all other request
types out of scope.

---

## How the skill drove the design

The skill is structured as a SKILL.md plus per-request-type reference files. Each
section below shows what the skill told us, and what made it into the code as a result.

### 1. Picked the right reference file from the decision tree

The skill's "Quick Decision Tree" maps goals to a primary reference file:

> | Goal | Read this first |
> |---|---|
> | Serve participant or directory avatar images (JPEG) | `references/participant-avatar.md` |

That single line told us where the authoritative request/response spec for the avatar
endpoint lives. No guessing about the URL path, no inventing parameter names.

### 2. Locked in the contract from `participant-avatar.md`

The reference file gave us the hard requirements we had to honor exactly:

- **URL:** `GET /policy/v1/participant/avatar/<alias>` — alias is a **path segment**
  (may contain `@`, `:`, `;`). → FastAPI `{alias:path}` converter in [app.py](app.py).
- **Response Content-Type:** `image/jpeg` (the *only* policy endpoint that is not JSON).
- **Color space:** RGB or RGBA only. **CMYK is rejected.** → Pillow `convert("RGB")`
  before saving.
- **Dimensions:** the JPEG must match the `width`/`height` query params **exactly**, or
  Pexip returns 404 to the client. → Resize with `Image.Resampling.LANCZOS`.
- **Fallback:** if there's no photo, return HTTP `404` — *do not* invent a blank JPEG.

The skill also pre-warned about a subtlety we'd otherwise hit later:

> SIP aliases include `sip:`; SfB may include `sip:` or have `;tag=`; WebRTC aliases
> often don't.

Our `alias_to_upn()` in [app.py](app.py) handles all three: strip URI scheme, drop SIP
URI parameters, lowercase the result.

### 3. Took the FastAPI skeleton from SKILL.md §4 and trimmed it

SKILL.md §4 ships a six-endpoint FastAPI skeleton with Basic Auth via
`secrets.compare_digest`. We kept only the `/health` and avatar endpoints (other request
types stay disabled on the Pexip Policy Profile and fall back to Pexip's DB, per the
skill's guidance).

Auth pattern came verbatim from the skill:

```python
def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    ok = (secrets.compare_digest(credentials.username, POLICY_USER)
          and secrets.compare_digest(credentials.password, POLICY_PASS))
    if not ok:
        raise HTTPException(401, headers={"WWW-Authenticate": "Basic"})
```

### 4. Used the worked Graph example, but hardened it

`participant-avatar.md` includes a "Microsoft Graph / Entra ID Avatar Proxy" worked
example. Excellent starting point, but the skill explicitly nudges past it with these
production tips at the bottom of the same file:

> 1. **Cache aggressively.** Same alias is requested many times; cache by
>    `(alias, width, height)`.
> 2. **Cache photo bytes too.** Don't hit the upstream on every request.
> 3. **Use Lanczos for resizing** — Pillow's default `BILINEAR` looks rough at small sizes.
> 5. **Bound the upstream call** with a tight timeout (1-2s) — the 5s Pexip budget is
>    shared with your lookup.

We took all of those and went one step further because the user explicitly asked for it:

- **OAuth2 token** is cached with a 60-second pre-expiry refresh buffer, protected by an
  `asyncio.Lock` (single-flight) and retried once on a Graph 401.
- **Photos** are cached by **UPN** (not `(alias, width, height)` — we cache the raw
  bytes from Graph and resize per request, since resizing is cheap and Pexip varies the
  requested size). TTL is configurable via `PHOTO_CACHE_TTL`.
- **Negative caching:** "this UPN has no photo" is cached for the same TTL, so unknown
  users don't hammer Graph.
- **Per-UPN `asyncio.Lock`** prevents duplicate Graph calls when the same UPN is
  requested concurrently during a cold start.
- **httpx timeout** set to 4.0s (connect 1.5s) — well inside the skill's stated 5s
  Pexip budget.

### 5. Honored the skill's hard limits

The skill's §1 "Transport & Auth" section lists constraints that *don't* show up in
Pexip's UI and would be easy to miss. Things we kept in mind even though they didn't
all surface in code:

- 5-second total timeout → tight `httpx` timeouts, in-memory caches.
- No 301/302 redirects from Pexip → if HTTPS-terminating in front of uvicorn, the proxy
  must not redirect.
- 250-char field limit → not applicable here (avatar responses are bytes, not JSON), but
  worth noting in the README.

### 6. Pre-flight checklist from SKILL.md §10

We ran our finished server against the checklist:

- ✅ Avatar endpoint returns `Content-Type: image/jpeg`
- ✅ HTTP Basic Auth validated on every request
- ✅ `/health` endpoint returns 200
- ✅ All decisions complete within 5 seconds (cache + tight timeout)
- ✅ Logging captures alias, resolved UPN, requested size, cache outcome
- ✅ Tested with curl against the endpoint before connecting Pexip
- ⏭️ HTTPS in production — left to the reverse proxy in front of uvicorn (documented in
  the README rather than baked in)
- ⏭️ Other five endpoints — intentionally disabled at the Policy Profile

---

## What the skill *didn't* have to tell us — but did anyway

A couple of things in [entra.py](entra.py) came from the skill's general "implementing
a policy server" mindset rather than from the avatar-specific reference:

- **Use the Management API for things external policy cannot do.** Not relevant for
  avatars, but the skill's §6 table set the right expectation: the avatar endpoint is a
  *read* path, not a control path. We didn't try to overload it with side effects.
- **Debugging silent failures** (§8). The first time the server returned a JPEG that
  wasn't the requested size, Pexip would silently 404 to the client. The skill's table
  of silent-failure modes told us exactly where to look.

---

## Resulting shape

```
app.py             FastAPI app + avatar endpoint + alias→UPN resolution
entra.py           OAuth2 token cache + Graph photo client + photo cache
requirements.txt   fastapi, uvicorn, httpx, pillow, python-dotenv
.env.example       POLICY_*, ENTRA_*, PHOTO_CACHE_TTL, LOG_LEVEL
.gitignore
README.md          User-facing documentation
CASE_STUDY.md      This file
```

Lines of code: ~180 total across `app.py` + `entra.py`. The skill let us stay narrow:
no scaffolding for the other five request types, no premature abstraction, no
bespoke retry frameworks — just the avatar endpoint, hardened to the constraints the
skill called out, in the form the skill's worked example suggested.

---

## Time-to-working

A reasonable estimate, end to end:

1. Reading the skill's decision tree + `participant-avatar.md` — a few minutes.
2. Scaffolding `app.py` from SKILL.md §4 and trimming — small.
3. Writing the Entra OAuth2 + photo cache module — the largest single chunk, because the
   skill points at *what* to cache but not at the token-refresh details (that's standard
   client-credentials boilerplate).
4. Wiring `.env` and Pillow resize — quick.

Without the skill, the most likely traps would have been:

- Returning JSON from the avatar endpoint (every other policy endpoint does), causing
  Pexip to silently serve placeholders.
- Skipping the CMYK → RGB conversion and getting silent 404s from Pexip on a subset of
  user photos.
- Not stripping `sip:` / `;tag=` from the alias and 404'ing on every SIP caller.
- Not bounding the upstream Graph call and blowing the 5s policy budget on the first
  slow Graph response.

All four are flagged explicitly in the skill — which is the point of having it.
