#!/usr/bin/env python3
"""
run_project.py — Stack Orchestrator for Mobile Store AI Telegram Bot

Launches the full stack in dedicated Windows console windows:
  • Ngrok HTTPS tunnel  →  Telegram webhook auto-registration
  • Ollama engine        (only when provider = local)
  • FastAPI / Uvicorn   (via venv Python)
  • Odoo 17 server       (via Conda env, from source)

Usage:
    python run_project.py gemini
    python run_project.py local
    python run_project.py groq

Dependencies: Python standard library only.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants  (all paths use forward slashes — Path normalises on Windows)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
VENV_PYTHON = ROOT / "odoo_ai_env" / "Scripts" / "python.exe"

# Odoo 17 — Conda environment + source installation
ODOO_CONDA_PYTHON = Path("C:/Users/ahmed/.conda/envs/odoo17/python.exe")
ODOO_ROOT = Path("E:/Odoo_Devlopment/odoo17/odoo17")
ODOO_BIN = ODOO_ROOT / "odoo-bin"
ODOO_CONF = ODOO_ROOT / "odoo.conf"
ODOO_ADDONS = ODOO_ROOT / "addons"
ODOO_CUSTOM_ADDONS = ODOO_ROOT / "odoo" / "custom_addons"
ODOO_PROJECT_ADDONS = ROOT / "odoo" / "custom_module"
ODOO_UPDATE_MODULES = "app_one,hospital_management,mobile_store_ai"

NGROK_API = "http://127.0.0.1:4040/api/tunnels"
TELEGRAM_API = "https://api.telegram.org/bot"
WEBHOOK_PATH = "/api/telegram/webhook"            # must match FastAPI route

SUPPORTED_PROVIDERS = ("gemini", "local", "groq")

# Emoji / label helpers
INFO = "  \u2139\ufe0f  "
OK = "  \u2705  "
WARN = "  \u26a0\ufe0f  "
ERR = "  \u274c  "
ROCKET = "  \ud83d\ude80  "
NGROK_EMOJI = "  \ud83d\udd17  "
BOT = "  \ud83e\udd16  "
ODOO_EMOJI = "  \ud83c\udf10  "
GEAR = "  \u2699\ufe0f  "

NGROK_POLL_TIMEOUT = 15  # seconds

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("orchestrator")

# ---------------------------------------------------------------------------
# .env helpers  (zero-dependency read / write, preserves comments)
# ---------------------------------------------------------------------------

def _read_env() -> dict[str, str]:
    env: dict[str, str] = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip("\"'")
    return env


def _write_env(env: dict[str, str]) -> None:
    lines: list[str] = []
    written_keys: set[str] = set()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                lines.append(line)
                continue
            key = stripped.partition("=")[0].strip()
            if key in env:
                lines.append(f"{key}={env[key]}")
                written_keys.add(key)
            else:
                lines.append(line)
        for k, v in env.items():
            if k not in written_keys:
                lines.append(f"{k}={v}")
    else:
        for k, v in env.items():
            lines.append(f"{k}={v}")
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_env(key: str, default: str = "") -> str:
    return _read_env().get(key, default)


def set_env(key: str, value: str) -> None:
    env = _read_env()
    env[key] = value
    _write_env(env)


# ---------------------------------------------------------------------------
# Port check  (stdlib socket)
# ---------------------------------------------------------------------------

def port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


# ---------------------------------------------------------------------------
# HTTP helper  (stdlib urllib — no requests dependency)
# ---------------------------------------------------------------------------

def http_get(url: str, timeout: float = 5.0) -> Optional[dict]:
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Subprocess launcher  —  Windows ``start "title" cmd /k`` pattern
# ---------------------------------------------------------------------------

_procs: list[subprocess.Popen] = []


def launch_terminal(
    command: str,
    title: str,
    cwd: Optional[Path] = None,
) -> Optional[subprocess.Popen]:
    """
    Open a new, persistent Windows console window running *command*.

    Uses the native ``start "title" cmd /k …`` pattern so that:
      * A dedicated console window appears with *title* in its title bar.
      * The window stays open (``cmd /k``) after the command finishes,
        preserving error messages.
      * Paths containing spaces, underscores or backslashes are handled
        correctly via standard Windows quoting.
    """
    full_cmd = f'start "{title}" cmd /k {command}'

    try:
        proc = subprocess.Popen(
            full_cmd,
            shell=True,
            cwd=str(cwd or ROOT),
        )
        log.info("%s Launched [%s] — PID %d | %s", OK, title, proc.pid, command[:140])
        _procs.append(proc)
        return proc
    except FileNotFoundError:
        log.error("%s Executable not found for [%s]: %s", ERR, title, command.split()[0])
    except Exception as exc:
        log.error("%s Failed to launch [%s]: %s", ERR, title, exc)
    return None


# ---------------------------------------------------------------------------
# Step 2 — Odoo 17  (Conda env, source-code installation)
# ---------------------------------------------------------------------------

def launch_odoo() -> Optional[subprocess.Popen]:
    ODOO_PORT = 8069

    # Guard — port already occupied
    if port_in_use(ODOO_PORT):
        log.info("%s Port %d is occupied — Odoo is already running", OK, ODOO_PORT)
        return None

    # Guard — odoo-bin missing
    if not ODOO_BIN.is_file():
        log.error(
            "%s Odoo binary not found at %s\n"
            "%s  Verify Odoo source is cloned to E:/Odoo_Devlopment/odoo17/odoo17",
            ERR,
            ODOO_BIN,
            GEAR,
        )
        return None

    # Initialise command string to prevent any possible UnboundLocalError
    command = ""

    # Guard — Conda python missing
    if not ODOO_CONDA_PYTHON.is_file():
        log.error(
            "%s Conda Python not found at %s\n"
            "%s  Create the Conda environment: conda create -n odoo17 python=3.11",
            ERR,
            ODOO_CONDA_PYTHON,
            GEAR,
        )
        return None

    # Build addons path: source addons, source custom_addons, project custom_module
    addons_path = f"{ODOO_ADDONS},{ODOO_CUSTOM_ADDONS},{ODOO_PROJECT_ADDONS}"

    command = (
        f'"{ODOO_CONDA_PYTHON}" "{ODOO_BIN}"'
        f' -c "{ODOO_CONF}"'
        f' --addons-path="{addons_path}"'
        f' -u {ODOO_UPDATE_MODULES}'
    )

    log.info("%s Starting Odoo 17 on port %d …", ODOO_EMOJI, ODOO_PORT)
    return launch_terminal(command, "Odoo 17 Server", cwd=ODOO_ROOT)


# ---------------------------------------------------------------------------
# Step 3 — Ngrok tunnel  +  Telegram webhook registration
# ---------------------------------------------------------------------------

def launch_ngrok() -> Optional[subprocess.Popen]:
    log.info("%s Starting Ngrok HTTPS tunnel on port 8000 …", NGROK_EMOJI)
    return launch_terminal("ngrok http 8000", "Ngrok Tunnel")


def wait_for_ngrok_url(timeout: float = NGROK_POLL_TIMEOUT) -> Optional[str]:
    """
    Poll ``http://127.0.0.1:4040/api/tunnels`` every 500 ms until the
    tunnel is live, then return the public HTTPS URL.

    Returns *None* if the API is not reachable within *timeout* seconds.
    """
    log.info("%s Polling ngrok API for up to %.0f s …", GEAR, timeout)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        data = http_get(NGROK_API, timeout=2.0)
        if data:
            for t in data.get("tunnels", []):
                if t.get("proto") == "https" and t.get("public_url"):
                    url: str = t["public_url"]
                    log.info("%s Ngrok tunnel active → %s", OK, url)
                    return url
        time.sleep(0.5)

    log.error(
        "%s Ngrok API not reachable after %.0f s. "
        "Is ngrok installed / allowed through the firewall?",
        ERR,
        timeout,
    )
    return None


def register_webhook(ngrok_url: str) -> bool:
    token = get_env("TELEGRAM_BOT_TOKEN")
    if not token:
        log.warning(
            "%s TELEGRAM_BOT_TOKEN is empty in .env — webhook skipped",
            WARN,
        )
        return False

    # Strip any trailing slash from the ngrok URL before appending the path
    webhook_url = f"{ngrok_url.rstrip('/')}{WEBHOOK_PATH}"
    api_url = f"{TELEGRAM_API}{token}/setWebhook?url={webhook_url}"

    log.info("%s Registering Telegram webhook → %s", BOT, webhook_url)
    data = http_get(api_url, timeout=10.0)

    if data and data.get("ok") is True:
        log.info("%s Telegram webhook registered successfully", OK)
        return True

    desc = (data or {}).get("description", "unknown error") if data else "no response"
    log.error("%s Telegram webhook registration failed: %s", ERR, desc)
    return False


# ---------------------------------------------------------------------------
# Step 4 — Ollama  (local provider only)
# ---------------------------------------------------------------------------

def _ollama_running() -> bool:
    return port_in_use(11434, "127.0.0.1")


def launch_ollama() -> Optional[subprocess.Popen]:
    if _ollama_running():
        log.info("%s Ollama engine is already running on port 11434", OK)
        return None

    log.info("%s Launching Ollama with model qwen2.5:1.5b …", ROCKET)
    return launch_terminal("ollama run qwen2.5:1.5b", "Ollama Engine")


# ---------------------------------------------------------------------------
# Step 5 — FastAPI / Uvicorn
# ---------------------------------------------------------------------------

def launch_fastapi() -> Optional[subprocess.Popen]:
    if not VENV_PYTHON.is_file():
        log.error(
            "%s Virtual environment interpreter not found at %s\n"
            "%s  Run: python -m venv odoo_ai_env && pip install -r requirements.txt",
            ERR,
            VENV_PYTHON,
            GEAR,
        )
        return None

    command = (
        f'"{VENV_PYTHON}" -m uvicorn backend.main:app '
        f"--reload --host 0.0.0.0 --port 8000"
    )
    log.info("%s Launching FastAPI / Uvicorn on port 8000 …", ROCKET)
    return launch_terminal(command, "FastAPI Server")


# ---------------------------------------------------------------------------
# Pre-flight validation
# ---------------------------------------------------------------------------

def validate_environment() -> int:
    """Return number of non-fatal issues found (0 = clean)."""
    issues = 0

    if not ENV_FILE.exists():
        log.warning("%s .env file not found at %s", WARN, ENV_FILE)
        issues += 1

    if not get_env("TELEGRAM_BOT_TOKEN"):
        log.warning(
            "%s TELEGRAM_BOT_TOKEN missing — webhook auto-registration disabled",
            WARN,
        )
        issues += 1

    provider = get_env("MODEL_PROVIDER", "local").lower()
    if provider not in SUPPORTED_PROVIDERS:
        log.warning(
            "%s MODEL_PROVIDER=%s is not standard (supported: %s)",
            WARN,
            provider,
            ", ".join(SUPPORTED_PROVIDERS),
        )
        issues += 1

    if not VENV_PYTHON.is_file():
        log.warning("%s Virtual environment not found at %s", WARN, VENV_PYTHON)
        issues += 1

    if not ODOO_CONDA_PYTHON.is_file():
        log.warning(
            "%s Conda environment 'odoo17' not found at %s",
            WARN,
            ODOO_CONDA_PYTHON,
        )
        issues += 1

    ngrok_found = any(
        (Path(p) / "ngrok.exe").is_file()
        for p in os.environ.get("PATH", "").split(os.pathsep)
    )
    if not ngrok_found:
        log.warning("%s ngrok.exe not found in PATH — tunnel will not start", WARN)
        issues += 1

    return issues


# ---------------------------------------------------------------------------
# Clean-up  (best-effort — independent console windows are not children)
# ---------------------------------------------------------------------------

def _cleanup():
    for proc in _procs:
        if proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mobile Store AI \u2014 Full Stack Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python run_project.py gemini\n"
            "  python run_project.py local\n"
            "  python run_project.py groq\n"
        ),
    )
    parser.add_argument(
        "provider",
        nargs="?",
        default=None,
        help=f"Model provider: {', '.join(SUPPORTED_PROVIDERS)}",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Main  (sequential execution flow)
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    provider = (args.provider or get_env("MODEL_PROVIDER", "local")).lower()

    if provider not in SUPPORTED_PROVIDERS:
        print(
            f"{ERR} Unsupported provider '{provider}'. "
            f"Choose from: {', '.join(SUPPORTED_PROVIDERS)}"
        )
        return 1

    ngrok_url: Optional[str] = None

    # ==================================================================
    # Step 1 — Environment
    # ==================================================================
    print()
    log.info("%s%s%s", "=" * 52, " ENVIRONMENT ", "=" * 52)
    set_env("MODEL_PROVIDER", provider)
    log.info("%s MODEL_PROVIDER set to '%s' in %s", OK, provider, ENV_FILE.name)

    issues = validate_environment()
    if issues:
        log.warning(
            "%s Pre-flight checks found %d issue(s) \u2014 continuing",
            WARN,
            issues,
        )

    # ==================================================================
    # Step 2 — Odoo 17  (port-conditional)
    # ==================================================================
    print()
    log.info("%s%s%s", "=" * 52, " ODOO 17 ", "=" * 52)
    launch_odoo()

    # ==================================================================
    # Step 3 — Ngrok tunnel  \u2192  Telegram webhook
    # ==================================================================
    print()
    log.info("%s%s%s", "=" * 52, " NGROK + TELEGRAM WEBHOOK ", "=" * 52)
    launch_ngrok()
    ngrok_url = wait_for_ngrok_url()
    if ngrok_url:
        register_webhook(ngrok_url)
    else:
        log.warning(
            "%s Ngrok URL not available \u2014 webhook NOT registered. "
            "Run `ngrok http 8000` manually and register the webhook later.",
            WARN,
        )

    # ==================================================================
    # Step 4 — Ollama  (local provider only)
    # ==================================================================
    if provider == "local":
        print()
        log.info("%s%s%s", "=" * 52, " OLLAMA ", "=" * 52)
        launch_ollama()

    # ==================================================================
    # Step 5 — FastAPI
    # ==================================================================
    print()
    log.info("%s%s%s", "=" * 52, " FASTAPI ", "=" * 52)
    launch_fastapi()

    # ==================================================================
    # Summary
    # ==================================================================
    print()
    log.info("%s%s", "=" * 52, "=" * 28)
    log.info(" %s  ALL SERVICES LAUNCHED", ROCKET)
    log.info(" %s  Provider . . . . . . . . . . . . . . . %s", GEAR, provider.upper())
    log.info(
        " %s  Ngrok tunnel . . . . . . . . . . . . . %s",
        NGROK_EMOJI,
        ngrok_url or "NOT STARTED",
    )
    has_token = bool(get_env("TELEGRAM_BOT_TOKEN"))
    log.info(
        " %s  Telegram webhook . . . . . . . . . . . . %s",
        BOT,
        "REGISTERED" if (ngrok_url and has_token) else "SKIPPED",
    )
    log.info(" %s  FastAPI  \u2192  http://localhost:8000", ROCKET)
    log.info(" %s  API docs \u2192  http://localhost:8000/docs", INFO)
    log.info(" %s  Odoo     \u2192  http://localhost:8069", ODOO_EMOJI)
    if provider == "local":
        log.info(" %s  Ollama   \u2192  http://localhost:11434", ROCKET)
    log.info("%s%s", "=" * 52, "=" * 28)
    print()
    log.info("Each service runs in its own console window \u2014 close them to stop.")
    log.info("Press Ctrl+C in this terminal to exit the orchestrator.")
    print()

    # ==================================================================
    # Idle  \u2014  keep orchestrator alive until Ctrl+C
    # ==================================================================
    try:
        while True:
            time.sleep(2)
            for proc in list(_procs):
                if proc.poll() is not None:
                    _procs.remove(proc)
    except KeyboardInterrupt:
        log.info("\n%s Shutdown requested \u2026", WARN)
    finally:
        _cleanup()

    log.info("%s Orchestrator finished.", OK)
    return 0


if __name__ == "__main__":
    sys.exit(main())
