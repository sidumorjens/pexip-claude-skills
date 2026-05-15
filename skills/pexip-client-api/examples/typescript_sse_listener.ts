/**
 * Pexip Infinity Client API — SSE listener with reconnect (TypeScript / Node 20+).
 *
 * Mirrors examples/python_sse_listener.py:
 *   - reuses requestToken/refreshToken from typescript_control_client.ts;
 *   - parses SSE manually (no library) from a streamed fetch response;
 *   - tracks the participant_sync_begin/_end bracket and maintains a roster;
 *   - watchdog timeout (closes idle connections), exponential backoff on reconnect;
 *   - 401 → re-auth path via a caller-supplied onReauth callback.
 *
 * Zero dependencies. Works in any runtime with global fetch + AbortController +
 * ReadableStream (Node 20+, Deno, modern browsers — browsers can also use the
 * built-in `EventSource` for a simpler path).
 */

import {
  PexipError,
  refreshToken,
  releaseToken,
  requestToken,
  type Session,
} from "./typescript_control_client";

export type EventHandler = (eventName: string, data: unknown) => void | Promise<void>;

const WATCHDOG_MS    = 90_000;
const BACKOFF_INIT_MS = 1_000;
const BACKOFF_MAX_MS  = 30_000;


// ---------------------------------------------------------------------------
// SSE parser — streams chunks → emits { event, data } records.
// Handles multi-line `data:`, comment lines starting with `:`, and CRLF.
// ---------------------------------------------------------------------------

async function* parseSse(stream: ReadableStream<Uint8Array>): AsyncGenerator<{ event: string; data: string }> {
  const reader = stream.getReader();
  const decoder = new TextDecoder("utf-8");
  let buf = "";
  let event = "message";
  let dataLines: string[] = [];

  const flush = (): { event: string; data: string } | null => {
    if (!event && dataLines.length === 0) return null;
    const out = { event, data: dataLines.join("\n") };
    event = "message";
    dataLines = [];
    return out;
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      const last = flush();
      if (last) yield last;
      return;
    }
    buf += decoder.decode(value, { stream: true });

    let nl: number;
    while ((nl = buf.indexOf("\n")) !== -1) {
      let line = buf.slice(0, nl);
      buf = buf.slice(nl + 1);
      if (line.endsWith("\r")) line = line.slice(0, -1);

      if (line === "") {
        const out = flush();
        if (out) yield out;
        continue;
      }
      if (line.startsWith(":")) continue;            // comment / heartbeat

      const colon = line.indexOf(":");
      const field = colon === -1 ? line : line.slice(0, colon);
      let value2  = colon === -1 ? "" : line.slice(colon + 1);
      if (value2.startsWith(" ")) value2 = value2.slice(1);

      if (field === "event") event = value2;
      else if (field === "data") dataLines.push(value2);
      // ignore id / retry
    }
  }
}


// ---------------------------------------------------------------------------
// Roster tracker
// ---------------------------------------------------------------------------

export class Roster {
  participants = new Map<string, Record<string, unknown>>();
  private inSync = false;
  private seen = new Set<string>();

  beginSync(): void { this.inSync = true; this.seen.clear(); }
  endSync(): void {
    for (const uuid of [...this.participants.keys()]) {
      if (!this.seen.has(uuid)) this.participants.delete(uuid);
    }
    this.inSync = false;
  }
  upsert(p: Record<string, unknown> | undefined | null): void {
    if (!p || typeof p.uuid !== "string") return;
    this.participants.set(p.uuid, p);
    if (this.inSync) this.seen.add(p.uuid);
  }
  delete(uuid: string): void { this.participants.delete(uuid); }
}


// ---------------------------------------------------------------------------
// SSE consumer with reconnect + watchdog
// ---------------------------------------------------------------------------

export async function consumeEvents(
  sess: Session,
  handle: EventHandler,
  opts: {
    roster?: Roster;
    signal: AbortSignal;
    onReauth?: () => Promise<Session>;
  },
): Promise<void> {
  let backoff = BACKOFF_INIT_MS;
  const { signal } = opts;

  while (!signal.aborted) {
    const url = `${sess.base}/events?token=${encodeURIComponent(sess.token)}`;
    const innerAc = new AbortController();
    const stopOnAbort = () => innerAc.abort();
    signal.addEventListener("abort", stopOnAbort, { once: true });

    let lastByte = Date.now();
    const watchdog = setInterval(() => {
      if (Date.now() - lastByte > WATCHDOG_MS) {
        console.warn(`SSE watchdog: no data for ${WATCHDOG_MS}ms, dropping`);
        innerAc.abort();
      }
    }, 5_000);

    try {
      console.log(`SSE connecting to ${sess.base}`);
      const r = await fetch(url, {
        method: "GET",
        headers: { Accept: "text/event-stream" },
        signal: innerAc.signal,
      });
      if (r.status === 401) {
        console.warn("SSE returned 401 — re-authenticating");
        if (!opts.onReauth) throw new PexipError("events", "401 and no onReauth");
        sess = await opts.onReauth();
        continue;
      }
      if (!r.ok || !r.body) {
        throw new PexipError("events", `HTTP ${r.status}`);
      }
      backoff = BACKOFF_INIT_MS;
      console.log("SSE connected");

      for await (const { event, data } of parseSse(r.body)) {
        lastByte = Date.now();
        let payload: unknown = null;
        if (data && data !== "null") {
          try { payload = JSON.parse(data); }
          catch { console.warn(`non-JSON SSE payload for ${event}:`, data); }
        }
        if (opts.roster && payload && typeof payload === "object") {
          if (event === "participant_sync_begin") opts.roster.beginSync();
          else if (event === "participant_sync_end") opts.roster.endSync();
          else if (event === "participant_create" || event === "participant_update") {
            opts.roster.upsert(payload as Record<string, unknown>);
          } else if (event === "participant_delete") {
            const u = (payload as { uuid?: unknown }).uuid;
            if (typeof u === "string") opts.roster.delete(u);
          }
        } else if (opts.roster && (event === "participant_sync_begin" || event === "participant_sync_end")) {
          if (event === "participant_sync_begin") opts.roster.beginSync();
          else opts.roster.endSync();
        }
        await handle(event, payload);
      }
    } catch (err) {
      if (signal.aborted) break;
      console.warn(`SSE error; reconnecting in ${backoff}ms:`, err);
      await new Promise((r) => setTimeout(r, backoff));
      backoff = Math.min(backoff * 2, BACKOFF_MAX_MS);
    } finally {
      signal.removeEventListener("abort", stopOnAbort);
      clearInterval(watchdog);
    }
  }
}


// ---------------------------------------------------------------------------
// Default dispatcher with per-event handlers
// ---------------------------------------------------------------------------

const handlers: Record<string, EventHandler> = {
  participant_create: (_n, p: any) =>
    void console.log(`+ participant: uuid=${p?.uuid} name=${p?.display_name} role=${p?.role}`),
  participant_delete: (_n, p: any) =>
    void console.log(`- participant: uuid=${p?.uuid}`),
  conference_update: (_n, c: any) => {
    if (!c) return;
    console.log(`conference state: locked=${c.locked} muted=${c.guests_muted} `
              + `started=${c.started} recording=${c.recording} streaming=${c.streaming}`);
  },
  disconnect: (_n, d: any) =>
    void console.warn(`Pexip disconnecting us: ${d?.reason}`),
  refer: (_n, d: any) =>
    void console.warn(`refer → alias=${d?.alias} breakout=${d?.breakout_name}`),
  message_received: (_n, m: any) => {
    if (!m) return;
    const arrow = m.direct ? "→" : "⇒";
    console.log(`chat ${m.origin} ${arrow} [${m.type}]: ${m.payload}`);
  },
};

export const defaultHandler: EventHandler = async (event, data) => {
  const fn = handlers[event];
  if (fn) await fn(event, data);
};


// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

async function demo() {
  const NODE  = "https://conf.example.com";
  const ALIAS = "ops_room";

  const ac = new AbortController();
  process.on("SIGINT",  () => ac.abort());
  process.on("SIGTERM", () => ac.abort());

  const sess = await requestToken(NODE, ALIAS, "Monitor Bot");
  const roster = new Roster();

  // Independent refresh loop.
  (async () => {
    while (!ac.signal.aborted) {
      await new Promise((r) => setTimeout(r, Math.max((sess.expires / 2) * 1000, 15_000)));
      if (ac.signal.aborted) return;
      try { await refreshToken(sess); }
      catch (e) { console.warn("refresh failed:", e); }
    }
  })();

  try {
    await consumeEvents(sess, defaultHandler, {
      roster,
      signal: ac.signal,
      onReauth: () => requestToken(NODE, ALIAS, "Monitor Bot"),
    });
  } finally {
    await releaseToken(sess);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  demo().catch((err) => { console.error(err); process.exit(1); });
}
