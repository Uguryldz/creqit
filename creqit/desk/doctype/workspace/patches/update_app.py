# update app in `Module Def` and `Workspace`

import creqit
from creqit.modules.utils import get_module_app


def execute():
	for module in creqit.get_all("Module Def", ["name", "app_name"], filters=dict(custom=0)):
		if not module.app_name:
			try:
				creqit.db.set_value("Module Def", module.name, "app_name", get_module_app(module.name))
			except Exception:
				# for some default modules like Home, there is no folder / app
				pass

	for workspace in creqit.get_all("Workspace", ["name", "module", "app"]):
		if not workspace.app and workspace.module:
			creqit.db.set_value(
				"Workspace",
				workspace.name,
				"app",
				creqit.db.get_value("Module Def", workspace.module, "app_name"),
			)
