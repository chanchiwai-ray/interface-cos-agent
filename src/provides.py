# Copyright 2023 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import dataclasses
from typing import ClassVar, Dict, List

from charmhelpers.core import hookenv
from charms.reactive import clear_flag  # noqa: H301
from charms.reactive import Endpoint, set_flag, when, when_any

DEFAULT_SCRAPE_CONFIG = {
    "metrics_path": "/metrics",
    "static_configs": [{"targets": ["localhost:80"]}],
}


@dataclasses.dataclass
class CosAgentProviderUnitData:
    """Unit databag model for `cos-agent` relation."""

    dashboards: List[str]  # NOT IMPLEMENTED
    log_alert_rules: dict  # NOT IMPLEMENTED
    log_slots: List[str]  # NOT IMPLEMENTED
    metrics_alert_rules: dict  # NOT IMPLEMENTED
    metrics_scrape_jobs: List[Dict]

    KEY: ClassVar[str] = "config"


class COSAgentProvider(Endpoint):
    """The "provides" part of cos-agent interface.

    See https://github.com/canonical/grafana-agent-k8s-operator/blob/main/lib/charms/grafana_agent/v0/cos_agent.py.
    """

    @when("endpoint.{endpoint_name}.joined")
    def joined(self):
        """Handle relation joined."""
        set_flag(self.expand_name("{endpoint_name}.connected"))

    @when("endpoint.{endpoint_name}.changed")
    def changed(self):
        """Handle relation changed."""
        set_flag(self.expand_name("{endpoint_name}.available"))

    @when_any("endpoint.{endpoint_name}.broken", "endpoint.{endpoint_name}.departed")
    def broken_or_departed(self):
        """Handle relation broken and departed."""
        self.clear_relation_data()
        clear_flag(self.expand_name("{endpoint_name}.connected"))
        clear_flag(self.expand_name("{endpoint_name}.availabe"))

    def _get_scrape_jobs(self, metrics_endpoints):
        """Parse the scrape jobs in the Canonical's form.

        See https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config.
        """
        scrape_configs = []
        metrics_endpoints = metrics_endpoints or []

        for idx, endpoint in enumerate(metrics_endpoints):
            default_job_name = endpoint.get("job_name", "default")
            scrape_configs.append(
                {
                    "metrics_path": endpoint["path"],
                    "static_configs": [{"targets": [f"localhost:{endpoint['port']}"]}],
                    "job_name": f"{hookenv.charm_name()}_{idx}_{default_job_name}",
                }
            )
        scrape_configs = scrape_configs or [DEFAULT_SCRAPE_CONFIG]

        return scrape_configs

    def update_relation_data(self, metrics_endpoints=None):
        """Update relation data."""
        data = CosAgentProviderUnitData(
            dashboards=[],  # NOT IMPLEMENTED
            log_alert_rules={},  # NOT IMPLEMENTED
            log_slots=[],  # NOT IMPLEMENTED
            metrics_alert_rules="",  # NOT IMPLEMENTED
            metrics_scrape_jobs=self._get_scrape_jobs(metrics_endpoints),
        )
        for relation in self.relations:
            relation.to_publish[data.KEY] = dataclasses.asdict(data)

    def clear_relation_data(self):
        """Clear relation data."""
        for relation in self.relations:
            relation.to_publish.pop(CosAgentProviderUnitData.KEY, None)
