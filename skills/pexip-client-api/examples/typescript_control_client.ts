/**
 * Pexip Infinity Client API — control-only client (no media).
 *
 * Mirrors examples/python_control_client.py:
 *   - request_token state machine (PIN, IDP, conference-extension, display-name prompts);
 *   - background token refresh on a ~expires/2 cadence;
 *   - typed wrappers for the most common conference and participant actions;
 *   - clean release on shutdown.
 *
 * Requires Node 20+ (or any runtime with global fetch + AbortController).
 * Zero dependencies.
 */

type PromptKind = "pin" | "choose_idp" | "complete_idp" | "conference_extension" | "display_name";
type PromptHandler = (kind: PromptKind, serverInfo: unknown) => Promise<string>;

export interface Session {
  node: string;
  alias: string;
  base: string;
  token: string;
  expires: number;
  participantUuid: string;
  role: "HOST" | "GUEST";
  directMedia: boolean;
  currentServiceType: string;
  raw: Record<string, unknown>;
}

export class PexipError extends Error {
  constructor(public readonly where: string, public readonly body: unknown) {
    super(`${where}: ${JSON.stringify(body)}`);
  }
}

function encodeAlias(alias: string): string {
  return encodeURIComponent(alias);
}

function buildBase(node: string, alias: string): string {
  return `${node.replace(/\/$/, "")}/api/client/v2/conferences/${encodeAlias(alias)}`;
}

// ---------------------------------------------------------------------------
// Low-level request
// ---------------------------------------------------------------------------

async function callApi<T = unknown>(
  url: string,
  init: RequestInit & { token?: string } = {},
): Promise<{ status: string; result: T }> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (init.token) headers.token = init.token;

  const r = await fetch(url, {
    method: init.method ?? "POST",
    headers,
    body: init.body ?? JSON.stringify({}),
    signal: init.signal,
  });
  if (r.status === 503) throw new PexipError(`${init.method ?? "POST"} ${url}`, { status: 503, body: await r.text() });
  const text = await r.text();
  let body: { status: string; result: T };
  try {
    body = text ? JSON.parse(text) : ({ status: "failure", result: "empty body" as unknown as T });
  } catch {
    throw new PexipError(`${init.method ?? "POST"} ${url}`, `non-JSON body: ${text}`);
  }
  if (!body || typeof body !== "object" || !("status" in body)) {
    throw new PexipError(`${init.method ?? "POST"} ${url}`, `missing envelope: ${text}`);
  }
  return body;
}

// ---------------------------------------------------------------------------
// Token state machine
// ---------------------------------------------------------------------------

export async function requestToken(
  node: string,
  alias: string,
  displayName: string,
  prompts: {
    pin?: PromptHandler;
    sso?: PromptHandler;
    extension?: PromptHandler;
    name?: PromptHandler;
  } = {},
): Promise<Session> {
  const base = buildBase(node, alias);
  const body: Record<string, unknown> = { display_name: displayName };

  for (let i = 0; i < 8; i++) {
    const r = await callApi<unknown>(`${base}/request_token`, { body: JSON.stringify(body) });
    const result = r.result as Record<string, unknown>;

    if (typeof result === "object" && result && "token" in result) {
      return {
        node,
        alias,
        base,
        token: String(result.token),
        expires: parseInt(String(result.expires ?? "120"), 10),
        participantUuid: String(result.participant_uuid ?? ""),
        role: (String(result.role ?? "GUEST").toUpperCase()) as "HOST" | "GUEST",
        directMedia: Boolean(result.direct_media),
        currentServiceType: String(result.current_service_type ?? "conference"),
        raw: result,
      };
    }

    if (result && result.pin === "required") {
      if (!prompts.pin) throw new PexipError("request_token", "PIN required, no pin prompt");
      body.pin = await prompts.pin("pin", result);
      continue;
    }
    if (result && Array.isArray(result.idp)) {
      if (!prompts.sso) throw new PexipError("request_token", "IDP required, no sso prompt");
      body.chosen_idp = await prompts.sso("choose_idp", result.idp);
      continue;
    }
    if (result && "redirect_url" in result) {
      if (!prompts.sso) throw new PexipError("request_token", "IDP redirect, no sso prompt");
      body.sso_token = await prompts.sso("complete_idp", result);
      continue;
    }
    if (result && "conference_extension" in result) {
      if (!prompts.extension) throw new PexipError("request_token", "conference_extension required");
      body.conference_extension = await prompts.extension("conference_extension", result);
      continue;
    }
    if (result && result.display_name === "required") {
      if (!prompts.name) throw new PexipError("request_token", "display_name required");
      body.display_name = await prompts.name("display_name", result);
      continue;
    }

    throw new PexipError("request_token", r);
  }
  throw new PexipError("request_token", "exceeded prompt iteration cap");
}

export async function refreshToken(sess: Session): Promise<void> {
  const r = await callApi<{ token: string; expires: string }>(
    `${sess.base}/refresh_token`,
    { token: sess.token },
  );
  if (r.status !== "success") throw new PexipError("refresh_token", r);
  sess.token = r.result.token;
  sess.expires = parseInt(r.result.expires, 10) || sess.expires;
}

export async function releaseToken(sess: Session): Promise<void> {
  try {
    await callApi(`${sess.base}/release_token`, { token: sess.token });
  } catch {
    // best-effort
  }
}

// ---------------------------------------------------------------------------
// Background refresher
// ---------------------------------------------------------------------------

export function startAutoRefresh(sess: Session, signal: AbortSignal): void {
  const tick = async () => {
    while (!signal.aborted) {
      await new Promise<void>((resolve) => {
        const t = setTimeout(resolve, Math.max((sess.expires / 2) * 1000, 15_000));
        signal.addEventListener("abort", () => { clearTimeout(t); resolve(); }, { once: true });
      });
      if (signal.aborted) return;
      try {
        await refreshToken(sess);
      } catch (e) {
        // Surface failures but keep trying; production code should bubble via an emitter.
        console.warn("refresh_token failed:", e);
      }
    }
  };
  void tick();
}

// ---------------------------------------------------------------------------
// Typed wrappers
// ---------------------------------------------------------------------------

async function post<T = unknown>(sess: Session, path: string, body: unknown = {}): Promise<T> {
  const r = await callApi<T>(`${sess.base}/${path}`, { token: sess.token, body: JSON.stringify(body) });
  if (r.status !== "success") throw new PexipError(path, r);
  return r.result;
}

async function get<T = unknown>(sess: Session, path: string): Promise<T> {
  const r = await callApi<T>(`${sess.base}/${path}`, { method: "GET", token: sess.token });
  if (r.status !== "success") throw new PexipError(path, r);
  return r.result;
}

// Conference-level
export const conferenceStatus  = (s: Session) => get(s, "conference_status");
export const participants      = (s: Session) => get<unknown[]>(s, "participants");
export const lock              = (s: Session) => post(s, "lock");
export const unlock            = (s: Session) => post(s, "unlock");
export const muteGuests        = (s: Session) => post(s, "muteguests");
export const unmuteGuests      = (s: Session) => post(s, "unmuteguests");
export const sendMessage       = (s: Session, text: string) => post(s, "message", { type: "text/plain", payload: text });
export const setBanner         = (s: Session, text: string) => post(s, "set_message_text", { text });
export const transformLayout   = (s: Session, transforms: Record<string, unknown>) =>
  post(s, "transform_layout", { transforms });

export interface DialOptions {
  role?: "GUEST" | "HOST";
  protocol?: "sip" | "h323" | "rtmp" | "mssip" | "auto";
  call_type?: "video" | "video-only" | "audio";
  source_display_name?: string;
  remote_display_name?: string;
  [extra: string]: unknown;
}
export const dial = (s: Session, destination: string, opts: DialOptions = {}) =>
  post<string[]>(s, "dial", { destination, role: "GUEST", protocol: "auto", call_type: "video", ...opts });

// Participant-level
export const participantMute     = (s: Session, uuid: string) => post(s, `participants/${uuid}/mute`);
export const participantUnmute   = (s: Session, uuid: string) => post(s, `participants/${uuid}/unmute`);
export const participantKick     = (s: Session, uuid: string) => post(s, `participants/${uuid}/disconnect`);
export const participantAdmit    = (s: Session, uuid: string) => post(s, `participants/${uuid}/unlock`);
export const participantRole     = (s: Session, uuid: string, role: "chair" | "guest") =>
  post(s, `participants/${uuid}/role`, { role });
export const participantTransfer = (
  s: Session, uuid: string, destAlias: string,
  opts: { role?: "host" | "guest"; pin?: string } = {},
) => post(s, `participants/${uuid}/transfer`, { conference_alias: destAlias, role: "guest", ...opts });

// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

async function demo() {
  const NODE  = "https://conf.example.com";
  const ALIAS = "ops_room";

  const ac = new AbortController();
  process.on("SIGINT",  () => ac.abort());
  process.on("SIGTERM", () => ac.abort());

  const sess = await requestToken(NODE, ALIAS, "Ops Bot", {
    pin: async () => "1234",
  });

  startAutoRefresh(sess, ac.signal);

  try {
    if (sess.role !== "HOST") {
      console.warn(`joined as ${sess.role} — most control actions will fail`);
    }

    console.log("conference state:", await conferenceStatus(sess));
    await lock(sess);
    await muteGuests(sess);
    await setBanner(sess, "Meeting in progress — please be respectful");

    const roster = await participants(sess);
    console.log(`${roster.length} participant(s) currently in room`);

    // Do work …
  } finally {
    ac.abort();
    await releaseToken(sess);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  demo().catch((err) => { console.error(err); process.exit(1); });
}
