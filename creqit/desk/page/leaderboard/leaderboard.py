# Copyright (c) 2017, creqit Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import creqit


@creqit.whitelist()
def get_leaderboard_config():
	leaderboard_config = creqit._dict()
	leaderboard_hooks = creqit.get_hooks("leaderboards")
	for hook in leaderboard_hooks:
		leaderboard_config.update(creqit.get_attr(hook)())

	return leaderboard_config
