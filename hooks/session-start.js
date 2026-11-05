#!/usr/bin/env node
// Verbatim - SessionStart hook.
// Prints the always-on project rules + a one-line status when the current
// folder is a Verbatim research project. Silent outside one.
// Never fails the session: it always exits 0, whatever happens here.

const { spawnSync } = require("node:child_process");
const path = require("node:path");

const script = path.join(__dirname, "..", "skills", "vault", "scripts", "verbatim.py");
const interpreters = process.platform === "win32"
  ? ["python", "py", "python3"]
  : ["python3", "python"];

for (const exe of interpreters) {
  let run;
  try {
    run = spawnSync(exe, [script, "session-context"], {
      encoding: "utf8",
      timeout: 10000,
      windowsHide: true,
    });
  } catch {
    continue;
  }
  if (!run || run.error || run.status !== 0) continue;
  if (run.stdout && run.stdout.trim()) process.stdout.write(run.stdout);
  break;
}

process.exit(0);
