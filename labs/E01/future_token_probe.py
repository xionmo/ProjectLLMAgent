"""Fixed-weight attention reference: test whether future tokens affect earlier logits.

Uses only Python's standard library. Two small attention layers plus a vocabulary
projection; this is not a trained language model or a complete Transformer.
No training, optimizer, model downloads, GPU work, or file writes are performed.
"""
import hashlib
import json
import math
import random


VOCAB = ["BOS", "2", "+", "3", "=", "5", "8", "EOS"]
WIDTH = 4
LAYERS = 2


def make_parameters():
    rng = random.Random(19)

    def matrix(rows, columns):
        return [[rng.uniform(-0.6, 0.6) for _ in range(columns)] for _ in range(rows)]

    return {
        "embedding": matrix(len(VOCAB), WIDTH),
        "positions": matrix(8, WIDTH),
        "layers": [
            {name: matrix(WIDTH, WIDTH) for name in ("q", "k", "v")}
            for _ in range(LAYERS)
        ],
        "head": matrix(WIDTH, len(VOCAB)),
    }


def project(vector, matrix):
    return [sum(vector[i] * matrix[i][j] for i in range(len(vector)))
            for j in range(len(matrix[0]))]


def softmax(scores):
    maximum = max(scores)
    weights = [math.exp(value - maximum) for value in scores]
    total = sum(weights)
    return [value / total for value in weights]


def forward(tokens, parameters, causal_layers):
    if len(causal_layers) != LAYERS:
        raise ValueError("Specify one visibility rule for each layer.")
    states = [
        [a + b for a, b in zip(parameters["embedding"][VOCAB.index(token)],
                              parameters["positions"][position])]
        for position, token in enumerate(tokens)
    ]
    all_attention = []
    for layer, causal in zip(parameters["layers"], causal_layers):
        queries = [project(row, layer["q"]) for row in states]
        keys = [project(row, layer["k"]) for row in states]
        values = [project(row, layer["v"]) for row in states]
        attention = []
        next_states = []
        for i, query in enumerate(queries):
            scores = [
                sum(a * b for a, b in zip(query, key)) / math.sqrt(WIDTH)
                if not causal or j <= i else -math.inf
                for j, key in enumerate(keys)
            ]
            weights = softmax(scores)
            mixed = [sum(weights[j] * values[j][d] for j in range(len(tokens)))
                     for d in range(WIDTH)]
            # A residual path, but no FFN or normalization in this reference.
            next_states.append([a + b for a, b in zip(states[i], mixed)])
            attention.append(weights)
        states = next_states
        all_attention.append(attention)
    return [project(row, parameters["head"]) for row in states], all_attention


def difference(left, right):
    return max(abs(a - b) for a, b in zip(left, right))


def digest(parameters):
    encoded = json.dumps(parameters, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main():
    parameters = make_parameters()
    before = digest(parameters)
    original = ["BOS", "2", "+", "3", "=", "5"]
    causal, attention = forward(original, parameters, [True, True])
    unmasked, _ = forward(original, parameters, [False, False])
    final_layer_only, _ = forward(original, parameters, [False, True])
    checks = []
    for query_position in range(len(original) - 1):
        for future_position in range(query_position + 1, len(original)):
            changed = original.copy()
            changed[future_position] = "8"
            new_causal, _ = forward(changed, parameters, [True, True])
            new_unmasked, _ = forward(changed, parameters, [False, False])
            new_final_only, _ = forward(changed, parameters, [False, True])
            checks.append({
                "query_position": query_position,
                "changed_future_position": future_position,
                "causal_max_logit_change": difference(causal[query_position], new_causal[query_position]),
                "unmasked_max_logit_change": difference(unmasked[query_position], new_unmasked[query_position]),
                "only_final_layer_masked_max_logit_change":
                    difference(final_layer_only[query_position], new_final_only[query_position]),
            })
    # Compare the same prefix processed alone and as part of the longer input.
    prefix_only, _ = forward(original[:5], parameters, [True, True])
    prefix_difference = difference(causal[4], prefix_only[4])
    assert all(case["causal_max_logit_change"] < 1e-12 for case in checks)
    assert max(case["unmasked_max_logit_change"] for case in checks) > 1e-6
    assert max(case["only_final_layer_masked_max_logit_change"] for case in checks) > 1e-6
    assert prefix_difference < 1e-12
    assert all(weights[j] == 0.0 for layer in attention
               for i, weights in enumerate(layer) for j in range(i + 1, len(weights)))
    assert before == digest(parameters)
    selected = next(case for case in checks
                    if case["query_position"] == 4 and case["changed_future_position"] == 5)
    print(json.dumps({
        "scope": "Fixed-weight attention mechanism check; not a trained-LM benchmark.",
        "original": original,
        "counterfactual": ["BOS", "2", "+", "3", "=", "8"],
        "observed_position": "input '='; next-token logits",
        "selected_case": selected,
        "future_perturbations_checked": len(checks),
        "all_causal_checks_passed": True,
        "prefix_only_logit_difference": prefix_difference,
        "weights_unchanged": before == digest(parameters),
        "optimizer_steps": 0,
        "note": "Unmasked runs are positive controls for this reference. Passing a finite set of checks cannot prove an arbitrary implementation is universally causal.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
