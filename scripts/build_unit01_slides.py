"""Build the standalone U00-U03 teaching deck without changing the 24-page review deck."""
from __future__ import annotations

import json
import math
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "docs" / "lessons"
SOURCE = LESSONS / "unit01"

# Stable topic ids; this volume has its own teaching order and reading-position key.
ORDER = [
    "unit-cover", "architecture-atlas",
    "model-agent", "context-parameters", "trace-diagnosis", "state-lifetimes", "image-pipeline", "experiment-contract",
    "next-token", "vocabulary-logits", "softmax-basics", "cross-entropy", "gradient-meaning", "gradient-chain", "parameter-update",
    "label-shift", "teacher-forcing", "causal-probe", "loss-mask", "tokenization", "split-generalization", "objective-choice",
    "architecture-types", "token-embedding", "position-encoding", "input-representation", "tensor-notation",
    "encoder-self-attention", "symbols", "qkv", "scores", "scaling-assumptions", "scaling-derivation", "mask", "encoder-visibility", "weighted-read", "multihead", "output-projection",
    "encoder-case-setup", "encoder-case-attention", "residual", "layernorm-stats", "layernorm-affine", "normalization-purpose", "normalization-tradeoffs",
    "encoder-attention-addnorm", "encoder-case-addnorm", "encoder-route", "encoder-ffn", "ffn-shapes", "ffn-nonlinearity", "encoder-second-norm",
    "encoder-case-ffn", "encoder-case-output", "encoder-stack", "encoder-summary",
    "decoder-input", "decoder-self-attention", "decoder-first-norm", "cross-sources", "cross-shapes", "cross-mask", "decoder-cross-norm", "decoder-ffn", "decoder-last-norm", "decoder-block", "vocabulary-head", "decoder-only",
    "implementation-plan", "initialization", "attention-code", "preln-code", "training-loop", "adamw", "dropout", "tiny-overfit", "gradient-accumulation", "checkpoint",
    "generation", "kv-cache", "cache-offset", "cache-equivalence", "memory-budget", "cpu-to-cuda", "benchmarking",
    "experiment-matrix", "paper-reading", "normalization-history", "attention-efficiency", "parallel-generation", "image-next",
    "test-u00-u01", "review", "test-u03", "delivery-state", "source-index",
]

REVIEW_IDS = {
    "symbols", "qkv", "scores", "mask", "weighted-read", "multihead", "output-projection", "residual",
    "layernorm-stats", "layernorm-affine", "normalization-purpose", "normalization-tradeoffs",
}
ENCODER_IDS = {"encoder-route", "encoder-ffn", "ffn-shapes", "ffn-nonlinearity", "encoder-second-norm", "encoder-stack"}
CROSS_IDS = {"cross-sources", "cross-shapes", "cross-mask"}


def sections(text: str) -> dict[str, str]:
    found = {}
    for match in re.finditer(r'<section class="slide" id="([^"]+)"[\s\S]*?</section>', text):
        if match[1] in found:
            raise ValueError(f"duplicate slide id: {match[1]}")
        found[match[1]] = match[0]
    return found


def mm(a, b):
    assert a and b and len(a[0]) == len(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def add(a, b):
    assert len(a) == len(b) and len(a[0]) == len(b[0])
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def ln(a, eps=1e-5):
    output, means, variances = [], [], []
    for row in a:
        mean = sum(row) / len(row)
        variance = sum((x - mean) ** 2 for x in row) / len(row)
        means.append(mean)
        variances.append(variance)
        output.append([(x - mean) / math.sqrt(variance + eps) for x in row])
    return output, means, variances


def encoder_example():
    h = [[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]]
    wq = [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]
    wv = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    q, k, value = mm(h, wq), mm(h, wq), mm(h, wv)
    score = [[sum(x * y for x, y in zip(qr, kr)) / math.sqrt(2) for kr in k] for qr in q]
    attention = []
    for row in score:
        exp = [math.exp(x - max(row)) for x in row]
        attention.append([x / sum(exp) for x in exp])
    read = mm(attention, value)
    residual1 = add(h, read)
    y, mean1, variance1 = ln(residual1)
    w1 = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 1.0, 1.0]]
    w2 = [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 1.0, 1.0]]
    hidden = mm(y, w1)
    active = [[max(0.0, x) for x in row] for row in hidden]
    ffn = mm(active, w2)
    residual2 = add(y, ffn)
    result, mean2, variance2 = ln(residual2)
    matrices = dict(H=h, WQ=wq, WK=wq, WV=wv, WO=wv, Q=q, K=k, V=value, scores=score, A=attention, O=read,
                    residual1=residual1, Y=y, W1=w1, W2=w2, hidden=hidden, activated=active, F=ffn, residual2=residual2, C=result)
    assert all(abs(sum(row) - 1) < 1e-12 for row in attention)
    assert attention[0][1] > 0  # the encoder can read the later, already-known source position
    assert all(abs(sum(row)) < 1e-12 for row in y + result)
    assert len(result) == len(h) and len(result[0]) == len(h[0])
    return {
        "scope": "Deterministic arithmetic for one untrained, single-head encoder block; input H is given, not produced by a trained tokenizer/model.",
        "config": {"source_positions": 2, "d_model": 3, "d_k": 2, "d_v": 3, "d_ff": 4, "heads": 1, "layers": 1, "eps": 1e-5,
                   "biases": "all zero", "layernorm_gamma": [1, 1, 1], "layernorm_beta": [0, 0, 0], "mask": "all source positions valid"},
        "matrices": matrices,
        "rounded": {key: [[round(x, 3) for x in row] for row in matrix] for key, matrix in matrices.items()},
        "statistics": {"mean1": mean1, "variance1": variance1, "mean2": mean2, "variance2": variance2},
    }


def main():
    base = (LESSONS / "transformer-slides.html").read_text(encoding="utf-8")
    bank = sections(base)
    for path in sorted(SOURCE.glob("*.html")):
        for slide_id, content in sections(path.read_text(encoding="utf-8")).items():
            if slide_id in bank:
                raise ValueError(f"duplicate across sources: {slide_id}")
            bank[slide_id] = content
    assert len(ORDER) == len(set(ORDER)), "duplicate order id"
    missing = set(ORDER) - bank.keys()
    if missing:
        raise ValueError(f"slides missing: {sorted(missing)}")
    rendered, catalog = [], []
    for ordinal, slide_id in enumerate(ORDER, 1):
        content = bank[slide_id]
        if slide_id in REVIEW_IDS:
            chapter, study = "U02 · 注意力与归一化", "复习"
        elif slide_id in ENCODER_IDS:
            chapter, study = "U02 · 完整 Encoder", "补齐"
        elif slide_id in CROSS_IDS:
            chapter, study = "U02 · Decoder 与交叉读取", "接回"
        elif slide_id == "review":
            chapter, study = "自测与实验", "自测"
        else:
            chapter = re.search(r'data-chapter="([^"]+)"', content)[1]
            study = re.search(r'data-study="([^"]+)"', content)[1]
        content = re.sub(r'data-chapter="[^"]+"', f'data-chapter="{chapter}"', content, count=1)
        if 'data-study="' not in content:
            content = content.replace(' aria-roledescription=', f' data-study="{study}" aria-roledescription=', 1)
        # Only the first page starts visible; navigation uses stable topic ids.
        opening, rest = content.split(">", 1)
        opening = re.sub(r"\s+hidden(?=\s|$)", "", opening)
        if ordinal > 1:
            opening += " hidden"
        content = opening + ">" + rest
        rendered.append(content)
        title = re.search(r"<h[12]>([\s\S]*?)</h[12]>", content)[1]
        title = unescape(re.sub(r"<[^>]+>", "", title))
        catalog.append(dict(page=ordinal, id=slide_id, chapter=chapter, study=study, title=title))
    html = re.sub(r'(<main class="deck" id="transformer-deck">)[\s\S]*?(</main>)', lambda m: m[1] + "\n" + "\n\n".join(rendered) + "\n" + m[2], base, count=1)
    html = html.replace("Transformer · 翻页课件", "第一单元 U00–U03 · 完整课件")
    html = re.sub(r'<a[^>]*data-complete-book[^>]*>[\s\S]*?</a>', '<a href="transformer-slides.html" target="_blank" rel="noreferrer">24 页回顾版</a>', html, count=1)
    html = html.replace('href="#encoder-route" data-jump="encoder-route">Encoder 章节', 'href="#architecture-atlas" data-jump="architecture-atlas">架构导航')
    html = html.replace("projectllm-transformer-slides-position-v1", "projectllm-unit01-complete-position-v1")
    html = html.replace('aria-valuemax="24"', f'aria-valuemax="{len(ORDER)}"').replace("第 1 / 24 页", f"第 1 / {len(ORDER)} 页")
    html = html.replace("chapter.textContent=slide.dataset.chapter;", "chapter.textContent=slide.dataset.chapter+' · '+slide.dataset.study;")
    html = html.replace("par(v('B'))", "par(sub(v('N'),v('h')))")
    case = encoder_example()
    (LESSONS / "unit-01-encoder-example.json").write_text(json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (LESSONS / "unit-01-slide-index.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    extra = (SOURCE / "formulas.js").read_text(encoding="utf-8")
    injection = "\n  const encoderCase = " + json.dumps(case["rounded"], ensure_ascii=False) + ";\n" + extra + "\n"
    needle = "  document.querySelectorAll('[data-math]').forEach"
    assert html.count(needle) == 1
    html = html.replace(needle, injection + needle)
    html = html.replace("  /* UNIT_EXTRA_CSS */", "")
    html = html.replace("</style>", "\n" + (SOURCE / "extra.css").read_text(encoding="utf-8") + "\n</style>", 1)
    # The full atlas has module links and no permanent progress highlight.
    old_start = html.index("  function architecture(host){")
    old_end = html.index("  document.querySelectorAll('[data-diagram=", old_start)
    html = html[:old_start] + (SOURCE / "atlas.js").read_text(encoding="utf-8") + "\n" + html[old_end:]
    html = html.replace("decodeURIComponent(location.hash.slice(1))", "location.hash.slice(1)")
    (LESSONS / "unit-01-complete-slides.html").write_text(html, encoding="utf-8")
    coverage = ["# 第一单元 U00–U03 完整课件覆盖清单", "", f"共 {len(ORDER)} 页。备课完成不等于授课、独立掌握或模型实验完成。", "",
                "回顾：此前已有讨论；补齐：补足计算链；预备：尚待逐项讲解；实验/自测：给出目标与验收，未伪造执行成绩。", "",
                "| 页 | 单元 / 章节 | 分类 | 固定主题 |", "| --- | --- | --- | --- |"]
    for item in catalog:
        coverage.append(f'| {item["page"]} | {item["chapter"]} | {item["study"]} | [{item["title"]}](unit-01-complete-slides.html#{item["id"]}) |')
    coverage += ["", "原 24 页回顾版的页面 ID 和页序保持不变。完整版独立保存阅读位置，架构图各模块链接到固定章节。", "",
                 "已提供：定义、公式、作用、形状、数值算例、问题与答案、实现阅读卡、实验验收与原始来源。", "",
                 "实验边界：本次完成文档、确定性小矩阵算例与页面验证；课程教学模型训练、CUDA 性能与真实图片模型实验仍须按 E01/V01 实施。", "",
                 "源码：unit01/ 下的补充页面与公式；构建：python3 scripts/build_unit01_slides.py。", ""]
    (LESSONS / "unit-01-coverage.md").write_text("\n".join(coverage), encoding="utf-8")
    print(json.dumps({"pages": len(ORDER), "output": str(LESSONS / "unit-01-complete-slides.html"), "case_C": case["matrices"]["C"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
