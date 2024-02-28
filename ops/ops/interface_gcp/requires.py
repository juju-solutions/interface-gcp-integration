# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""Implementation of gcp interface.

This only implements the requires side, currently, since the providers
is still using the Reactive Charm framework self.
"""
import json
from hashlib import sha256
import logging
import ops
import os
from functools import cached_property
from typing import Mapping, Optional
from urllib.parse import urljoin
from urllib.request import urlopen, Request


log = logging.getLogger(__name__)

# block size to read data from GCP metadata service
# (realistically, just needs to be bigger than ~20 chars)
READ_BLOCK_SIZE = 2048

# https://cloud.google.com/compute/docs/storing-retrieving-metadata
METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/"
INSTANCE_URL = urljoin(METADATA_URL, "instance/name")
ZONE_URL = urljoin(METADATA_URL, "instance/zone")
METADATA_HEADERS = {"Metadata-Flavor": "Google"}


def _request(url):
    req = Request(url, headers=METADATA_HEADERS)
    with urlopen(req) as fd:
        return fd.read(READ_BLOCK_SIZE).decode("utf8")


class GCPIntegrationRequires(ops.Object):
    """

    Interface to request integration access.

    Note that due to resource limits and permissions granularity, policies are
    limited to being applied at the charm level.  That means that, if any
    permissions are requested (i.e., any of the enable methods are called),
    what is granted will be the sum of those ever requested by any instance of
    the charm on this cloud.

    Labels, on the other hand, will be instance specific.

    Example usage:

    ```python

    class MyCharm(ops.CharmBase):

        def __init__(self, *args):
            super().__init__(*args)
            self.gcp = GCPIntegrationRequires(self)
            ...

        def request_gcp_integration():
            self.gcp.request_instance_tags({
                'tag1': 'value1',
                'tag2': None,
            })
            gcp.request_load_balancer_management()
            # ...

        def check_gcp_integration():
            if self.gcp.is_ready():
                update_config_enable_gcp()
        ```
    """

    _stored = ops.StoredState()

    def __init__(self, charm: ops.CharmBase, endpoint="gcp"):
        super().__init__(charm, f"relation-{endpoint}")
        self.endpoint = endpoint
        self.charm = charm

        events = charm.on[endpoint]
        self.framework.observe(events.relation_joined, self.send_instance_info)
        self._stored.set_default(instance_id=None, zone=None)

    @property
    def relation(self) -> Optional[ops.Relation]:
        """The relation to the integrator, or None."""
        relations = self.charm.model.relations.get(self.endpoint)
        return relations[0] if relations else None

    @property
    def _received(self) -> Mapping[str, str]:
        """
        Helper to streamline access to received data since we expect to only
        ever be connected to a single GCP integration application with a
        single unit.
        """
        if self.relation and self.relation.units:
            return self.relation.data[list(self.relation.units)[0]]
        return {}

    @property
    def _to_publish(self):
        """
        Helper to streamline access to received data since we expect to only
        ever be connected to a single GCP integration application with a
        single unit.
        """
        if self.relation:
            return self.relation.data[self.charm.model.unit]
        return {}

    def send_instance_info(self, _):
        info = {
            "charm": self.charm.meta.name,
            "instance": self.instance_id,
            "zone": self.zone,
            "model-uuid": os.environ["JUJU_MODEL_UUID"],
        }
        self._request(info)

    @cached_property
    def instance_id(self):
        """This unit's instance-id."""
        if self._stored.instance_id is None:
            self._stored.instance_id = _request(INSTANCE_URL)
        return self._stored.instance_id

    @cached_property
    def zone(self):
        """The zone this unit is in."""
        if self._stored.zone is None:
            zone = _request(ZONE_URL)
            self._stored.zone = zone.strip().split("/")[-1]
        return self._stored.zone

    @property
    def is_ready(self):
        """
        Whether or not the request for this instance has been completed.
        """
        requested = self._to_publish.get("requested")
        completed = json.loads(self._received.get("completed", "{}")).get(
            self.instance_id
        )
        return bool(requested and requested == completed)

    @property
    def credentials(self):
        return self._received["credentials"]

    def evaluate_relation(self, event) -> Optional[str]:
        """Determine if relation is ready."""
        no_relation = not self.relation or (
            isinstance(event, ops.RelationBrokenEvent)
            and event.relation is self.relation
        )
        if no_relation:
            return f"Missing required {self.endpoint}"
        if not self.is_ready:
            return f"Waiting for {self.endpoint}"
        return None

    @property
    def _expected_hash(self):
        return sha256(
            json.dumps(dict(self._to_publish), sort_keys=True).encode("utf8")
        ).hexdigest()

    def _request(self, keyvals):
        kwds = {key: json.dumps(val) for key, val in keyvals.items()}
        self._to_publish.update(**kwds)
        self._to_publish["requested"] = self._expected_hash

    def tag_instance(self, tags):
        """
        Request that the given tags be applied to this instance.

        # Parameters
        `tags` (dict): Mapping of tag names to values (or `None`).
        """
        self._request({"instance-labels": dict(tags)})

    label_instance = tag_instance
    """Alias for tag_instance"""

    def enable_instance_inspection(self):
        """
        Request the ability to inspect instances.
        """
        self._request({"enable-instance-inspection": True})

    def enable_network_management(self):
        """
        Request the ability to manage networking.
        """
        self._request({"enable-network-management": True})

    def enable_security_management(self):
        """
        Request the ability to manage security (e.g., firewalls).
        """
        self._request({"enable-security-management": True})

    def enable_block_storage_management(self):
        """
        Request the ability to manage block storage.
        """
        self._request({"enable-block-storage-management": True})

    def enable_dns_management(self):
        """
        Request the ability to manage DNS.
        """
        self._request({"enable-dns": True})

    def enable_object_storage_access(self):
        """
        Request the ability to access object storage.
        """
        self._request({"enable-object-storage-access": True})

    def enable_object_storage_management(self):
        """
        Request the ability to manage object storage.
        """
        self._request({"enable-object-storage-management": True})
