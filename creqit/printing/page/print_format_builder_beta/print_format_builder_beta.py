# Copyright (c) 2021, creqit Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import functools

import creqit


@creqit.whitelist()
def get_google_fonts():
	return _get_google_fonts()


@functools.lru_cache
def _get_google_fonts():
	file_path = creqit.get_app_path("creqit", "data", "google_fonts.json")
	return creqit.parse_json(creqit.read_file(file_path))
