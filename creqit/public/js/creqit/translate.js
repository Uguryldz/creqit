// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// for translation
creqit._ = function (txt, replace, context = null) {
	if (!txt) return txt;
	if (typeof txt != "string") return txt;

	let translated_text = "";

	let key = txt; // txt.replace(/\n/g, "");
	if (context) {
		translated_text = creqit._messages[`${key}:${context}`];
	}

	if (!translated_text) {
		translated_text = creqit._messages[key] || txt;
	}

	if (replace && typeof replace === "object") {
		translated_text = $.format(translated_text, replace);
	}
	return translated_text;
};

window.__ = creqit._;

creqit.get_languages = function () {
	if (!creqit.languages) {
		creqit.languages = [];
		$.each(creqit.boot.lang_dict, function (lang, value) {
			creqit.languages.push({ label: lang, value: value });
		});
		creqit.languages = creqit.languages.sort(function (a, b) {
			return a.value < b.value ? -1 : 1;
		});
	}
	return creqit.languages;
};
