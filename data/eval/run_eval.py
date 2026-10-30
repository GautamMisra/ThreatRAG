import json
import re
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://localhost:8000/analyze"

DATASET_PATH = Path(__file__).parent / "eval_dataset.json"

RESULTS_PATH = Path(__file__).parent / "evaluation_results.json"

REQUEST_TIMEOUT = 300


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize(text):
    """
    Normalize text for case-insensitive keyword matching.
    """

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def threat_text(threat):
    """
    Combine important fields from a generated threat
    into one searchable string.
    """

    fields = [
        threat.get("threat", ""),
        threat.get("description", ""),
        threat.get("summary", ""),
        threat.get("mitigation", ""),
        threat.get("stride_category", ""),
        threat.get("source", ""),
        threat.get("citation", ""),
    ]

    return normalize(
        " ".join(
            str(x)
            for x in fields
            if x
        )
    )


# ============================================================
# THREAT MATCHING
# ============================================================

def threat_matches(expected, generated):
    """
    Match an expected threat against a generated threat.

    A match requires:

    1. STRIDE category matches
    2. At least one expected keyword appears
       in the generated threat
    """

    expected_stride = normalize(
        expected.get("stride", "")
    )

    generated_stride = normalize(
        generated.get("stride_category", "")
    )

    if not expected_stride or not generated_stride:
        return False

    stride_match = (
        expected_stride in generated_stride
        or generated_stride in expected_stride
    )

    if not stride_match:
        return False

    generated_text = threat_text(generated)

    for keyword in expected.get("keywords", []):

        if normalize(keyword) in generated_text:
            return True

    return False


# ============================================================
# BUILD API PAYLOAD
# ============================================================

def build_payload(system):
    """
    Convert the evaluation dataset into the exact
    SystemDescription format expected by FastAPI.

    API expects:

    {
        "components": [
            {
                "name": "...",
                "technology": "..."
            }
        ],
        "data_flows": [
            {
                "source": "...",
                "destination": "...",
                "description": "..."
            }
        ],
        "trust_boundaries": [...]
    }
    """

    components = []

    for component in system.get("components", []):

        components.append(
            {
                "name": component.get(
                    "name",
                    component.get("component", "")
                ),
                "technology": component.get(
                    "technology",
                    ""
                )
            }
        )

    data_flows = []

    for flow in system.get("data_flows", []):

        data_flows.append(
            {
                "source": flow["source"],
                "destination": flow["destination"],
                "description": flow["description"]
            }
        )

    return {
        "components": components,
        "data_flows": data_flows,
        "trust_boundaries": system.get(
            "trust_boundaries",
            []
        )
    }


# ============================================================
# EXTRACT GENERATED THREATS
# ============================================================

def extract_generated_threats(response_json):
    """
    Extract threats from the current API response.

    Expected response:

    {
        "status": "success",
        "components": [
            {
                "component": "...",
                "technology": "...",
                "threat_model": {
                    "summary": "...",
                    "threats": [...]
                }
            }
        ]
    }
    """

    threats = []

    for component in response_json.get(
        "components",
        []
    ):

        threat_model = (
            component.get("threat_model")
            or {}
        )

        component_threats = (
            threat_model.get("threats", [])
        )

        for threat in component_threats:

            threat_copy = dict(threat)

            threat_copy["_component"] = (
                component.get(
                    "component",
                    component.get(
                        "name",
                        "Unknown"
                    )
                )
            )

            threats.append(threat_copy)

    return threats


# ============================================================
# EVALUATE ONE SYSTEM
# ============================================================

def evaluate_system(system):

    print("\n" + "=" * 72)

    print(
        f"Evaluating: {system['name']}"
    )

    print("=" * 72)

    payload = build_payload(system)

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:

            print(
                f"API ERROR: HTTP "
                f"{response.status_code}"
            )

            try:

                print(
                    "FastAPI response:"
                )

                print(
                    json.dumps(
                        response.json(),
                        indent=2
                    )
                )

            except ValueError:

                print(
                    "Raw response:",
                    response.text
                )

            return {
                "id": system["id"],
                "name": system["name"],
                "status": "ERROR",
                "error": (
                    f"HTTP "
                    f"{response.status_code}"
                ),
                "expected": len(
                    system.get(
                        "expected_threats",
                        []
                    )
                ),
                "generated": 0,
                "hits": 0,
                "misses": len(
                    system.get(
                        "expected_threats",
                        []
                    )
                ),
                "precision": 0.0,
                "recall": 0.0
            }

        result = response.json()

    except requests.exceptions.RequestException as e:

        print(
            f"ERROR calling API: {e}"
        )

        return {
            "id": system["id"],
            "name": system["name"],
            "status": "ERROR",
            "error": str(e),
            "expected": len(
                system.get(
                    "expected_threats",
                    []
                )
            ),
            "generated": 0,
            "hits": 0,
            "misses": len(
                system.get(
                    "expected_threats",
                    []
                )
            ),
            "precision": 0.0,
            "recall": 0.0
        }

    generated_threats = (
        extract_generated_threats(
            result
        )
    )

    expected_threats = system.get(
        "expected_threats",
        []
    )

    print(
        f"Generated threats: "
        f"{len(generated_threats)}"
    )

    print(
        f"Expected threats:  "
        f"{len(expected_threats)}"
    )

    # ========================================================
    # MATCH EXPECTED THREATS
    # ========================================================

    hits = 0

    matched_generated_indices = set()

    match_details = []

    for expected in expected_threats:

        match_index = None

        for index, generated in enumerate(
            generated_threats
        ):

            if index in matched_generated_indices:
                continue

            if threat_matches(
                expected,
                generated
            ):

                match_index = index

                break

        if match_index is not None:

            hits += 1

            matched_generated_indices.add(
                match_index
            )

            match_details.append(
                {
                    "expected": expected,
                    "generated": generated_threats[
                        match_index
                    ],
                    "matched": True
                }
            )

            print(
                f"[HIT]  "
                f"{expected['stride']} - "
                f"{expected['keywords'][0]}"
            )

        else:

            match_details.append(
                {
                    "expected": expected,
                    "generated": None,
                    "matched": False
                }
            )

            print(
                f"[MISS] "
                f"{expected['stride']} - "
                f"{expected['keywords'][0]}"
            )

    misses = (
        len(expected_threats) - hits
    )

    # ========================================================
    # METRICS
    # ========================================================

    precision = (
        hits / len(generated_threats)
        if generated_threats
        else 0.0
    )

    recall = (
        hits / len(expected_threats)
        if expected_threats
        else 0.0
    )

    print(
        f"\nPrecision: {precision:.2f}"
    )

    print(
        f"Recall:    {recall:.2f}"
    )

    return {
        "id": system["id"],
        "name": system["name"],
        "status": "SUCCESS",
        "expected": len(
            expected_threats
        ),
        "generated": len(
            generated_threats
        ),
        "hits": hits,
        "misses": misses,
        "precision": precision,
        "recall": recall,
        "matches": match_details,
        "generated_threats": generated_threats
    }


# ============================================================
# RUN EVALUATION
# ============================================================

def run_evaluation():

    print("\n")

    print("=" * 72)

    print(
        "ThreatModel-RAG Evaluation"
    )

    print("=" * 72)

    dataset = load_dataset()

    print(
        f"\nEvaluation systems: "
        f"{len(dataset)}"
    )

    print(
        f"API endpoint:       "
        f"{API_URL}"
    )

    results = []

    for system in dataset:

        result = evaluate_system(
            system
        )

        results.append(result)

    # ========================================================
    # OVERALL METRICS
    # ========================================================

    successful_results = [
        result
        for result in results
        if result["status"] == "SUCCESS"
    ]

    total_expected = sum(
        result["expected"]
        for result in successful_results
    )

    total_generated = sum(
        result["generated"]
        for result in successful_results
    )

    total_hits = sum(
        result["hits"]
        for result in successful_results
    )

    total_misses = sum(
        result["misses"]
        for result in successful_results
    )

    overall_precision = (
        total_hits / total_generated
        if total_generated
        else 0.0
    )

    overall_recall = (
        total_hits / total_expected
        if total_expected
        else 0.0
    )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n\n")

    print("=" * 72)

    print(
        "FINAL EVALUATION RESULTS"
    )

    print("=" * 72)

    print(
        f"\nSystems evaluated : "
        f"{len(successful_results)}"
    )

    print(
        f"Expected threats  : "
        f"{total_expected}"
    )

    print(
        f"Generated threats : "
        f"{total_generated}"
    )

    print(
        f"Correct matches   : "
        f"{total_hits}"
    )

    print(
        f"Misses            : "
        f"{total_misses}"
    )

    print(
        f"\nOverall Precision  : "
        f"{overall_precision:.2f}"
    )

    print(
        f"Overall Recall     : "
        f"{overall_recall:.2f}"
    )

    # ========================================================
    # PER-SYSTEM TABLE
    # ========================================================

    print("\n")

    print("-" * 92)

    print(
        f"{'System':30} "
        f"{'Expected':>10} "
        f"{'Generated':>10} "
        f"{'Hits':>8} "
        f"{'Precision':>10} "
        f"{'Recall':>10}"
    )

    print("-" * 92)

    for result in results:

        if result["status"] != "SUCCESS":
            continue

        print(
            f"{result['name'][:30]:30} "
            f"{result['expected']:>10} "
            f"{result['generated']:>10} "
            f"{result['hits']:>8} "
            f"{result['precision']:>10.2f} "
            f"{result['recall']:>10.2f}"
        )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    output = {
        "systems_evaluated": len(
            successful_results
        ),
        "expected_threats": total_expected,
        "generated_threats": total_generated,
        "correct_matches": total_hits,
        "misses": total_misses,
        "overall_precision": (
            overall_precision
        ),
        "overall_recall": (
            overall_recall
        ),
        "results": results
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print(
        f"\nDetailed results saved to:"
    )

    print(RESULTS_PATH)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_evaluation()