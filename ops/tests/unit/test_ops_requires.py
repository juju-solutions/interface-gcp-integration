# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
import io
import json
import unittest.mock as mock
from pathlib import Path

import pytest
import yaml
import ops
import ops.testing
from ops.interface_gcp.requires import GCPIntegrationRequires, INSTANCE_URL, ZONE_URL
import os


class MyCharm(ops.CharmBase):
    gcp_meta = ops.RelationMeta(
        ops.RelationRole.requires, "gcp", {"interface": "gcp-integration"}
    )

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.gcp = GCPIntegrationRequires(self)


@pytest.fixture(autouse=True)
def juju_enviro():
    with mock.patch.dict(
        os.environ, {"JUJU_MODEL_UUID": "cf67b90e-7201-4f23-8c0a-e1f453f1dc2e"}
    ):
        yield


@pytest.fixture(scope="function")
def harness():
    harness = ops.testing.Harness(MyCharm)
    harness.framework.meta.name = "test"
    harness.framework.meta.relations = {
        MyCharm.gcp_meta.relation_name: MyCharm.gcp_meta
    }
    harness.set_model_name("test/0")
    harness.begin_with_initial_hooks()
    yield harness


@pytest.fixture(autouse=True)
def mock_url():
    with mock.patch("ops.interface_gcp.requires.urlopen") as urlopen:

        def urlopener(req):
            if req.full_url == INSTANCE_URL:
                return io.BytesIO(b"i-abcdefghijklmnopq")
            elif req.full_url == ZONE_URL:
                return io.BytesIO(b"us-east1")

        urlopen.side_effect = urlopener
        yield urlopen


@pytest.fixture()
def sent_data():
    yield yaml.safe_load(Path("tests/data/gcp_sent.yaml").open())


@pytest.mark.parametrize(
    "event_type", [None, ops.RelationBrokenEvent], ids=["unrelated", "dropped relation"]
)
def test_is_ready_no_relation(harness, event_type):
    event = ops.ConfigChangedEvent(None)
    assert harness.charm.gcp.is_ready is False
    assert "Missing" in harness.charm.gcp.evaluate_relation(event)

    rel_id = harness.add_relation("gcp", "remote")
    assert harness.charm.gcp.is_ready is False

    rel = harness.model.get_relation("gcp", rel_id)
    harness.add_relation_unit(rel_id, "remote/0")
    event = ops.RelationJoinedEvent(None, rel)
    assert "Waiting" in harness.charm.gcp.evaluate_relation(event)

    event = ops.RelationChangedEvent(None, rel)
    harness.update_relation_data(rel_id, "remote/0", {"completed": "{}"})
    assert "Waiting" in harness.charm.gcp.evaluate_relation(event)

    if event_type:
        harness.remove_relation(rel_id)
        event = event_type(None, rel)
        assert "Missing" in harness.charm.gcp.evaluate_relation(event)


def test_is_ready_success(harness):
    chksum = "e595c1619f2c63d4d237b20af77b1451b2912e878ce3dff666e49de2794df745"
    completed = '{"i-abcdefghijklmnopq": "%s"}' % chksum
    harness.add_relation("gcp", "remote", unit_data={"completed": completed})
    assert harness.charm.gcp.is_ready is True
    event = ops.ConfigChangedEvent(None)
    assert harness.charm.gcp.evaluate_relation(event) is None


@pytest.mark.parametrize(
    "method_name, args",
    [
        ("tag_instance", 'tags={"tag1": "val1", "tag2": "val2"}'),
        ("enable_instance_inspection", None),
        ("enable_network_management", None),
        ("enable_security_management", None),
        ("enable_block_storage_management", None),
        ("enable_dns_management", None),
        ("enable_object_storage_access", None),
        ("enable_object_storage_management", None),
    ],
)
def test_request_simple(harness, method_name, args, sent_data):
    rel_id = harness.add_relation("gcp", "remote")
    method = getattr(harness.charm.gcp, method_name)
    kwargs = {}
    if args:
        kw, val = args.split("=")
        kwargs[kw] = json.loads(val)
    method(**kwargs)
    data = harness.get_relation_data(rel_id, harness.charm.unit.name)
    assert data.pop("requested")
    for each, value in data.items():
        assert sent_data[each] == value
