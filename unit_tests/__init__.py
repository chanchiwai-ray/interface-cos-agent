import sys

import charms_openstack.test_mocks

sys.path.append("src")
# Mock out charmhelpers so that we can test without it.
charms_openstack.test_mocks.mock_charmhelpers()
