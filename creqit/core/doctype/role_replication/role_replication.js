// Copyright (c) 2024, creqit Technologies and contributors
// For license information, please see license.txt

creqit.ui.form.on("Role Replication", {
	refresh(frm) {
		frm.disable_save();
		frm.page.set_primary_action(__("Replicate"), ($btn) => {
			$btn.text(__("Replicating..."));
			creqit.run_serially([
				() => creqit.dom.freeze("Replicating..."),
				() => frm.call("replicate_role"),
				() => creqit.dom.unfreeze(),
				() => creqit.msgprint(__("Replication completed.")),
				() => $btn.text(__("Replicate")),
			]);
		});
	},
});
