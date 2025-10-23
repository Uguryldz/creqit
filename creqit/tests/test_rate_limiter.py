# Copyright (c) 2020, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import time

from werkzeug.wrappers import Response

import creqit
import creqit.rate_limiter
from creqit.rate_limiter import RateLimiter
from creqit.tests import IntegrationTestCase
from creqit.utils import cint


class TestRateLimiter(IntegrationTestCase):
	def test_apply_with_limit(self):
		creqit.conf.rate_limit = {"window": 86400, "limit": 1}
		creqit.rate_limiter.apply()

		self.assertTrue(hasattr(creqit.local, "rate_limiter"))
		self.assertIsInstance(creqit.local.rate_limiter, RateLimiter)

		creqit.cache.delete(creqit.local.rate_limiter.key)
		delattr(creqit.local, "rate_limiter")

	def test_apply_without_limit(self):
		creqit.conf.rate_limit = None
		creqit.rate_limiter.apply()

		self.assertFalse(hasattr(creqit.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		creqit.conf.rate_limit = {"window": 86400, "limit": 0.01}
		self.assertRaises(creqit.TooManyRequestsError, creqit.rate_limiter.apply)
		creqit.rate_limiter.update()

		response = creqit.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = creqit.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertNotIn("X-RateLimit-Used", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		creqit.cache.delete(limiter.key)
		creqit.cache.delete(creqit.local.rate_limiter.key)
		delattr(creqit.local, "rate_limiter")

	def test_respond_under_limit(self):
		creqit.conf.rate_limit = {"window": 86400, "limit": 0.01}
		creqit.rate_limiter.apply()
		creqit.rate_limiter.update()
		response = creqit.rate_limiter.respond()
		self.assertEqual(response, None)

		creqit.cache.delete(creqit.local.rate_limiter.key)
		delattr(creqit.local, "rate_limiter")

	def test_headers_under_limit(self):
		creqit.conf.rate_limit = {"window": 86400, "limit": 0.01}
		creqit.rate_limiter.apply()
		creqit.rate_limiter.update()
		headers = creqit.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Used"]), creqit.local.rate_limiter.duration)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 10000)

		creqit.cache.delete(creqit.local.rate_limiter.key)
		delattr(creqit.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(creqit.TooManyRequestsError, limiter.apply)

		creqit.cache.delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		creqit.cache.delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(creqit.cache.get(limiter.key)))

		creqit.cache.delete(limiter.key)
