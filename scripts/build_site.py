"""Build docs/assets/data.js for the static results page from results/baseline_eval_50.

Usage:  python scripts/build_site.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results" / "baseline_eval_50"
OUT = ROOT / "docs" / "assets" / "data.js"

CRIT = ["correctness", "completeness", "urdu_fluency", "relevance"]

# display names and the GGUF repos used in the notebook
MODEL_META = {
    "Gemma-4-E2B [Q4_0]": {"short": "Gemma 4 E2B", "family": "Google Gemma 4", "quant": "Q4_0", "repo": "ggml-org/gemma-4-E2B-it-GGUF"},
    "Tiny-Aya-Fire [Q4_K_M]": {"short": "Tiny Aya Fire", "family": "Cohere Labs Aya", "quant": "Q4_K_M", "repo": "CohereLabs/tiny-aya-fire-GGUF"},
    "Qwen3.5-2B [Q4_K_M]": {"short": "Qwen3.5 2B", "family": "Alibaba Qwen3.5", "quant": "Q4_K_M", "repo": "unsloth/Qwen3.5-2B-GGUF"},
    "Qwen3-1.7B [Q4_K_M]": {"short": "Qwen3 1.7B", "family": "Alibaba Qwen3", "quant": "Q4_K_M", "repo": "unsloth/Qwen3-1.7B-GGUF"},
}


def records(df):
    return json.loads(df.to_json(orient="records", force_ascii=False))


def main():
    summ = pd.read_csv(RES / "summary" / "summary.csv")
    scored = pd.read_csv(RES / "answers" / "answers_scored.csv", encoding="utf-8-sig")
    cpu = pd.read_csv(RES / "answers" / "answers_cpu_timing.csv")
    judges = pd.read_csv(RES / "judging" / "judge_scores_long.csv", encoding="utf-8-sig")
    agree = pd.read_csv(RES / "summary" / "judge_agreement.csv")
    sig = pd.read_csv(RES / "summary" / "significance_tests.csv")
    rec = json.loads((RES / "summary" / "recommended_model.json").read_text(encoding="utf-8"))
    cfg = json.loads((RES / "summary" / "run_config.json").read_text(encoding="utf-8"))

    models = summ.model.tolist()  # already sorted by overall score

    # share of answers that both judges rate as mostly correct (mean correctness >= 4)
    good = scored.assign(good=scored.correctness >= 4).groupby("model").good.mean().mul(100).round(0)
    summ["good_answers_pct"] = summ.model.map(good)
    for key in ["short", "family", "quant", "repo"]:
        summ[key] = summ.model.map(lambda m: MODEL_META[m][key])

    by_cat = scored.pivot_table(index="model", columns="category", values="quality", aggfunc="mean").round(2)
    by_crop = scored.pivot_table(index="model", columns="crop", values="quality", aggfunc="mean").round(2)
    per_judge = judges.groupby(["judge", "model"])[CRIT].mean().round(2).reset_index()

    # one record per question with all four answers
    reasons = judges.set_index(["model", "id", "judge"]).reason
    questions = []
    for qid, g in scored.groupby("id", sort=False):
        q = g.iloc[0]
        answers = {}
        for _, r in g.iterrows():
            answers[r.model] = {
                "answer": r.answer, "words": int(r.words), "looping": bool(r.looping), "harmful": bool(r.harmful),
                "finish": r.finish, "latency_s": r.latency_s, "ttft_s": r.ttft_s, "gen_tok_s": r.gen_tok_s,
                "urdu_pct": r.urdu_pct, "chrf": r.chrf, "sim": r.sim_bge_m3,
                **{c: round(float(r[c]), 2) for c in CRIT}, "quality": round(float(r.quality), 2),
                "overall": round(float(r.overall), 2),
                "reasons": {j: reasons.get((r.model, qid, j), "") for j in judges.judge.unique()},
            }
        questions.append({"id": qid, "crop": q.crop, "category": q.category, "question": q.question,
                          "reference": q.reference, "answers": answers})
    questions.sort(key=lambda x: x["id"])

    data = {
        "models": models,
        "summary": records(summ),
        "by_category": {m: by_cat.loc[m].to_dict() for m in models},
        "by_crop": {m: by_crop.loc[m].to_dict() for m in models},
        "per_judge": records(per_judge),
        "judge_agreement": records(agree),
        "significance": records(sig),
        "cpu_timing": records(cpu),
        "recommended": rec,
        "config": cfg,
        "questions": questions,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.EVAL = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e3:.0f} KB, {len(questions)} questions)")


if __name__ == "__main__":
    main()
