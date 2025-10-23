# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit
import creqit.monitor
from creqit.monitor import MONITOR_REDIS_KEY, get_trace_id
from creqit.tests import IntegrationTestCase
from creqit.utils import set_request
from creqit.utils.response import build_response


class TestMonitor(IntegrationTestCase):
	def setUp(self):
		creqit.conf.monitor = 1
		creqit.cache.delete_value(MONITOR_REDIS_KEY)

	def tearDown(self):
		creqit.conf.monitor = 0
		creqit.cache.delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/creqit.ping")
		response = build_response("json")

		creqit.monitor.start()
		creqit.monitor.stop(response)

		logs = creqit.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = creqit.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_no_response(self):
		set_request(method="GET", path="/api/method/creqit.ping")

		creqit.monitor.start()
		creqit.monitor.stop(response=None)

		logs = creqit.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = creqit.parse_json(logs[0].decode())
		self.assertEqual(log.request["status_code"], 500)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		creqit.utils.background_jobs.execute_job(
			creqit.local.site, "creqit.ping", None, None, {}, is_async=False
		)

		logs = creqit.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = creqit.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "creqit.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/creqit.ping")
		response = build_response("json")
		creqit.monitor.start()
		creqit.monitor.stop(response)

		open(creqit.monitor.log_file(), "w").close()
		creqit.monitor.flush()

		with open(creqit.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = creqit.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def test_trace_ids(self):
		set_request(method="GET", path="/api/method/creqit.ping")
		response = build_response("json")
		creqit.monitor.start()
		creqit.db.sql("select 1")
		self.assertIn(get_trace_id(), str(creqit.db.last_query))
		creqit.monitor.stop(response)
