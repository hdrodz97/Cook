import logging
import unittest
import uuid

import pytest
import requests
import requests.adapters
import requests_mock
from cook import http

from cook.querying import query_cluster, make_job_request


@pytest.mark.cli
class CookCliTest(unittest.TestCase):
    _multiprocess_can_split_ = True

    def setUp(self):
        self.logger = logging.getLogger(__name__)

    def test_query_cluster_should_gracefully_handle_json_parsing_failures(self):
        http_plugins = {
            'http-adapter-factory': requests.adapters.HTTPAdapter,
            'http-session-factory': requests.Session,
        }
        http.configure(config={}, plugins=http_plugins)
        cluster = {'url': 'http://localhost'}
        uuids = [uuid.uuid4()]
        with requests_mock.mock() as m:
            m.get('http://localhost/rawscheduler', text='this is not json')
            self.assertEqual([], query_cluster(cluster, uuids, None, None, None, make_job_request, 'job'))
