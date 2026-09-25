#!/usr/bin/env python3
"""
claude-x-jev  ·  scripts/jev.py

The one place this skill talks to Jev. Zero dependencies (Python 3.8+, stdlib only).

Jev is a decision model from TypeSafe, served through the OpenRouter Decisions API:
    POST https://openrouter.ai/api/alpha/decisions
It is NOT a chat model. Sending it to /chat/completions returns HTTP 400.

Subcommands
    status                    key present, credits, model uptime
    presets                   list presets found on this machine
    lint     --preset X       static checks on a preset's questions and criteria
    ask      --preset X --input items.json     run every question over every item
    route    --preset X --input items.json     ask, then split into sure / unsure files
    gate     --preset tool-gate --state '{...}'  approve / block / review one action
    match    --preset match-entity --input pairs.json   pairwise "same thing?" checks
    tune     --results run.jsonl --truth truth.jsonl --question Q   pick a threshold
    bench    --a run_a.jsonl --b run_b.jsonl --questions Q1,Q2      agreement table

Every run prints a one-line summary to stderr: items, wall time, mean latency, cost.
"""
import argparse
import csv
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API_URL = "https://openrouter.ai/api/alpha/decisions"
CREDITS_URL = "https://openrouter.ai/api/v1/credits"
ENDPOINTS_URL = "https://openrouter.ai/api/v1/models/typesafe/jev-1.13/endpoints"
DEFAULT_MODEL = "typesafe/jev-1.13"
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------
def die(msg, code=1):
    sys.stderr.write("[jev] " + msg + "\n")
    sys.exit(code)


def api_key():
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        die(
            "OPENROUTER_API_KEY is not set. Run /jev-setup, or:\n"
            "       export OPENROUTER_API_KEY=sk-or-...   (key from https://openrouter.ai/settings/keys)"
        )
    return key


def preset_dirs():
    dirs = []
    env = os.environ.get("JEV_PRESET_DIR")
    if env:
        dirs.append(env)
    dirs.append(os.path.join(os.getcwd(), ".claude", "jev-presets"))
    dirs.append(os.path.join(os.path.expanduser("~"), ".claude", "jev-presets"))
    dirs.append(os.path.join(SKILL_ROOT, "presets", "user"))
    dirs.append(os.path.join(SKILL_ROOT, "presets"))
    return [d for d in dirs if os.path.isdir(d)]


def load_preset(name_or_path):
    if os.path.isfile(name_or_path):
        path = name_or_path
    else:
        path = None
        for d in preset_dirs():
            cand = os.path.join(d, name_or_path + ".json")
            if os.path.isfile(cand):
                path = cand
                break
        if not path:
            die("preset '%s' not found. Searched: %s" % (name_or_path, ", ".join(preset_dirs())))
    with open(path, "r", encoding="utf-8") as fh:
        preset = json.load(fh)
    preset["_path"] = path
    preset.setdefault("model", DEFAULT_MODEL)
    preset.setdefault("thresholds", {})
    preset.setdefault("rules", [])
    if "questions" not in preset or not isinstance(preset["questions"], dict):
        die("preset %s has no 'questions' object" % path)
    return preset


def load_items(path):
    """JSON array, JSONL, or CSV. '-' reads stdin. Every item becomes a dict with an _id."""
    if path == "-":
        raw = sys.stdin.read()
        ext = ".json"
    else:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
        ext = os.path.splitext(path)[1].lower()
    raw = raw.strip()
    items = []
    if ext == ".csv":
        for row in csv.DictReader(io.StringIO(raw)):
            items.append(dict(row))
    elif ext == ".jsonl" or (ext != ".json" and "\n" in raw and raw[0] == "{"):
        for line in raw.splitlines():
            line = line.strip()
            if line:
                items.append(json.loads(line))
    else:
        data = json.loads(raw)
        if isinstance(data, dict):
            data = [data]
        items = list(data)
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            die("item %d is not an object" % i)
        it.setdefault("_id", str(i))
    return items


def build_state(item, preset, max_chars):
    fields = preset.get("state_fields")
    state = {}
    for k, v in item.items():
        if k.startswith("_"):
            continue
        if fields and k not in fields:
            continue
        if isinstance(v, str) and max_chars and len(v) > max_chars:
            v = v[:max_chars]
        state[k] = v
    return state


def post_json(url, body, key, timeout):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url, key, timeout=20):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def decide(state, questions, model, key, timeout=60, retries=4):
    """One Decisions request. Retries on 429 / 5xx / network. Raises on 4xx."""
    body = {"model": model, "state": state, "questions": questions}
    delay = 1.0
    last = None
    for attempt in range(retries + 1):
        try:
            t0 = time.time()
            out = post_json(API_URL, body, key, timeout)
            out["_latency_s"] = round(time.time() - t0, 3)
            return out
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "ignore")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                last = "HTTP %d" % e.code
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError("HTTP %d: %s" % (e.code, text[:400]))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < retries:
                last = str(e)
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError("network: %s" % e)
    raise RuntimeError("gave up: %s" % last)


def flatten_answers(answers):
    """Turn the API's per-question objects into flat, predictable fields."""
    flat = {}
    for q, a in answers.items():
        t = a.get("type")
        if t == "choice":
            flat[q] = a.get("choice")
            flat[q + "_conf"] = a.get("confidence")
            flat[q + "_probs"] = a.get("probabilities", {})
        elif t == "noul":
            flat[q] = a.get("noul")
        elif t == "score":
            flat[q] = a.get("score")
            flat[q + "_conf"] = a.get("confidence")
            flat[q + "_probs"] = a.get("probabilities", {})
            flat[q + "_legend"] = a.get("legend", {})
        else:
            flat[q] = a
    return flat


def apply_rules(flat, rules):
    """Reconcile answers. Jev answers questions independently; rules connect them.

    rule = {"when": {"q": "value"} | {"q": {"gte": 0.8}} | {"q": {"lte": 0.1}}, "set": {"q2": "value"}}
    All conditions in 'when' must hold. Rules run in order. Returns names of rules that fired.
    """
    fired = []
    for i, rule in enumerate(rules):
        ok = True
        for q, cond in rule.get("when", {}).items():
            v = flat.get(q)
            if isinstance(cond, dict):
                if "gte" in cond and not (isinstance(v, (int, float)) and v >= cond["gte"]):
                    ok = False
                if "lte" in cond and not (isinstance(v, (int, float)) and v <= cond["lte"]):
                    ok = False
                if "equals" in cond and v != cond["equals"]:
                    ok = False
            else:
                if v != cond:
                    ok = False
            if not ok:
                break
        if ok and rule.get("when"):
            for q, val in rule.get("set", {}).items():
                flat[q] = val
                flat[q + "_by_rule"] = True
            fired.append(rule.get("name", "rule_%d" % i))
    return fired


def is_sure(flat, questions, thresholds, default_threshold):
    """True when every thresholded question clears its bar.

    choice / score: confidence >= threshold
    noul:           probability outside the [low, high] band  (default band: 0.2 .. 0.8)
    """
    for q, spec in questions.items():
        t = thresholds.get(q, default_threshold)
        if flat.get(q + "_by_rule"):
            continue
        if spec.get("type") in ("choice", "score"):
            conf = flat.get(q + "_conf")
            if conf is None or conf < float(t):
                return False
        elif spec.get("type") == "noul":
            p = flat.get(q)
            if isinstance(t, dict):
                low, high = float(t.get("low", 0.2)), float(t.get("high", 0.8))
            else:
                low, high = 0.2, 0.8
            if p is None or (low < p < high):
                return False
    return True


# ----------------------------------------------------------------------------
# Subcommands
# ----------------------------------------------------------------------------
def cmd_status(args):
    key = api_key()
    print("key:        present (OPENROUTER_API_KEY)")
    try:
        c = get_json(CREDITS_URL, key)["data"]
        left = float(c.get("total_credits", 0)) - float(c.get("total_usage", 0))
        print("credits:    $%.2f left  (bought $%.2f, used $%.2f)" % (left, c["total_credits"], c["total_usage"]))
    except Exception as e:
        print("credits:    could not read (%s)" % e)
    try:
        ep = get_json(ENDPOINTS_URL, key)["data"]["endpoints"][0]
        lat = ep.get("latency_last_30m", {})
        print("model:      %s via %s" % (ep.get("model_id"), ep.get("provider_name")))
        print("uptime 24h: %s%%   p50 latency: %s ms   price: %s prompt, %s completion"
              % (ep.get("uptime_last_1d"), lat.get("p50"), ep["pricing"]["prompt"], ep["pricing"]["completion"]))
    except Exception as e:
        print("model:      could not read endpoint (%s)" % e)
    t0 = time.time()
    try:
        r = decide({"text": "ping"}, {"ok": {"type": "noul", "instructions": "Is `text` the word ping?"}}, DEFAULT_MODEL, key)
        print("live call:  ok  (%.0f ms, cost $%.6f, answer %.2f)" % ((time.time() - t0) * 1000, r["usage"]["cost"], r["answers"]["ok"]["noul"]))
    except Exception as e:
        die("live call failed: %s" % e)


def cmd_presets(args):
    seen = set()
    for d in preset_dirs():
        for f in sorted(os.listdir(d)):
            if f.endswith(".json") and f[:-5] not in seen:
                seen.add(f[:-5])
                try:
                    with open(os.path.join(d, f)) as fh:
                        p = json.load(fh)
                    print("%-18s %-60s %s" % (f[:-5], (p.get("description") or "")[:60], d))
                except Exception:
                    print("%-18s (unreadable) %s" % (f[:-5], d))


LINT_TELLS = ("etc", "and so on", "maybe", "might", "something like", "various", "general")


def lint_preset(preset):
    """Returns (errors, warnings). Errors block a run. Warnings are advice."""
    errors, warns = [], []
    qs = preset["questions"]
    if not qs:
        errors.append("no questions")
    for q, spec in qs.items():
        t = spec.get("type")
        ins = (spec.get("instructions") or "").strip()
        if t not in ("choice", "noul", "score"):
            errors.append("%s: type must be choice | noul | score" % q)
            continue
        if not ins:
            errors.append("%s: missing instructions" % q)
        elif len(ins) < 15:
            warns.append("%s: instructions are very short (%d chars). Say what to judge and on what field." % (q, len(ins)))
        if t == "choice":
            crit = spec.get("criteria")
            if not isinstance(crit, dict) or len(crit) < 2:
                errors.append("%s: choice needs 'criteria' as an object with 2+ labels" % q)
            else:
                for label, desc in crit.items():
                    if not desc or len(desc.strip()) < 12:
                        warns.append("%s.%s: criterion is too thin to separate it from its neighbours" % (q, label))
                    if any(w in desc.lower() for w in LINT_TELLS):
                        warns.append("%s.%s: vague words (%s). Replace with an observable cue." % (q, label, ", ".join(w for w in LINT_TELLS if w in desc.lower())))
                catch_all = ("other", "none", "not_applicable", "unclear", "unspecified", "unknown", "non_pitch", "noise", "irrelevant", "neither")
                if not spec.get("exhaustive") and not any(k in catch_all for k in crit):
                    warns.append("%s: no catch-all label (other / not_applicable). Items that fit nothing get forced into a wrong bucket. Add one, or set \"exhaustive\": true if the labels truly cover every case." % q)
        elif t == "score":
            crit = spec.get("criteria")
            if not isinstance(crit, list) or len(crit) < 2:
                errors.append("%s: score needs 'criteria' as an ORDERED list of level descriptions (index 0 = lowest)" % q)
        elif t == "noul":
            if "criteria" in spec:
                warns.append("%s: noul takes only instructions; 'criteria' is ignored" % q)
            if not any(ch in ins for ch in "?`"):
                warns.append("%s: noul instructions should read as a yes/no statement or question that names the field it judges" % q)
    for q, t in preset.get("thresholds", {}).items():
        if q not in qs:
            errors.append("thresholds.%s: no such question" % q)
    for i, rule in enumerate(preset.get("rules", [])):
        for q in list(rule.get("when", {}).keys()) + list(rule.get("set", {}).keys()):
            if q not in qs:
                errors.append("rules[%d]: refers to unknown question '%s'" % (i, q))
        if not rule.get("when") or not rule.get("set"):
            errors.append("rules[%d]: needs both 'when' and 'set'" % i)
    has_choice = any(spec.get("type") == "choice" for spec in qs.values())
    if len(qs) > 1 and has_choice and not preset.get("rules"):
        warns.append("a choice question plus other questions and no rules: Jev answers each question alone. Add a rule if two answers can contradict (e.g. 'affiliate_only' vs 'vendor_pitch').")
    return errors, warns


def cmd_lint(args):
    preset = load_preset(args.preset)
    errors, warns = lint_preset(preset)
    print("preset: %s" % preset["_path"])
    for e in errors:
        print("  ERROR  " + e)
    for w in warns:
        print("  warn   " + w)
    if not errors and not warns:
        print("  clean")
    sys.exit(1 if errors else 0)


def run_items(preset, items, args):
    key = api_key()
    errors, _ = lint_preset(preset)
    if errors:
        die("preset has errors, run `jev.py lint --preset %s` first:\n  " % args.preset + "\n  ".join(errors))
    questions = preset["questions"]
    model = args.model or preset["model"]
    display = preset.get("display_fields") or []
    results = [None] * len(items)
    T0 = time.time()

    def one(idx):
        item = items[idx]
        row = {"_id": item.get("_id")}
        for f in display:
            if f in item:
                row[f] = item[f]
        if args.dry_run:
            row["_state"] = build_state(item, preset, args.max_chars)
            return idx, row
        try:
            out = decide(build_state(item, preset, args.max_chars), questions, model, key, timeout=args.timeout)
            flat = flatten_answers(out.get("answers", {}))
            row["_rules"] = apply_rules(flat, preset.get("rules", []))
            row.update(flat)
            row["_sure"] = is_sure(flat, questions, preset.get("thresholds", {}), args.threshold)
            row["_cost"] = out.get("usage", {}).get("cost")
            row["_latency_s"] = out.get("_latency_s")
        except Exception as e:
            row["_error"] = str(e)
        return idx, row

    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as ex:
        for idx, row in ex.map(one, range(len(items))):
            results[idx] = row
    wall = time.time() - T0
    ok = [r for r in results if "_error" not in r and not args.dry_run]
    cost = sum(r.get("_cost") or 0 for r in ok)
    lat = [r["_latency_s"] for r in ok if r.get("_latency_s")]
    errs = [r for r in results if "_error" in r]
    sys.stderr.write(
        "[jev] %d items · %.1fs wall · %s mean latency · $%.4f · %d errors · sure %d / unsure %d\n"
        % (len(results), wall, ("%.2fs" % (sum(lat) / len(lat))) if lat else "n/a", cost, len(errs),
           sum(1 for r in ok if r.get("_sure")), sum(1 for r in ok if not r.get("_sure")))
    )
    for r in errs[:5]:
        sys.stderr.write("[jev]   error on %s: %s\n" % (r.get("_id"), r["_error"][:160]))
    return results


def write_rows(rows, path, as_csv=False):
    if path == "-" or not path:
        fh = sys.stdout
        close = False
    else:
        fh = open(path, "w", encoding="utf-8", newline="")
        close = True
    try:
        if as_csv:
            keys = []
            for r in rows:
                for k in r.keys():
                    if k not in keys and not k.endswith("_probs") and not k.endswith("_legend") and k != "_state":
                        keys.append(k)
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in r.items()})
        else:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    finally:
        if close:
            fh.close()


def cmd_ask(args):
    preset = load_preset(args.preset)
    items = load_items(args.input)
    if args.limit:
        items = items[: args.limit]
    rows = run_items(preset, items, args)
    write_rows(rows, args.out, as_csv=args.csv)


def cmd_route(args):
    preset = load_preset(args.preset)
    items = load_items(args.input)
    if args.limit:
        items = items[: args.limit]
    rows = run_items(preset, items, args)
    base = args.out or "jev-route"
    if base.endswith(".jsonl"):
        base = base[:-6]
    sure = [r for r in rows if r.get("_sure")]
    unsure = [r for r in rows if not r.get("_sure")]
    write_rows(sure, base + ".sure.jsonl")
    write_rows(unsure, base + ".unsure.jsonl")
    # Hand the unsure items back with their full state so Claude can read them without a second fetch.
    by_id = {it["_id"]: it for it in items}
    with open(base + ".unsure.items.jsonl", "w", encoding="utf-8") as fh:
        for r in unsure:
            it = dict(by_id.get(r["_id"], {}))
            it["_jev"] = {k: v for k, v in r.items() if not k.startswith("_") or k in ("_rules", "_error")}
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    print("sure:   %d  -> %s.sure.jsonl" % (len(sure), base))
    print("unsure: %d  -> %s.unsure.jsonl  (+ %s.unsure.items.jsonl with full text for Claude)" % (len(unsure), base, base))
    # Label distribution on the sure side, so the operator sees what auto-routing would do.
    for q, spec in preset["questions"].items():
        if spec.get("type") == "choice":
            counts = {}
            for r in sure:
                counts[r.get(q)] = counts.get(r.get(q), 0) + 1
            print("  %s (sure): %s" % (q, ", ".join("%s=%d" % kv for kv in sorted(counts.items(), key=lambda kv: -kv[1]))))


def cmd_gate(args):
    """Approve / block / review one action. Exit 0 approve, 1 block, 2 review.

    With --hook, read Claude Code's PreToolUse JSON from stdin and print the hook decision JSON.
    On any failure the hook prints nothing and exits 0, which leaves Claude Code's normal permission
    prompt in place. A gate must never auto-approve on error.
    """
    preset = load_preset(args.preset)
    hook_mode = args.hook
    if hook_mode and not os.environ.get("OPENROUTER_API_KEY", "").strip():
        sys.stderr.write("[jev gate] OPENROUTER_API_KEY not set; leaving the normal permission prompt in place\n")
        sys.exit(0)
    try:
        if hook_mode:
            raw = sys.stdin.read()
            hook_in = json.loads(raw) if raw.strip() else {}
            tools = [t.strip() for t in (args.tools or "Bash").split(",") if t.strip()]
            tool = hook_in.get("tool_name", "")
            if tool not in tools:
                return  # not gated, normal flow
            state = {
                "tool": tool,
                "tool_input": json.dumps(hook_in.get("tool_input", {}))[: args.max_chars],
                "cwd": hook_in.get("cwd", os.getcwd()),
            }
            if args.task:
                state["task"] = args.task
        else:
            if not args.state:
                die("gate needs --state '{...}' or --hook")
            state = json.loads(args.state)
        key = api_key()
        out = decide(state, preset["questions"], args.model or preset["model"], key, timeout=args.timeout)
        flat = flatten_answers(out.get("answers", {}))
        apply_rules(flat, preset.get("rules", []))
        checks = {q: flat.get(q) for q, s in preset["questions"].items() if s.get("type") == "noul"}
        if not checks:
            die("gate presets must use noul questions (each one is a condition that must hold)")
        vals = list(checks.values())
        if all(v is not None and v >= args.approve for v in vals):
            decision, code = "allow", 0
        elif any(v is not None and v <= args.block for v in vals):
            decision, code = "deny", 1
        else:
            decision, code = "ask", 2
        reason = "jev: " + ", ".join("%s=%.2f" % (k, v if v is not None else -1) for k, v in checks.items())
        if hook_mode:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}}))
            sys.exit(0)
        print(json.dumps({"decision": decision, "checks": checks, "reason": reason, "cost": out.get("usage", {}).get("cost"), "latency_s": out.get("_latency_s")}, indent=2))
        sys.exit(code)
    except SystemExit:
        raise
    except Exception as e:
        if hook_mode:
            sys.stderr.write("[jev gate] %s (falling through to the normal permission prompt)\n" % e)
            sys.exit(0)
        die("gate failed: %s" % e)


def cmd_match(args):
    """Pairwise checks. Items carry two sides (default fields: a, b). Preset should be noul questions."""
    preset = load_preset(args.preset)
    items = load_items(args.input)
    if args.limit:
        items = items[: args.limit]
    rows = run_items(preset, items, args)
    write_rows(rows, args.out, as_csv=args.csv)


def cmd_tune(args):
    """Sweep confidence thresholds for one choice/score question against a truth file.

    results: JSONL from `ask` (needs _id, Q, Q_conf).  truth: JSONL/JSON/CSV with _id and Q (the right label).
    Prints, per threshold: coverage (share of items auto-decided) and precision (share of those that were right).
    """
    res = {r["_id"]: r for r in load_items(args.results)}
    truth = {t["_id"]: t for t in load_items(args.truth)}
    q = args.question
    pairs = []
    for i, t in truth.items():
        r = res.get(i)
        if r is None or q not in r or (q + "_conf") not in r:
            continue
        pairs.append((float(r[q + "_conf"]), str(r[q]) == str(t.get(q))))
    if not pairs:
        die("no overlapping _id between results and truth for question %s" % q)
    n = len(pairs)
    print("question: %s   items with truth: %d   overall accuracy: %.1f%%" % (q, n, 100.0 * sum(1 for _, ok in pairs if ok) / n))
    print("%-10s %-10s %-10s %-10s" % ("threshold", "coverage", "precision", "auto-wrong"))
    best = None
    for t10 in range(50, 100, 5):
        t = t10 / 100.0
        auto = [ok for c, ok in pairs if c >= t]
        cov = len(auto) / n
        prec = (sum(1 for ok in auto if ok) / len(auto)) if auto else 0.0
        wrong = len(auto) - sum(1 for ok in auto if ok)
        print("%-10.2f %-9.1f%% %-9.1f%% %d" % (t, cov * 100, prec * 100, wrong))
        if prec >= args.target and (best is None or cov > best[1]):
            best = (t, cov, prec)
    if best:
        print("\nrecommend: threshold %.2f  -> auto-decides %.0f%% of items at %.1f%% precision (target %.0f%%)" % (best[0], best[1] * 100, best[2] * 100, args.target * 100))
        print("write it into the preset:  \"thresholds\": {\"%s\": %.2f}" % (q, best[0]))
    else:
        print("\nno threshold reaches %.0f%% precision. Rewrite the criteria for '%s' (run lint) before trusting auto-routing." % (args.target * 100, q))


def cmd_bench(args):
    a = {r["_id"]: r for r in load_items(args.a)}
    b = {r["_id"]: r for r in load_items(args.b)}
    ids = [i for i in a if i in b]
    if not ids:
        die("no overlapping _id between the two result files")
    qs = [q.strip() for q in args.questions.split(",") if q.strip()]
    print("items compared: %d" % len(ids))
    print("%-20s %-10s %s" % ("question", "agree", "disagreements (id: a vs b)"))
    for q in qs:
        agree = [i for i in ids if str(a[i].get(q)) == str(b[i].get(q))]
        dis = [i for i in ids if i not in set(agree)]
        sample = "; ".join("%s: %s vs %s" % (i, a[i].get(q), b[i].get(q)) for i in dis[:6])
        print("%-20s %-10s %s" % (q, "%d/%d (%.1f%%)" % (len(agree), len(ids), 100.0 * len(agree) / len(ids)), sample))
    ca = sum(float(a[i].get("_cost") or 0) for i in ids)
    cb = sum(float(b[i].get("_cost") or 0) for i in ids)
    if ca or cb:
        print("cost: a=$%.4f  b=$%.4f" % (ca, cb))


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def add_run_args(p):
    p.add_argument("--preset", required=True, help="preset name (searched in preset dirs) or a path to a .json")
    p.add_argument("--input", required=True, help="items file: .json array, .jsonl, .csv, or - for stdin")
    p.add_argument("--out", default="-", help="output path (.jsonl default, .csv with --csv). Default stdout")
    p.add_argument("--csv", action="store_true", help="write CSV instead of JSONL")
    p.add_argument("--threshold", type=float, default=0.7, help="default confidence bar for choice/score questions (preset thresholds override; a preset threshold of 0 makes that question informational, never blocking _sure)")
    p.add_argument("--concurrency", type=int, default=8, help="parallel requests (Jev handles 8 comfortably)")
    p.add_argument("--max-chars", type=int, default=8000, help="truncate each string field in state to this many chars")
    p.add_argument("--limit", type=int, default=0, help="only run the first N items")
    p.add_argument("--model", default=None, help="override model (default from preset, typesafe/jev-1.13)")
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--dry-run", action="store_true", help="show the state each item would send, no API calls")


def main():
    ap = argparse.ArgumentParser(prog="jev.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="key, credits, model uptime, one live call").set_defaults(fn=cmd_status)
    sub.add_parser("presets", help="list presets on this machine").set_defaults(fn=cmd_presets)

    p = sub.add_parser("lint", help="static checks on a preset")
    p.add_argument("--preset", required=True)
    p.set_defaults(fn=cmd_lint)

    p = sub.add_parser("ask", help="run a preset over items")
    add_run_args(p)
    p.set_defaults(fn=cmd_ask)

    p = sub.add_parser("route", help="ask, then split sure / unsure")
    add_run_args(p)
    p.set_defaults(fn=cmd_route)

    p = sub.add_parser("match", help="pairwise checks (items carry both sides)")
    add_run_args(p)
    p.set_defaults(fn=cmd_match)

    p = sub.add_parser("gate", help="approve / block / review one action")
    p.add_argument("--preset", default="tool-gate")
    p.add_argument("--state", default=None, help="JSON object describing the action")
    p.add_argument("--hook", action="store_true", help="read Claude Code PreToolUse JSON from stdin, print hook decision JSON")
    p.add_argument("--tools", default="Bash", help="comma list of tool names to gate in --hook mode")
    p.add_argument("--task", default=None, help="what the agent is supposed to be doing (improves the serves_task check)")
    p.add_argument("--approve", type=float, default=0.9)
    p.add_argument("--block", type=float, default=0.1)
    p.add_argument("--model", default=None)
    p.add_argument("--timeout", type=int, default=20)
    p.add_argument("--max-chars", type=int, default=4000)
    p.set_defaults(fn=cmd_gate)

    p = sub.add_parser("tune", help="pick a confidence threshold from labelled data")
    p.add_argument("--results", required=True)
    p.add_argument("--truth", required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--target", type=float, default=0.95, help="precision you require on auto-decided items")
    p.set_defaults(fn=cmd_tune)

    p = sub.add_parser("bench", help="agreement between two result files")
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--questions", required=True, help="comma list of question keys")
    p.set_defaults(fn=cmd_bench)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
