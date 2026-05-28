---
name: cowork-to-code-bridge-setup
description: Walk the user through installing the cowork-to-code-bridge so Cowork can run commands on their Mac. Triggers when the user pastes the bridge GitHub URL, asks to "install the bridge", or says "set up cowork bridge" / "connect Cowork to my Mac".
---

# Setup skill — cowork-to-code-bridge

You are walking the user through a **one-paste-and-go install**. The user has done one thing: pasted a URL or said "install the bridge". You drive the rest.

## Your job in one sentence

Get the Mac daemon installed and verified working, with the user running **exactly one terminal command** of their own.

## Step 1 — probe for existing install

Before asking the user to do anything, check if the daemon is already set up. Use the bridge client to call the ping script:

```python
from cowork_to_code_bridge import call_remote, daemon_alive
if daemon_alive(ping_timeout=5):
    print("Bridge is already configured and live.")
```

If `daemon_alive()` returns `True`, **skip to Step 5 (verify + ready)**. Don't put the user through setup they don't need.

If it returns `False` or raises, the daemon is missing or unreachable. Continue to Step 2.

## Step 2 — show the user the install command

Tell the user this, verbatim, in a code block:

> I need you to run **one command** on your Mac terminal (not in Cowork — open Terminal.app or iTerm on your Mac).
>
> Copy this and paste it into your Mac terminal:
>
> ```bash
> curl -fsSL https://raw.githubusercontent.com/abhinaykrupa/cowork-to-code-bridge/main/install.sh | bash
> ```
>
> It takes about 30 seconds. It will:
> - Install the bridge Python package
> - Create `~/.cowork-to-code-bridge/` on your Mac
> - Generate a security token
> - Start a background daemon that auto-restarts on login
>
> Tell me when it finishes, or paste any error you see.

## Step 3 — wait for user confirmation

Accept variants: "done", "finished", "ok", "ran it", "installed", "complete", "✓", or any short affirmative. Also handle:

- **User pastes the install.sh output** → confirm it looks successful (look for the "DONE. Bridge is installed and running." line) and proceed.
- **User pastes an error** → diagnose using Step 4.

## Step 4 — error recovery

Common failure modes and what to tell the user:

| Symptom in user's paste | Diagnosis | Tell the user |
|---|---|---|
| `command not found: python3` | No Python | "Install Python first: `brew install python@3.12`, then re-run the curl command." |
| `Python ... is too old` | Python < 3.10 | "Your Python is too old. Install 3.10+: `brew install python@3.12`, then re-run." |
| `pip: command not found` | No pip | "Run `python3 -m ensurepip --upgrade`, then re-run the curl command." |
| `Permission denied` writing `~/Library/LaunchAgents` | Filesystem perms | "Check that you own `~/Library/LaunchAgents` — `ls -ld ~/Library/LaunchAgents`. If it's missing, `mkdir -p ~/Library/LaunchAgents` and re-run." |
| `launchctl: ... already loaded` | Re-install | This is fine — installer handles it. Tell them to re-run; if still stuck, run `launchctl unload ~/Library/LaunchAgents/dev.cowork-to-code-bridge.daemon.plist` manually then re-run installer. |
| `daemon failed to register` | launchd refused the plist | Ask them to paste the tail of `~/.cowork-to-code-bridge/daemon.err`. |
| `curl: command not found` | No curl (rare on Mac) | Provide wget alternative: `wget -qO- https://... \| bash` or manual download. |
| Network timeout / DNS error | Connectivity | "Check your internet connection, then re-run." |

If the symptom doesn't match any of these, ask the user for:
1. The last 20 lines of installer output
2. Output of `which python3 && python3 --version`
3. Output of `ls ~/.cowork-to-code-bridge/` if the directory exists

## Step 5 — verify the bridge actually works

Do not declare success based on the user's word. Probe the bridge yourself:

```python
from cowork_to_code_bridge import daemon_alive
if daemon_alive(ping_timeout=10):
    # success
else:
    # the user thinks it worked but the daemon isn't responding
```

If the probe fails after the user reports success:

- Tell them: "The installer reported success but I can't reach the daemon. Check `launchctl list | grep cowork-to-code-bridge` on your Mac — it should show one line. If it doesn't, the daemon failed to start."
- Ask them to paste `tail -20 ~/.cowork-to-code-bridge/daemon.err`.

Common cause: the `BRIDGE_ROOT` directory isn't visible from inside this Cowork session because of how the bind-mount is structured. In that case ask the user what their project's bind-mount path looks like and try setting `BRIDGE_ROOT` explicitly.

## Step 6 — declare ready

Once `daemon_alive()` returns `True`, tell the user:

> ✓ Bridge is live. You can now ask me to run things on your Mac. Try:
>
> - "run `ls` on my Mac"
> - "git status on my AAQuant repo"
> - "run `pytest` on my project"
>
> I'll route those through the bridge automatically. The `run-on-mac` skill handles it from here.

## What not to do

- **Don't** try to install anything on the Mac yourself via shell commands. Your Cowork sandbox can't reach the user's Mac except through the bridge.
- **Don't** ask the user to read the README. The skill *is* the README from their perspective.
- **Don't** declare success based on the user saying "done". Always verify with `daemon_alive()`.
- **Don't** keep retrying silently. If something fails after 2 attempts, surface it to the user with a concrete diagnostic ask.

## State preservation

After successful setup, future Cowork sessions in the same project will find the daemon already alive on probe (Step 1) and jump straight to Step 6. No re-onboarding.
