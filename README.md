# Interface cos_agent

The interface-cos-agent handles the relations with [grafana-agent-k8s-operator](https://github.com/canonical/grafana-agent-k8s-operator/tree/main) (machine charm). In particular, it is the `Provider` part of the `cos_agent` interface for reactive charms, whereas the `Requirer` is implemented in the `grafana-agent-k8s-operator` (machine charm).

**Note: only metrics_endpoints is supported.**
