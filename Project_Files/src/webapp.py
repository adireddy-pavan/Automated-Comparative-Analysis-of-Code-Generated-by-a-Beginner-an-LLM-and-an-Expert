"""Interactive web dashboard for the comparative code analysis.

Two things live here:

1. :func:`build_dashboard` renders a single, fully self-contained
   ``report/dashboard.html`` — every number, every figure (base64-inlined) and
   every solution's syntax-highlighted source is embedded, so it opens offline
   straight from ``file://`` with no server and no network.
2. :func:`serve` starts a standard-library ``http.server`` so the same dashboard
   can be browsed "live" at ``http://localhost:8000`` and (optionally) re-run.

It introduces **no new dependencies**: templating uses ``jinja2`` (already
required) and the web server is Python's standard library. Source highlighting
uses the standard-library ``tokenize`` module, so it is exact and offline.

Run directly:

    python -m src.webapp build           # write report/dashboard.html
    python -m src.webapp serve            # build + serve at :8000
"""
from __future__ import annotations

import argparse
import base64
import html
import io
import json
import keyword
# subprocess is used only for a fixed, local, no-shell command (the re-run hook);
# see the [tool.bandit] skips rationale in pyproject.toml.
import subprocess
import sys
import tokenize
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pandas as pd
from jinja2 import Environment
from markupsafe import Markup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402
from src import dataset_loader, utils  # noqa: E402

DASHBOARD_PATH = config.REPORT_DIR / "dashboard.html"


# --------------------------------------------------------------------------- #
# Python source -> monochrome, line-numbered HTML (stdlib tokenize)
# --------------------------------------------------------------------------- #
_TOKEN_CLASS = {
    tokenize.COMMENT: "c",   # comment
    tokenize.STRING: "s",    # string / docstring
    tokenize.NUMBER: "n",    # number
}


def highlight(source: str) -> str:
    """Return *source* as highlighted, line-numbered HTML (monochrome classes)."""
    try:
        spans = _tokenize_spans(source)
    except Exception:  # noqa: BLE001 - fall back to plain escaped text
        spans = None

    lines = source.splitlines() or [""]
    if spans is None:
        body = "\n".join(html.escape(line) for line in lines)
        return f'<pre class="code"><code>{body}</code></pre>'

    out_lines: list[str] = []
    for i, line_html in enumerate(spans, 1):
        out_lines.append(
            f'<span class="ln">{i:>2}</span><span class="lc">{line_html}</span>'
        )
    return '<pre class="code"><code>' + "\n".join(out_lines) + "</code></pre>"


def _tokenize_spans(source: str) -> list[str]:
    """Build a list of per-line HTML with <span> wrapped tokens."""
    lines = source.split("\n")
    # Per-character class map, then assemble. Simpler & robust against overlaps.
    readline = io.StringIO(source).readline
    marks: dict[tuple[int, int], tuple[str, int]] = {}
    for tok in tokenize.generate_tokens(readline):
        cls = _TOKEN_CLASS.get(tok.type)
        if cls is None and tok.type == tokenize.NAME:
            if keyword.iskeyword(tok.string):
                cls = "k"
            elif keyword.issoftkeyword(tok.string):
                cls = "k"
        if cls is None and tok.type == tokenize.OP:
            cls = "o"
        if cls is None:
            continue
        (sr, sc), (er, ec) = tok.start, tok.end
        if sr == er:
            marks[(sr, sc)] = (cls, ec)
    rendered: list[str] = []
    for lineno, line in enumerate(lines, 1):
        col = 0
        buf: list[str] = []
        while col < len(line):
            mark = marks.get((lineno, col))
            if mark:
                cls, end_col = mark
                segment = line[col:end_col]
                buf.append(f'<span class="{cls}">{html.escape(segment)}</span>')
                col = end_col
            else:
                buf.append(html.escape(line[col]))
                col += 1
        rendered.append("".join(buf))
    return rendered


# --------------------------------------------------------------------------- #
# Context assembly (all numbers come from the computed output files)
# --------------------------------------------------------------------------- #
def _figure_data_uri(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def _build_context() -> dict[str, Any]:
    df = pd.read_csv(config.METRICS_CSV)
    stats_blob = utils.read_json(config.STATS_JSON)
    tasks = {t.task_id: t for t in dataset_loader.discover_tasks()}

    # KPI cards
    rates = stats_blob["functional"]["pass_rate_overall"]
    counts = stats_blob["functional"]["pass_counts_overall"]

    def best(metric: str) -> str:
        rec = stats_blob["metrics"][metric]
        medians = {s: rec["groups"][s]["median"] for s in config.SOURCES
                   if rec["groups"][s]["median"] is not None}
        if not medians:
            return "N/A"
        return (max if rec["orientation"] == "up" else min)(medians, key=medians.get)

    # Bandit total per source on the balanced one-per-(task, source) view (each
    # source's per-task median), so the k-sample LLM arm is not summed over k x
    # tasks rows and the comparison matches the static-metric tests / figures.
    bandit_collapsed = utils.collapse_samples(df, ["bandit_total"])
    kpis = {
        "n_tasks": stats_blob["n_tasks"],
        "n_rows": len(df),
        "llm_samples": config.SAMPLES_PER_SOURCE.get("llm", 1),
        "pass_rates": {s: rates[s] for s in config.SOURCES},
        "pass_counts": counts,
        "best_mi": best("mi"),
        "best_cc": best("mean_cc"),
        "best_style": best("pylint_score"),
        "bandit_by_source": {
            s: int(bandit_collapsed.loc[bandit_collapsed["source"] == s,
                                        "bandit_total"].sum())
            for s in config.SOURCES
        },
    }

    # Metrics table (records) for the explorer
    table_cols = ["task_id", "difficulty", "source", "sample", "mean_cc", "max_cc",
                  "mi", "halstead_volume", "sloc", "comments", "pylint_score",
                  "pylint_issues", "bandit_total", "functional_pass",
                  "tests_passed", "tests_total"]
    table_cols = [c for c in table_cols if c in df.columns]
    metrics_records = df[table_cols].to_dict(orient="records")

    # Statistics tables
    metric_stats = []
    for rec in stats_blob["metrics"].values():
        g = rec["groups"]
        metric_stats.append({
            "label": rec["label"],
            "orientation": rec["orientation"],
            "median": {s: g[s]["median"] for s in config.SOURCES},
            "kw_h": rec["friedman"]["statistic"],
            "kw_p": rec["friedman"]["p"],
            "kw_sig": rec["friedman"]["significant"],
            "pairs": [
                {"name": p.replace("_vs_", " vs "), "p_adj": pr["p_adj"],
                 "sig": pr["significant"], "delta": pr["rank_biserial"],
                 "mag": "paired"}
                for p, pr in rec["pairwise"].items()
            ],
        })

    # Figures (base64 inlined)
    order = {f"box_{m}.png": i for i, m in enumerate(config.BOXPLOT_METRICS)}
    order["passrate_by_difficulty.png"] = 100
    order["radar_overall.png"] = 101
    figures = []
    for path in sorted(config.FIGURES_DIR.glob("*.png"),
                       key=lambda p: order.get(p.name, 50)):
        figures.append({"name": path.stem, "uri": _figure_data_uri(path)})

    # Task code browser: highlighted source + metric chips per source
    task_views = []
    for task_id in sorted(tasks):
        task = tasks[task_id]
        sub = df[df["task_id"] == task_id]
        sources = []
        for source in config.SOURCES:
            n_samples = config.SAMPLES_PER_SOURCE.get(source, 1)
            # Show the representative (first) sample; note the sample count so the
            # multi-sample LLM arm is transparent in the browser.
            sel = sub[sub["source"] == source]
            if "sample" in sub.columns:
                sel = sel[sel["sample"] == 1]
            row = sel.iloc[0].to_dict()
            code = task.solution_path(source).read_text(encoding="utf-8")
            sources.append({
                "source": source,
                "n_samples": n_samples,
                # highlight() HTML-escapes every character of the raw source and
                # only emits fixed <span> tags, so the result is XSS-safe to mark.
                "code_html": Markup(highlight(code)),
                "loc": len(code.splitlines()),
                "mean_cc": row["mean_cc"], "mi": row["mi"],
                "pylint_score": row["pylint_score"], "bandit_total": row["bandit_total"],
                "passed": bool(row["functional_pass"]),
                "tests": f"{int(row['tests_passed'])}/{int(row['tests_total'])}",
            })
        task_views.append({
            "id": task_id, "title": task.title, "difficulty": task.difficulty,
            "entry_point": task.entry_point, "description": task.description,
            "sources": sources,
        })

    # Findings: pass-by-difficulty, significance summary, RQ3 verdict, RQ4 example
    by_diff = stats_blob["functional"]["pass_rate_by_difficulty"]
    sig_summary = [
        {"label": rec["label"], "sig": rec["friedman"]["significant"],
         "p": rec["friedman"]["p"]}
        for rec in stats_blob["metrics"].values()
    ]
    rq3 = _rq3_verdict(stats_blob)
    rq4 = _rq4_example(df)

    return {
        "title": config.PROJECT_NAME, "full_title": config.FULL_TITLE,
        "author": config.AUTHOR, "institution": config.INSTITUTION,
        "sources": list(config.SOURCES), "difficulties": list(config.DIFFICULTIES),
        "kpis": kpis, "metrics_records": metrics_records,
        "metric_stats": metric_stats, "figures": figures,
        "tasks": task_views, "by_difficulty": by_diff,
        "chi2": stats_blob["functional"]["cochrans_q"], "sig_summary": sig_summary,
        "rq3": rq3, "rq4": rq4, "references": list(config.REFERENCES),
        "pass_at_k": stats_blob.get("pass_at_k", {}),
        "pass_at_k_ks": list(config.PASS_AT_K),
        # Our own data (task ids + numbers). HTML-significant characters are
        # unicode-escaped so the payload can never break out of the <script>
        # block, then marked safe for embedding as a JS/JSON literal.
        "metrics_json": Markup(_json_for_script(metrics_records)),
    }


def _json_for_script(data: Any) -> str:
    """Serialise *data* to JSON safe to embed inside an HTML <script> element.

    The payload is read back via ``JSON.parse(textContent)``; escaping the three
    HTML-significant characters guarantees it cannot terminate the script block.
    """
    return (json.dumps(data)
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))


def _rq3_verdict(stats_blob: dict) -> dict[str, Any]:
    metrics = ["mean_cc", "max_cc", "mi", "halstead_volume", "loc", "sloc",
               "comments", "pylint_score", "pylint_issues", "bandit_total"]
    nearer_beg = nearer_exp = ties = 0
    for metric in metrics:
        g = stats_blob["metrics"][metric]["groups"]
        m_l, m_b, m_e = g["llm"]["median"], g["beginner"]["median"], g["expert"]["median"]
        if None in (m_l, m_b, m_e):
            continue
        d_b, d_e = abs(m_l - m_b), abs(m_l - m_e)
        if d_b < d_e:
            nearer_beg += 1
        elif d_e < d_b:
            nearer_exp += 1
        else:
            ties += 1
    verdict = ("expert" if nearer_exp > nearer_beg else
               "beginner" if nearer_beg > nearer_exp else "neither (tie)")
    return {"beginner": nearer_beg, "expert": nearer_exp, "ties": ties,
            "verdict": verdict, "metric_count": len(metrics)}


def _rq4_example(df: pd.DataFrame) -> dict[str, Any] | None:
    failing = df[~df["functional_pass"].astype(bool)]
    if failing.empty:
        return None
    worst = failing.sort_values("mi", ascending=False).iloc[0]
    return {"task_id": worst["task_id"], "source": worst["source"],
            "mi": round(float(worst["mi"]), 1),
            "pylint": round(float(worst["pylint_score"]), 1),
            "passed": int(worst["tests_passed"]), "total": int(worst["tests_total"])}


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def build_dashboard() -> Path:
    """Render the self-contained dashboard to report/dashboard.html."""
    log = utils.get_logger()
    context = _build_context()
    # autoescape ON: every interpolated text value is HTML-escaped. The two
    # fields that are intentionally raw HTML (code_html, metrics_json) are passed
    # as markupsafe.Markup and are themselves already escaped/trusted.
    env = Environment(autoescape=True)
    template = env.from_string(_TEMPLATE)
    config.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(template.render(**context), encoding="utf-8")
    log.info("Wrote %s", DASHBOARD_PATH)
    return DASHBOARD_PATH


# --------------------------------------------------------------------------- #
# Live server (standard library only)
# --------------------------------------------------------------------------- #
class _Handler(SimpleHTTPRequestHandler):
    """Serves the project dir read-only; '/' redirects to the dashboard.

    The re-run endpoint (``POST /api/rerun``) is **disabled by default** and only
    accepted when the server was started with ``enable_rerun=True``. The server
    binds to loopback only, so it is never exposed to the network.
    """

    enable_rerun = False  # class-level switch flipped by serve()

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/report/dashboard.html")
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self):  # noqa: N802
        """Handle the opt-in ``/api/rerun`` endpoint; 404 otherwise."""
        if self.path == "/api/rerun" and self.enable_rerun:
            # Fixed, local command; no shell; no request data reaches the args.
            proc = subprocess.run(
                [sys.executable, str(config.ROOT / "run_analysis.py")],
                cwd=str(config.ROOT), capture_output=True, text=True, check=False,
            )
            build_dashboard()
            payload = json.dumps({"returncode": proc.returncode,
                                  "tail": (proc.stdout or "")[-2000:]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_error(404)

    def log_message(self, *args):  # keep the console clean
        return


def serve(port: int = 8000, open_browser: bool = True,
          enable_rerun: bool = False) -> None:
    """Build the dashboard then serve the project directory on loopback.

    Args:
        port: TCP port to listen on (loopback only).
        open_browser: Open the dashboard in a browser when starting.
        enable_rerun: Opt in to the ``POST /api/rerun`` endpoint (off by default;
            it would execute the pipeline, so it stays disabled unless asked for).
    """
    build_dashboard()
    _Handler.enable_rerun = enable_rerun
    handler = partial(_Handler, directory=str(config.ROOT))
    url = f"http://127.0.0.1:{port}/report/dashboard.html"
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)  # loopback only
    rerun_note = "  (re-run endpoint ENABLED)" if enable_rerun else ""
    print(f"\n  Dashboard live at:  {url}\n  (Ctrl+C to stop){rerun_note}\n")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            utils.get_logger().debug("could not auto-open a browser")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        print("\n  Dashboard stopped.")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``build`` writes the dashboard, ``serve`` serves it."""
    parser = argparse.ArgumentParser(description="Comparative code analysis dashboard.")
    parser.add_argument("command", choices=["build", "serve"], nargs="?",
                        default="build")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--enable-rerun", action="store_true",
                        help="enable POST /api/rerun (executes the pipeline; off by default)")
    args = parser.parse_args(argv)
    utils.setup_logging()
    if args.command == "serve":
        serve(port=args.port, open_browser=not args.no_browser,
              enable_rerun=args.enable_rerun)
    else:
        print(build_dashboard())
    return 0


# The template is defined in webapp_template.py to keep this module readable.
from src.webapp_template import TEMPLATE as _TEMPLATE  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
