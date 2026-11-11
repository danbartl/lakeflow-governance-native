import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest

spec = importlib.util.spec_from_file_location(
    "page_publish", Path(__file__).parents[1] / "publish.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
DOMAIN = "domains/12345678-1234-4234-8234-123456789012"
PAGE = "pages/12345678-1234-4234-8234-123456789013"
REQUEST = "12345678-1234-4234-8234-123456789014"


def concept():
    return module.Concept.model_validate_json(
        (Path(__file__).parents[1] / "concepts/account-balance.json").read_text()
    )


def test_create_defaults_to_draft_and_reuses_idempotency_key():
    prepared = module.request(concept(), DOMAIN, request_id=REQUEST)
    assert prepared["body"]["state"] == "DRAFT"
    assert prepared["query"] == {"request_id": REQUEST}
    assert "page" not in prepared["body"]  # REST expects the Page fields directly.
    assert prepared == module.request(concept(), DOMAIN, request_id=REQUEST)


def test_update_preserves_publication_unless_explicitly_requested():
    prepared = module.request(concept(), DOMAIN, page_name=PAGE)
    assert "state" not in prepared["body"]
    client = Mock()
    client.do.side_effect = [
        {"domain": DOMAIN, "body": "<!-- concept-id: sandbox.account_balance -->\nold"},
        {"name": PAGE},
    ]
    assert module.apply(client, prepared, concept(), DOMAIN) == {"name": PAGE}
    assert client.do.call_count == 2


@pytest.mark.parametrize("current", [{}, {"domain": DOMAIN, "body": "someone else's definition"}])
def test_update_refuses_unrelated_page(current):
    client = Mock()
    client.do.return_value = current
    with pytest.raises(ValueError, match="refusing"):
        module.apply(client, module.request(concept(), DOMAIN, PAGE), concept(), DOMAIN)
    assert client.do.call_count == 1


def test_publish_is_explicit():
    prepared = module.request(concept(), DOMAIN, PAGE, publish=True)
    assert prepared["body"]["state"] == "PUBLISHED"
    assert prepared["query"]["update_mask"].endswith(",state")


@pytest.mark.parametrize("domain,request_id", [("domains/../../x", REQUEST), (DOMAIN, None)])
def test_invalid_resource_or_missing_retry_key_rejected(domain, request_id):
    with pytest.raises(ValueError):
        module.request(concept(), domain, request_id=request_id)
