// Copyright (c) 2015, creqit Technologies Pvt. Ltd. and Contributors

creqit.has_indicator = function (doctype) {
	// returns true if indicator is present
	if (creqit.model.is_submittable(doctype)) {
		return true;
	} else if (
		(creqit.listview_settings[doctype] || {}).get_indicator ||
		creqit.workflow.get_state_fieldname(doctype)
	) {
		return true;
	} else if (
		creqit.meta.has_field(doctype, "enabled") ||
		creqit.meta.has_field(doctype, "disabled")
	) {
		return true;
	} else if (
		creqit.meta.has_field(doctype, "status") &&
		creqit.get_meta(doctype).states.length
	) {
		return true;
	}
	return false;
};

creqit.get_indicator = function (doc, doctype, show_workflow_state) {
	if (doc.__unsaved) {
		return [__("Not Saved"), "orange"];
	}

	if (!doctype) doctype = doc.doctype;

	let meta = creqit.get_meta(doctype);
	var workflow = creqit.workflow.workflows[doctype];
	var without_workflow = workflow ? workflow["override_status"] : true;

	var settings = creqit.listview_settings[doctype] || {};

	var is_submittable = creqit.model.is_submittable(doctype);
	let workflow_fieldname = creqit.workflow.get_state_fieldname(doctype);

	let avoid_status_override = (creqit.workflow.avoid_status_override[doctype] || []).includes(
		doc[workflow_fieldname]
	);
	// workflow
	if (
		workflow_fieldname &&
		(!without_workflow || show_workflow_state) &&
		!avoid_status_override
	) {
		var value = doc[workflow_fieldname];
		if (value) {
			let colour = "";
			let icon = "creqit-info"; //creqit.v1.sevval//
			if (locals["Workflow State"][value] && locals["Workflow State"][value].style) {
				colour = {
					Success: "green",
					Warning: "orange",
					Danger: "red",
					Primary: "primary",//creqit.v1.sevval//
					Secondary: "light-gray",//creqit.v1.sevval//
					Inverse: "black",
					Info: "blue",//creqit.v1.sevval//
				}[locals["Workflow State"][value].style];
			}
			if (!colour) colour = "gray";
            const icon_html = `<div class="indicator-icon ">${creqit.utils.icon(icon)}</div>`;//creqit.v1.sevval//
			return [__(value), colour, workflow_fieldname + ",=," + value, icon_html];//creqit.v1.sevval//
		}
	}

	// draft if document is submittable
	if (is_submittable && doc.docstatus == 0 && !settings.has_indicator_for_draft) {
		return [__("Draft"), "red", "docstatus,=,0"];
	}

	// cancelled
	if (is_submittable && doc.docstatus == 2 && !settings.has_indicator_for_cancelled) {
		return [__("Cancelled"), "red", "docstatus,=,2"];
	}

	// based on document state
	if (doc.status && meta && meta.states && meta.states.find((d) => d.title === doc.status)) {
		let state = meta.states.find((d) => d.title === doc.status);
		let color_class = creqit.scrub(state.color, "-");
		return [__(doc.status), color_class, "status,=," + doc.status];
	}

	if (settings.get_indicator) {
		var indicator = settings.get_indicator(doc);
		if (indicator) return indicator;
	}

	// if submittable
	if (is_submittable && doc.docstatus == 1) {
		return [__("Submitted"), "primary", "docstatus,=,1"];//creqit.v1.sevval//
	}

	// based on status
	if (doc.status) {
		return [__(doc.status), creqit.utils.guess_colour(doc.status), "status,=," + doc.status];
	}

	// based on enabled
	if (creqit.meta.has_field(doctype, "enabled")) {
		if (doc.enabled) {
			return [__("Enabled"), "blue", "enabled,=,1"];
		} else {
			return [__("Disabled"), "grey", "enabled,=,0"];
		}
	}

	// based on disabled
	if (creqit.meta.has_field(doctype, "disabled")) {
		if (doc.disabled) {
			return [__("Disabled"), "grey", "disabled,=,1"];
		} else {
			return [__("Enabled"), "blue", "disabled,=,0"];
		}
	}
};
