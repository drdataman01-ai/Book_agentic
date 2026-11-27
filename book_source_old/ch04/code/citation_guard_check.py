import re
CITE = re.compile(r"\[([A-Z]{2,6}-[A-Z]+-v\d+) §[\d.]+\]")
text = ("UK employees receive 25 days of annual leave plus bank holidays "
        "[UK-LEAVE-v7 §2.1]. Up to 5 days may be carried over [UK-LEAVE-v7 §4.3] "
        "with your manager's approval [GLOBAL-YEAREND-v2 §1].")
print(sorted(set(CITE.findall(text))))
