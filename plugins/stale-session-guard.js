import { existsSync, mkdirSync, statSync, unlinkSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";

const IDLE_MS = Number(process.env.OPENCODE_STALE_GUARD_IDLE_MS) || 60 * 60 * 1000;
const MIN_CONTEXT = Number(process.env.OPENCODE_STALE_GUARD_MIN_CTX) || 50000;
const MARKER_TTL_MS = 30 * 60 * 1000;
const STATE_DIR = path.join(os.tmpdir(), "opencode-stale-guard");

export const StaleSessionGuard = async ({ client }) => ({
  "chat.message": async (input, output) => {
    let hours = 0;
    let context = 0;
    let sessionID = "";

    try {
      if (process.env.OPENCODE_STALE_GUARD === "0") return;
      if (
        (output?.parts ?? []).some(
          (part) => typeof part.text === "string" && part.text.startsWith("[stale-session-guard]"),
        )
      ) {
        return;
      }
      sessionID = input.sessionID;
      const { data } = await client.session.get({ path: { id: sessionID } });
      if (!data || data.parentID) return;
      const idle = Date.now() - (data.time?.updated ?? 0);
      const ctx = (data.tokens?.input ?? 0) + (data.tokens?.cache?.read ?? 0);
      if (!(idle >= IDLE_MS && ctx >= MIN_CONTEXT)) return;
      hours = idle / 3600000;
      context = ctx;

      const marker = path.join(STATE_DIR, sessionID);
      if (existsSync(marker) && Date.now() - statSync(marker).mtimeMs < MARKER_TTL_MS) {
        unlinkSync(marker);
        return;
      }
    } catch {
      return;
    }

    let userText = "";
    try {
      userText = (output?.parts ?? [])
        .filter((part) => part.type === "text" && typeof part.text === "string")
        .map((part) => part.text)
        .join("\n");
    } catch {
      userText = "";
    }

    const note = `[stale-session-guard] Blocked before sending. Session idle ${hours.toFixed(1)}h with ${Math.round(context / 1000)}k context. Resending runs a cold cache read at full input price. Resend to proceed, or start fresh from the handoff.`;

    try {
      await client.tui.showToast({
        body: { title: "Stale session", message: note, variant: "warning", duration: 8000 },
      });
    } catch {}

    try {
      if (userText) await client.tui.appendPrompt({ body: { text: userText } });
    } catch {}

    try {
      await client.session.promptAsync({
        path: { id: sessionID },
        body: { noReply: true, parts: [{ type: "text", text: note }] },
      });
    } catch {}

    try {
      mkdirSync(STATE_DIR, { recursive: true });
      writeFileSync(path.join(STATE_DIR, sessionID), String(Date.now()));
    } catch {}

    throw new Error("STALE_SESSION_GUARD");
  },
});
