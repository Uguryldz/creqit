creqit.provide("creqit.ui.misc");
creqit.ui.misc.about = function () {
	if (!creqit.ui.misc.about_dialog) {
		var d = new creqit.ui.Dialog({ title: __("creqit Framework") });

		$(d.body).html(
			repl(
				`<div>
					<p>${__("Open Source Applications for the Web")}</p>
					<p><i class='fa fa-globe fa-fw'></i>
						${__("Website")}:
						<a href='https://creqitframework.com' target='_blank'>https://creqitframework.com</a></p>
					<p><i class='fa fa-github fa-fw'></i>
						${__("Source")}:
						<a href='https://github.com/creqit' target='_blank'>https://github.com/creqit</a></p>
					<p><i class='fa fa-graduation-cap fa-fw'></i>
						creqit School: <a href='https://creqit.school' target='_blank'>https://creqit.school</a></p>
					<p><i class='fa fa-linkedin fa-fw'></i>
						Linkedin: <a href='https://linkedin.com/company/creqit-tech' target='_blank'>https://linkedin.com/company/creqit-tech</a></p>
					<p><i class='fa fa-twitter fa-fw'></i>
						Twitter: <a href='https://twitter.com/creqittech' target='_blank'>https://twitter.com/creqittech</a></p>
					<p><i class='fa fa-youtube fa-fw'></i>
						YouTube: <a href='https://www.youtube.com/@creqittech' target='_blank'>https://www.youtube.com/@creqittech</a></p>
					<hr>
					<h4>${__("Installed Apps")}</h4>
					<div id='about-app-versions'>${__("Loading versions...")}</div>
					<p>
						<b>
							<a href="/attribution" target="_blank" class="text-muted">
								${__("Dependencies & Licenses")}
							</a>
						</b>
					</p>
					<hr>
					<p class='text-muted'>${__("&copy; creqit Technologies Pvt. Ltd. and contributors")} </p>
					</div>`,
				creqit.app
			)
		);

		creqit.ui.misc.about_dialog = d;

		creqit.ui.misc.about_dialog.on_page_show = function () {
			if (!creqit.versions) {
				creqit.call({
					method: "creqit.utils.change_log.get_versions",
					callback: function (r) {
						show_versions(r.message);
					},
				});
			} else {
				show_versions(creqit.versions);
			}
		};

		var show_versions = function (versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function (i, key) {
				var v = versions[key];
				let text;
				if (v.branch) {
					text = $.format("<p><b>{0}:</b> v{1} ({2})<br></p>", [
						v.title,
						v.branch_version || v.version,
						v.branch,
					]);
				} else {
					text = $.format("<p><b>{0}:</b> v{1}<br></p>", [v.title, v.version]);
				}
				$(text).appendTo($wrap);
			});

			creqit.versions = versions;
		};
	}

	creqit.ui.misc.about_dialog.show();
};
