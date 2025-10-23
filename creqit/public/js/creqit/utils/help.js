// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

creqit.provide("creqit.help");

creqit.help.youtube_id = {};

creqit.help.has_help = function (doctype) {
	return creqit.help.youtube_id[doctype];
};

creqit.help.show = function (doctype) {
	if (creqit.help.youtube_id[doctype]) {
		creqit.help.show_video(creqit.help.youtube_id[doctype]);
	}
};

creqit.help.show_video = function (youtube_id, title) {
	if (creqit.utils.is_url(youtube_id)) {
		const expression =
			'(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (creqit.help_feedback_link || "")
	let dialog = new creqit.ui.Dialog({
		title: title || __("Help"),
		size: "large",
	});

	let video = $(
		`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`
	);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr;
	creqit.utils.load_video_player().then(() => {
		plyr = new creqit.Plyr(video[0], {
			hideControls: true,
			resetOnEnd: true,
		});
	});

	dialog.onhide = () => {
		plyr?.destroy();
	};
};

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && creqit.help.show(doctype);
});
