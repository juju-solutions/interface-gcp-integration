<h1 id="provides">provides</h1>


This is the provides side of the interface layer, for use only by the GCP
integration charm itself.

The flags that are set by the provides side of this interface are:

* **`endpoint.{endpoint_name}.requested`** This flag is set when there is
  a new or updated request by a remote unit for GCP integration features.
  The GCP integration charm should then iterate over each request, perform
  whatever actions are necessary to satisfy those requests, and then mark
  them as complete.

<h1 id="provides.GCPProvides">GCPProvides</h1>

```python
GCPProvides(self, endpoint_name, relation_ids=None)
```

Example usage:

```python
from charms.reactive import when, endpoint_from_flag
from charms import layer

@when('endpoint.gcp.requested')
def handle_requests():
    gcp = endpoint_from_flag('endpoint.gcp.requested')
    for request in gcp.requests:
        if request.instance_labels:
            label_instance(
                request.instance,
                request.zone,
                request.instance_labels)
        if request.requested_load_balancer_management:
            layer.gcp.enable_load_balancer_management(
                request.application_name,
                request.instance,
                request.zone,
            )
        # ...
        request.mark_completed()
```

<h2 id="provides.GCPProvides.requests">requests</h2>


A list of the new or updated `IntegrationRequests` that
have been made.

<h2 id="provides.GCPProvides.application_names">application_names</h2>


Set of names of all applications that are still joined.

<h2 id="provides.GCPProvides.unit_instances">unit_instances</h2>


Mapping of unit names to instance names and zones for all joined units.

<h1 id="provides.IntegrationRequest">IntegrationRequest</h1>

```python
IntegrationRequest(self, unit)
```

A request for integration from a single remote unit.

<h2 id="provides.IntegrationRequest.object_storage_access_patterns">object_storage_access_patterns</h2>


List of patterns to which to restrict object storage access.

<h2 id="provides.IntegrationRequest.clear">clear</h2>

```python
IntegrationRequest.clear(self)
```

Clear this request's cached data.

<h2 id="provides.IntegrationRequest.requested_block_storage_management">requested_block_storage_management</h2>


Flag indicating whether block storage management was requested.

<h2 id="provides.IntegrationRequest.requested_dns_management">requested_dns_management</h2>


Flag indicating whether DNS management was requested.

<h2 id="provides.IntegrationRequest.hash">hash</h2>


SHA hash of the data for this request.

<h2 id="provides.IntegrationRequest.instance_labels">instance_labels</h2>


Mapping of label names to values to apply to this instance.

<h2 id="provides.IntegrationRequest.zone">zone</h2>


The zone reported for this request.

<h2 id="provides.IntegrationRequest.requested_object_storage_management">requested_object_storage_management</h2>


Flag indicating whether object storage management was requested.

<h2 id="provides.IntegrationRequest.changed">changed</h2>


Whether this request has changed since the last time it was
marked completed.

<h2 id="provides.IntegrationRequest.requested_load_balancer_management">requested_load_balancer_management</h2>


Flag indicating whether load balancer management was requested.

<h2 id="provides.IntegrationRequest.requested_instance_inspection">requested_instance_inspection</h2>


Flag indicating whether the ability to inspect instances was requested.

<h2 id="provides.IntegrationRequest.unit_name">unit_name</h2>


The name of the unit making the request.

<h2 id="provides.IntegrationRequest.application_name">application_name</h2>


The name of the application making the request.

<h2 id="provides.IntegrationRequest.object_storage_management_patterns">object_storage_management_patterns</h2>


List of patterns to which to restrict object storage management.

<h2 id="provides.IntegrationRequest.instance">instance</h2>


The instance name reported for this request.

<h2 id="provides.IntegrationRequest.mark_completed">mark_completed</h2>

```python
IntegrationRequest.mark_completed(self)
```

Mark this request as having been completed.

<h2 id="provides.IntegrationRequest.requested_network_management">requested_network_management</h2>


Flag indicating whether the ability to manage networking (firewalls,
subnets, etc) was requested.

<h2 id="provides.IntegrationRequest.requested_object_storage_access">requested_object_storage_access</h2>


Flag indicating whether object storage access was requested.

