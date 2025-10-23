creqit.pages["user-profile"].on_page_load = function (wrapper) {
	creqit.require("user_profile_controller.bundle.js", () => {
		let user_profile = new creqit.ui.UserProfile(wrapper);
		user_profile.show();
	});
};
