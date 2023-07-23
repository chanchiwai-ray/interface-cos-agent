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

import charms_openstack.test_utils as test_utils

import provides


class TestRegisteredHooks(test_utils.TestRegisteredHooks):
    def test_hooks(self):
        defaults = []
        hook_set = {
            "when": {
                "broken": ("endpoint.{endpoint_name}.broken",),
                "changed": ("endpoint.{endpoint_name}.changed",),
                "departed": ("endpoint.{endpoint_name}.departed",),
                "joined": ("endpoint.{endpoint_name}.joined",),
            },
        }
        # test that the hooks were registered
        self.registered_hooks_test_helper(provides, hook_set, defaults)


class RelationMock(object):
    def __init__(self, relation_id="cos-agent:01", app_name=None, units=None):
        self.application_name = app_name
        self.relation_id = relation_id
        self.to_publish = {}
        self.units = units


class TestCOSAgentProvider(test_utils.PatchHelper):
    def setUp(self):
        super().setUp()

        self.patch_object(provides.hookenv, "charm_name", return_value="myapp")
        self.relation_mock = RelationMock()

        self.endpoint = provides.COSAgentProvider(
            "cos-agent", [self.relation_mock.relation_id]
        )
        self.endpoint.relations[0] = self.relation_mock

    def test_update_and_clear_relation_data(self):
        # Test update_relation_data
        metrics_endpoints = [
            {"path": "/metrics", "port": 9000},
            {"path": "/metrics", "port": 9001},
            {"path": "/metrics", "port": 9002},
        ]
        self.endpoint.update_relation_data(metrics_endpoints)

        expected_result = {
            provides.CosAgentProviderUnitData.KEY: {
                "dashboards": [],
                "log_alert_rules": {},
                "log_slots": [],
                "metrics_alert_rules": "",
                "metrics_scrape_jobs": self.endpoint._get_scrape_jobs(
                    metrics_endpoints
                ),
            }
        }
        self.assertEqual(self.relation_mock.to_publish, expected_result)

        # Test clear_relation_data
        self.endpoint.clear_relation_data()
        self.assertEqual(self.relation_mock.to_publish, {})
