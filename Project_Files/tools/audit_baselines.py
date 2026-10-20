#!/usr/bin/env python3
"""Describe construct validity of deliberately constructed reference code.

This is an AUTOMATED structural inspection, not independent human validation or
proof that the 'beginner' and 'expert' labels describe actual programmers.
Run with `python tools/audit_baselines.py`.  Python standard library only.
"""
from __future__ import annotations
import ast
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "dataset" / "tasks"
OUT = ROOT / "verification"


def describe(path: Path, entry_point: str) -> dict:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    funcs = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    matches = [node for node in funcs if node.name == entry_point]
    if len(matches) != 1:
        raise ValueError(f"Expected one entry point {entry_point}: {path}")
    fn = matches[0]
    return {
        "file": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(source.encode()).hexdigest(),
        "lines": len(source.splitlines()),
        "top_level_functions": len(funcs),
        "docstring": bool(ast.get_docstring(fn)),
        "return_annotated": fn.returns is not None,
        "annotated_parameters": sum(a.annotation is not None for a in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs)),
        "branch_nodes": sum(isinstance(node, (ast.If, ast.IfExp, ast.For, ast.While, ast.Try, ast.Match)) for node in ast.walk(fn)),
    }


def audit() -> list[dict]:
    rows=[]
    for directory in sorted(TASKS.iterdir()):
        if not directory.is_dir():
            continue
        meta=json.loads((directory/"meta.json").read_text(encoding="utf-8"))
        for source in ("beginner", "expert"):
            path=directory/"solutions"/(source+".py")
            details=describe(path,meta["entry_point"])
            rows.append({"task_id":directory.name,"difficulty":meta["difficulty"],"constructed_label":source,**details})
    if len(rows)!=60:
        raise ValueError(f"Expected 60 reference files; got {len(rows)}")
    return rows


def main():
    rows=audit()
    OUT.mkdir(parents=True, exist_ok=True)
    columns=list(rows[0])
    with (OUT/"baseline_structural_audit.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
    summary={src:{"n":len(sub),
                  "docstring_count":sum(row["docstring"] for row in sub),
                  "return_annotated_count":sum(row["return_annotated"] for row in sub),
                  "median_lines":sorted(row["lines"] for row in sub)[len(sub)//2]}
             for src in ("beginner","expert")
             for sub in [[r for r in rows if r["constructed_label"]==src]]}
    result={"status":"descriptive-only construct audit; not validation of real programming expertise",
            "n_tasks":30,"n_constructed_implementations":len(rows),"summary":summary,
            "major_threat":"Labels and some failure patterns are imposed by construction. Any expert advantage may be partly baked into the design.",
            "external_review":"NOT PERFORMED: independent programming-experience and difficulty validation needs actual reviewer evidence"}
    (OUT/"baseline_audit_summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    main()
