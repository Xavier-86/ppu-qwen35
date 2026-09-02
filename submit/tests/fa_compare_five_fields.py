# Five-field parity check between two benchmark result JSONs.
# Compares per-sample question_id / parsed_answer / correct / token_count /
# validation_errors, plus top-level accuracy. Exit 1 on any mismatch.
import json
import sys

FIELDS = ("parsed_answer", "correct", "token_count", "validation_errors")


def rows_by_qid(d):
    rows = d.get("answers") or d.get("results") or d.get("samples") or []
    out = {}
    for r in rows:
        key = r.get("question_id", r.get("index", r.get("idx", r.get("id"))))
        out[key] = r
    return out


def main():
    old_path, new_path = sys.argv[1], sys.argv[2]
    old = json.load(open(old_path))
    new = json.load(open(new_path))
    oa, na = rows_by_qid(old), rows_by_qid(new)
    common = sorted(set(oa) & set(na))
    only_old = sorted(set(oa) - set(na))
    only_new = sorted(set(na) - set(oa))
    flips = {f: [] for f in FIELDS}
    for k in common:
        for f in FIELDS:
            if oa[k].get(f) != na[k].get(f):
                flips[f].append(k)
    total = sum(len(v) for v in flips.values())
    acc_old = old.get("accuracy")
    acc_new = new.get("accuracy")
    print(f"old={old_path} acc={acc_old}")
    print(f"new={new_path} acc={acc_new}")
    print(f"common={len(common)} only_old={only_old} only_new={only_new}")
    for f in FIELDS:
        print(f"  {f}: flipped={len(flips[f])}")
        for k in flips[f][:10]:
            print(f"    idx={k}: {oa[k].get(f)} -> {na[k].get(f)}")
    print(f"TOTAL_FIELD_DIFFS={total}")
    sys.exit(1 if (total or only_old or only_new or acc_old != acc_new) else 0)


if __name__ == "__main__":
    main()
