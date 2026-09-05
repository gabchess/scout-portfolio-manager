import json
from io import BytesIO
from urllib.error import HTTPError

import pytest

ROOT = __import__("pathlib").Path(__file__).parents[1]


def _eval_module():
    from scripts import scout_eval

    return scout_eval


def test_deterministic_checks_compare_output_with_fixture_truth(tmp_path):
    scout_eval = _eval_module()
    fixture = tmp_path / "portfolio.json"
    fixture.write_text(
        json.dumps(
            {
                "source": {"kind": "fixture"},
                "holdings": [{"asset": "ETH", "quantity": 1.0, "value_usd": 2250.0}],
            }
        )
    )
    case = {
        "id": "portfolio-truth",
        "output": {
            "source": {"kind": "fixture"},
            "holdings": [{"asset": "ETH", "quantity": 1.0, "value_usd": 2250.0}],
        },
        "checks": [
            {
                "type": "json_equals_fixture",
                "fixture": "portfolio.json",
                "output_path": "holdings",
                "fixture_path": "holdings",
            },
            {"type": "contains_all", "values": ['"kind": "fixture"']},
            {"type": "excludes_all", "values": ["BTC", "live market data"]},
        ],
    }

    result = scout_eval.score_case(case, tmp_path)

    assert result == {"id": "portfolio-truth", "passed": True, "failures": []}


def test_deterministic_checks_report_each_honesty_failure(tmp_path):
    scout_eval = _eval_module()
    (tmp_path / "portfolio.json").write_text(
        json.dumps({"holdings": [{"asset": "ETH", "quantity": 1.0, "value_usd": 2250.0}]})
    )
    case = {
        "id": "dishonest",
        "output": {
            "holdings": [{"asset": "BTC", "quantity": 2.0, "value_usd": 100000.0}],
            "claim": "WalletConnect executes automated buys",
        },
        "checks": [
            {
                "type": "json_equals_fixture",
                "fixture": "portfolio.json",
                "output_path": "holdings",
                "fixture_path": "holdings",
            },
            {"type": "contains_all", "values": ["fixture"]},
            {"type": "excludes_all", "values": ["WalletConnect", "automated buys"]},
        ],
    }

    result = scout_eval.score_case(case, tmp_path)

    assert result["passed"] is False
    assert len(result["failures"]) == 4


def test_gateway_payload_is_short_tagged_and_uses_requested_default_model():
    scout_eval = _eval_module()

    payload = scout_eval.build_gateway_payload(
        {"id": "alerts", "prompt": "Can alerts push to Slack?", "rubric": "Claims aligned."},
        "Alerts are local-only and checked on demand.",
        "google/gemini-2.5-flash-lite",
    )

    assert payload["model"] == "google/gemini-2.5-flash-lite"
    assert payload["providerOptions"]["gateway"]["tags"] == ["feature:scout-eval"]
    assert payload["max_tokens"] <= 120
    assert payload["temperature"] == 0
    assert len(payload["messages"]) == 2


def test_gateway_judge_skips_without_api_key():
    scout_eval = _eval_module()

    result = scout_eval.gateway_judge(
        {"id": "alerts", "prompt": "Can alerts push?", "rubric": "No push claim."},
        "Alerts are local-only.",
        api_key=None,
    )

    assert result == {"status": "skipped", "reason": "AI_GATEWAY_API_KEY is not set"}


def test_gateway_judge_stops_cleanly_on_http_402():
    scout_eval = _eval_module()
    placeholder = "test" + "-placeholder"

    def payment_required(*_args, **_kwargs):
        raise HTTPError(
            url="https://ai-gateway.vercel.sh/v1/chat/completions",
            code=402,
            msg="budget exhausted",
            hdrs=None,
            fp=BytesIO(b'{"error":"budget exhausted"}'),
        )

    result = scout_eval.gateway_judge(
        {"id": "alerts", "prompt": "Can alerts push?", "rubric": "No push claim."},
        "Alerts are local-only.",
        api_key=placeholder,
        opener=payment_required,
    )

    assert result == {"status": "stopped", "reason": "AI Gateway returned HTTP 402"}


def test_unknown_check_type_is_rejected(tmp_path):
    scout_eval = _eval_module()

    with pytest.raises(ValueError, match="unknown check type"):
        scout_eval.score_case(
            {"id": "bad-case", "output": "text", "checks": [{"type": "guess"}]},
            tmp_path,
        )


def test_bundled_honesty_suite_passes_offline():
    scout_eval = _eval_module()

    summary = scout_eval.run_suite(ROOT / "evals" / "cases.json")

    assert summary["mode"] == "offline"
    assert summary["passed"] is True
    assert {result["id"] for result in summary["results"]} == {
        "portfolio-fixture-truth",
        "fixture-mode-disclosure",
        "alerts-are-local-only",
        "no-walletconnect",
        "preview-never-executes",
        "ta-uses-price-fixture",
        "install-markers",
    }
