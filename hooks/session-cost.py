#!/usr/bin/env python3
"""Per-session cost for worklogs.

Billed delta: Claude reads extraUsage.spent (mcp__ccd_session_mgmt__get_usage) at session
start and at /log, and passes it here. Account-wide, so parallel sessions inflate it.
Estimate: token usage from the session transcript (+ subagents) at list price, as a cross-check.

  session-cost.py snapshot --cwd "$PWD" --spent 127.52
  session-cost.py report   --cwd "$PWD" --spent 129.80
"""
import argparse, glob, json, os, re, sys, time, urllib.request
from datetime import datetime, date

STATE = os.path.expanduser("~/.claude/state/session-cost")
PROJECTS = os.path.expanduser("~/.claude/projects")
PRICES_URL = "https://platform.claude.com/docs/en/about-claude/pricing.md"
PRICES_CACHE = os.path.join(STATE, "prices.json")
PRICES_MAX_AGE = 7 * 86400

# Fallback when docs and cache are unavailable. USD per MTok:
# input, 5m cache write, 1h cache write, cache read, output.
FALLBACK = {
    "claude-opus-5-5": [4.00, 5.00, 8.00, 0.20, 20.00],
    "claude-sonnet-5-5": [2.00, 2.50, 4.00, 0.10, 10.00],
    "claude-haiku-5-5": [0.10, 0.125, 0.20, 0.01, 0.50],
    "claude-haiku-5-5@long": [0.50, 0.625, 1.00, 0.05, 2.50],
    "claude-fable-5-1": [10.00, 12.50, 20.00, 0.25, 50.00],
}
FAST = {"claude-opus-5-5": 2.0}  # fast mode multiplier
LONG_PROMPT = 100_000  # Haiku 5.5 "@long" tier threshold
US_GEO_MULT = 1.1
WEB_SEARCH_USD = 0.01  # per request


def model_id(name):
    name = name.split("(")[0].strip().lower()  # drop "(for prompts ...)" / "([retired](link))"
    return re.sub(r"[ .]+", "-", name)


def parse_prices(md):
    prices, fast, table = {}, {}, None
    for line in md.splitlines():
        if line.startswith("## ") or line.startswith("### "):
            table = None
        if line.startswith("| Model") and "Base input tokens" in line:
            table = "base"
        elif line.startswith("| Model") and "Input" in line and "Output" in line:
            table = "fast"
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        nums = [float(n) for n in (re.search(r"\$([\d.]+)", re.sub(r"<sup>.*?</sup>", "", c)).group(1)
                for c in cells[1:] if re.search(r"\$[\d.]+", c))]
        if not table or not cells[0].startswith("Claude"):
            continue
        if table == "base" and len(nums) == 5:
            key = model_id(cells[0]) + ("@long" if "over 100,000" in cells[0] else "")
            prices[key] = nums
        elif table == "fast" and len(nums) == 2:
            for name in cells[0].split("/"):
                base = prices.get(model_id(name))
                if base:
                    fast[model_id(name)] = nums[0] / base[0]
    return prices, fast


def load_prices():
    try:
        c = json.load(open(PRICES_CACHE))
        if time.time() - c["fetched"] < PRICES_MAX_AGE:
            return c["prices"], c["fast"], f"docs {c['date']} (cache)"
    except (OSError, ValueError, KeyError):
        c = None
    try:
        req = urllib.request.Request(PRICES_URL, headers={"User-Agent": "curl/8.7.1"})  # default Python UA gets 403
        md = urllib.request.urlopen(req, timeout=15).read().decode()
        prices, fast = parse_prices(md)
        if "claude-opus-5-5" not in prices:
            raise ValueError("pricing table not parsed")
        os.makedirs(STATE, exist_ok=True)
        json.dump({"fetched": time.time(), "date": date.today().isoformat(), "prices": prices, "fast": fast},
                  open(PRICES_CACHE, "w"))
        return prices, fast, f"docs {date.today().isoformat()}"
    except Exception as e:
        if c:
            return c["prices"], c["fast"], f"docs {c['date']} (stale cache; fetch failed: {e})"
        return FALLBACK, FAST, f"hardcoded fallback (fetch failed: {e})"


def transcript_for(cwd, session):
    proj = os.path.join(PROJECTS, re.sub(r"[^A-Za-z0-9]", "-", cwd))
    if session:
        return os.path.join(proj, session + ".jsonl")
    files = glob.glob(os.path.join(proj, "*.jsonl"))
    if not files:
        sys.exit(f"no transcript in {proj}")
    return max(files, key=os.path.getmtime)


def estimate(main):
    prices, fast, source = load_prices()
    sid = os.path.basename(main)[:-6]
    files = [main] + glob.glob(os.path.join(os.path.dirname(main), sid, "subagents", "**", "*.jsonl"), recursive=True)
    seen, total, unknown, tokens = set(), 0.0, set(), {}
    for f in files:
        for line in open(f):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            m = d.get("message") or {}
            u = m.get("usage")
            if d.get("type") != "assistant" or not u:
                continue
            key = (m.get("id"), d.get("requestId"))
            if key in seen:  # streaming writes one line per content block
                continue
            seen.add(key)
            model = re.sub(r"-\d{8}$", "", m.get("model", "?"))  # claude-haiku-4-5-20251001 -> claude-haiku-4-5
            if model == "<synthetic>":
                continue
            if model not in prices:
                unknown.add(model)
                continue
            prompt = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
            key = model + "@long" if prompt > LONG_PROMPT and model + "@long" in prices else model
            pin, p5m, p1h, pread, pout = prices[key]
            mult = fast.get(model, 1) if u.get("speed") == "fast" else 1
            if u.get("inference_geo") == "us":
                mult *= US_GEO_MULT
            cc = u.get("cache_creation") or {}
            w1h = cc.get("ephemeral_1h_input_tokens", 0)
            w5m = cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) - w1h)
            cost = (u.get("input_tokens", 0) * pin + u.get("output_tokens", 0) * pout
                    + u.get("cache_read_input_tokens", 0) * pread
                    + w5m * p5m + w1h * p1h) / 1e6 * mult
            cost += (u.get("server_tool_use") or {}).get("web_search_requests", 0) * WEB_SEARCH_USD
            total += cost
            t = tokens.setdefault(model, [0, 0])
            t[0] += prompt
            t[1] += u.get("output_tokens", 0)
    return sid, total, tokens, unknown, source


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["snapshot", "report"])
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("--session")
    ap.add_argument("--spent", type=float)
    a = ap.parse_args()
    sid = os.path.basename(transcript_for(a.cwd, a.session))[:-6]
    snap = os.path.join(STATE, sid + ".json")

    if a.cmd == "snapshot":
        if a.spent is None:
            sys.exit("--spent required")
        os.makedirs(STATE, exist_ok=True)
        if os.path.exists(snap):
            print(f"snapshot exists, kept: {open(snap).read()}")
            return
        json.dump({"session_id": sid, "start_spent": a.spent, "start_at": datetime.now().isoformat(timespec="seconds")}, open(snap, "w"))
        print(f"snapshot saved: {sid} spent={a.spent:.2f}")
        return

    _, est, tokens, unknown, source = estimate(transcript_for(a.cwd, a.session))
    if os.path.exists(snap) and a.spent is not None:
        s = json.load(open(snap))
        print(f"- Billed (extra usage delta): US$ {a.spent - s['start_spent']:.2f} "
              f"(US$ {s['start_spent']:.2f} at {s['start_at']} -> US$ {a.spent:.2f}; account-wide)")
    else:
        print("- Billed (extra usage delta): n/a (no start snapshot)")
    detail = ", ".join(f"{m}: {i/1e6:.2f}M in / {o/1e3:.0f}k out" for m, (i, o) in tokens.items())
    print(f"- Estimate (transcript, list price): US$ {est:.2f} ({detail}; prices: {source})")
    if unknown:
        print(f"- Unpriced models, not in estimate: {', '.join(sorted(unknown))}")


if __name__ == "__main__":
    main()
