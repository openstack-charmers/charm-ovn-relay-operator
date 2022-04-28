#!/usr/bin/env python3

# Copyright 2021 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

sys.path.append('lib')  # noqa
sys.path.append('src')  # noqa

import charm
import advanced_sunbeam_openstack.test_utils as test_utils


class _OVNRelayXenaOperatorCharm(charm.OVNRelayXenaOperatorCharm):

    def __init__(self, framework):
        self.seen_events = []
        super().__init__(framework)

    def _log_event(self, event):
        self.seen_events.append(type(event).__name__)

    def configure_charm(self, event):
        super().configure_charm(event)
        self._log_event(event)


class TestOVNRelayXenaOperatorCharm(test_utils.CharmTestCase):

    PATCHES = []

    def setUp(self):
        super().setUp(charm, self.PATCHES)
        self.harness = test_utils.get_harness(
            _OVNRelayXenaOperatorCharm,
            container_calls=self.container_calls)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_pebble_ready_handler(self):
        self.assertEqual(self.harness.charm.seen_events, [])
        self.harness.container_pebble_ready('ovsdb-server')
        self.assertEqual(len(self.harness.charm.seen_events), 1)

    def test_all_relations(self):
        self.harness.set_leader()
        self.assertEqual(self.harness.charm.seen_events, [])
        test_utils.set_all_pebbles_ready(self.harness)
        test_utils.add_all_relations(self.harness)
        config_files = [
            '/etc/ovn/cert_host',
            '/etc/ovn/key_host',
            '/etc/ovn/ovn-central.crt',
            '/root/ovn-relay-wrapper.sh']
        for f in config_files:
            self.check_file('ovsdb-server', f)
