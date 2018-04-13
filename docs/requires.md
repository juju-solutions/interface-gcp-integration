<h1 id="requires">requires</h1>


This is the requires side of the interface layer, for use in charms that
wish to request integration with GCP native features.  The integration will
be provided by the GCP integration charm, which allows the requiring charm
to not require cloud credentials itself and not have a lot of GCP specific
API code.

The flags that are set by the requires side of this interface are:

* **`endpoint.{endpoint_name}.joined`** This flag is set when the relation
  has been joined, and the charm should then use the methods documented below
  to request specific GCP features.  This flag is automatically removed if
  the relation is broken.  It should not be removed by the charm.

* **`endpoint.{endpoint_name}.ready`** This flag is set once the requested
  features have been enabled for the GCP instance on which the charm is
  running.  This flag is automatically removed if new integration features
  are requested.  It should not be removed by the charm.

<h1 id="requires.GCPRequires">GCPRequires</h1>

```python
GCPRequires(self, *args, **kwargs)
```

Example usage:

```python
from charms.reactive import when, endpoint_from_flag

@when('endpoint.gcp.joined')
def request_gcp_integration():
    gcp = endpoint_from_flag('endpoint.gcp.joined')
    gcp.label_instance({
        'tag1': 'value1',
        'tag2': None,
    })
    gcp.request_load_balancer_management()
    # ...

@when('endpoint.gcp.ready')
def gcp_integration_ready():
    update_config_enable_gcp()
```

<h2 id="requires.GCPRequires.enable_block_storage_management">enable_block_storage_management</h2>

```python
GCPRequires.enable_block_storage_management(self)
```

Request the ability to manage block storage.

<h2 id="requires.GCPRequires.enable_load_balancer_management">enable_load_balancer_management</h2>

```python
GCPRequires.enable_load_balancer_management(self)
```

Request the ability to manage load balancers.

<h2 id="requires.GCPRequires.instance">instance</h2>


This unit's instance name.

<h2 id="requires.GCPRequires.enable_object_storage_access">enable_object_storage_access</h2>

```python
GCPRequires.enable_object_storage_access(self, patterns=None)
```

Request the ability to access object storage.

__Parameters__

- __`patterns` (list)__: If given, restrict access to the resources matching
    the patterns.

<h2 id="requires.GCPRequires.label_instance">label_instance</h2>

```python
GCPRequires.label_instance(self, labels)
```

Request that the given labels be applied to this instance.

__Parameters__

- __`labels` (dict)__: Mapping of labels names to values.

<h2 id="requires.GCPRequires.zone">zone</h2>


The zone this unit is in.

<h2 id="requires.GCPRequires.enable_object_storage_management">enable_object_storage_management</h2>

```python
GCPRequires.enable_object_storage_management(self, patterns=None)
```

Request the ability to manage object storage.

__Parameters__

- __`patterns` (list)__: If given, restrict management to the resources
    matching the patterns.

<h2 id="requires.GCPRequires.enable_network_management">enable_network_management</h2>

```python
GCPRequires.enable_network_management(self)
```

Request the ability to manage networking (firewalls, subnets, etc).

<h2 id="requires.GCPRequires.enable_instance_inspection">enable_instance_inspection</h2>

```python
GCPRequires.enable_instance_inspection(self)
```

Request the ability to inspect instances.

<h2 id="requires.GCPRequires.enable_dns">enable_dns</h2>

```python
GCPRequires.enable_dns(self)
```

Request the ability to manage DNS.

