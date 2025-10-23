# Copyright (c) 2018, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import creqit


def execute():
	creqit.db.set_value("Currency", "USD", "smallest_currency_fraction_value", "0.01")
