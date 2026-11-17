"""Regenerate BUILD_STATUS.md from the folder trees in each lab README."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
out, tot, have = [], 0, 0
for d in ["setup"] + [f"ch{i:02d}" for i in range(1, 14)]:
    s = open(f"{d}/README.md").read()
    m = re.search(r"```\n" + re.escape(d) + r"/\n(.*?)```", s, re.S)
    if not m:
        continue
    stack, items = [], []
    for line in m.group(1).splitlines():
        mm = re.match(r"^([│ ]*)[├└]── (.+?)(\s+←.*)?$", line)
        if not mm:
            continue
        depth = len(mm.group(1)) // 4
        stack = stack[:depth]
        for n in [x.strip() for x in mm.group(2).strip().split(" / ") if x.strip() != ".env"]:
            items.append("/".join(stack + [n]))
            if n.endswith("/"):
                stack.append(n.rstrip("/"))
    out.append(f"\n## {d}\n")
    for p in items:
        full = os.path.join(d, p.rstrip("/"))
        ok = os.path.exists(full) and (not p.endswith("/") or bool(os.listdir(full)))
        tot += 1
        have += ok
        out.append(f"- {'✅' if ok else '⬜'} `{p}`")
head = ["# Repository build status\n",
        "Each lab README is the specification for its folder. This file lists, per lab, "
        "the files the README's folder tree names, and whether each exists yet. "
        "Regenerate it with `python tools/build_status.py`.\n",
        "Legend: ✅ present · ⬜ still to build\n",
        f"**{have} of {tot} listed items exist.** `vendor/` folders are filled by each lab's "
        "`setup.sh` from Google's `adk-samples` at the pinned commit.\n"]
open("BUILD_STATUS.md", "w").write("\n".join(head + out) + "\n")
print(f"{have} of {tot} items present")
