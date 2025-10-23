import os

from . import __version__ as app_version

app_name = "creqit"
app_title = "creqit" #UPDATES --sevval
app_publisher = "creqit Technologies" #UPDATES --sevval
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
app_license = "MIT"
app_logo_url = "/assets/creqit/images/creqit_logo.png" #UPDATES --sevval
develop_version = "15.x.x-develop"
app_home = "/app/build"

app_email = "developers@creqit.io"

before_install = "creqit.utils.install.before_install"
after_install = "creqit.utils.install.after_install"

page_js = {"setup-wizard": "public/js/creqit/setup_wizard.js"}

# website
app_include_js = [
	"libs.bundle.js",
	"desk.bundle.js",
	"list.bundle.js",
	"form.bundle.js",
	"controls.bundle.js",
	"report.bundle.js",
	"telemetry.bundle.js",
]

app_include_css = [
	"desk.bundle.css",
	"report.bundle.css",
]
app_include_icons = [
	"/assets/creqit/icons/timeless/icons.svg",
	"/assets/creqit/icons/espresso/icons.svg",
]

doctype_js = {
	"Web Page": "public/js/creqit/utils/web_template.js",
	"Website Settings": "public/js/creqit/utils/web_template.js",
}

web_include_js = ["website_script.js"]
web_include_css = []
web_include_icons = [
	"/assets/creqit/icons/timeless/icons.svg",
	"/assets/creqit/icons/espresso/icons.svg",
]

email_css = ["email.bundle.css"]

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/newsletters", "to_route": "Newsletter"},
	{"from_route": "/profile", "to_route": "me"},
	{"from_route": "/app/<path:app_path>", "to_route": "app"},
]

website_redirects = [
	{"source": r"/desk(.*)", "target": r"/app\1"},
	{
		"source": "/.well-known/openid-configuration",
		"target": "/api/method/creqit.integrations.oauth2.openid_configuration",
	},
]

base_template = "templates/base.html"

write_file_keys = ["file_url", "file_name"]

notification_config = "creqit.core.notifications.get_notification_config"

before_tests = "creqit.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]

calendars = ["Event"]

leaderboards = "creqit.desk.leaderboard.get_leaderboards"

# login

on_session_creation = [
	"creqit.core.doctype.activity_log.feed.login_feed",
	"creqit.core.doctype.user.user.notify_admin_access_to_system_manager",
]

on_logout = "creqit.core.doctype.session_default_settings.session_default_settings.clear_session_defaults"

# PDF
pdf_header_html = "creqit.utils.pdf.pdf_header_html"
pdf_body_html = "creqit.utils.pdf.pdf_body_html"
pdf_footer_html = "creqit.utils.pdf.pdf_footer_html"

# permissions

permission_query_conditions = {
	"Event": "creqit.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "creqit.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "creqit.core.doctype.user.user.get_permission_query_conditions",
	"Dashboard Settings": "creqit.desk.doctype.dashboard_settings.dashboard_settings.get_permission_query_conditions",
	"Notification Log": "creqit.desk.doctype.notification_log.notification_log.get_permission_query_conditions",
	"Dashboard": "creqit.desk.doctype.dashboard.dashboard.get_permission_query_conditions",
	"Dashboard Chart": "creqit.desk.doctype.dashboard_chart.dashboard_chart.get_permission_query_conditions",
	"Number Card": "creqit.desk.doctype.number_card.number_card.get_permission_query_conditions",
	"Notification Settings": "creqit.desk.doctype.notification_settings.notification_settings.get_permission_query_conditions",
	"Note": "creqit.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "creqit.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "creqit.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "creqit.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "creqit.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "creqit.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions",
	"Prepared Report": "creqit.core.doctype.prepared_report.prepared_report.get_permission_query_condition",
	"File": "creqit.core.doctype.file.file.get_permission_query_conditions",
}

has_permission = {
	"Event": "creqit.desk.doctype.event.event.has_permission",
	"ToDo": "creqit.desk.doctype.todo.todo.has_permission",
	"Note": "creqit.desk.doctype.note.note.has_permission",
	"User": "creqit.core.doctype.user.user.has_permission",
	"Dashboard Chart": "creqit.desk.doctype.dashboard_chart.dashboard_chart.has_permission",
	"Number Card": "creqit.desk.doctype.number_card.number_card.has_permission",
	"Kanban Board": "creqit.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "creqit.contacts.address_and_contact.has_permission",
	"Address": "creqit.contacts.address_and_contact.has_permission",
	"Communication": "creqit.core.doctype.communication.communication.has_permission",
	"Workflow Action": "creqit.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "creqit.core.doctype.file.file.has_permission",
	"Prepared Report": "creqit.core.doctype.prepared_report.prepared_report.has_permission",
	"Notification Settings": "creqit.desk.doctype.notification_settings.notification_settings.has_permission",
}

has_website_permission = {"Address": "creqit.contacts.doctype.address.address.has_website_permission"}

jinja = {
	"methods": "creqit.utils.jinja_globals",
	"filters": [
		"creqit.utils.data.global_date_format",
		"creqit.utils.markdown",
		"creqit.website.utils.abs_url",
	],
}

standard_queries = {"User": "creqit.core.doctype.user.user.user_query"}

doc_events = {
	"*": {
		"on_update": [
			"creqit.desk.notifications.clear_doctype_notifications",
			"creqit.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"creqit.core.doctype.file.utils.attach_files_to_document",
			"creqit.automation.doctype.assignment_rule.assignment_rule.apply",
			"creqit.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"creqit.core.doctype.user_type.user_type.apply_permissions_for_non_standard_user_type",
			"creqit.core.doctype.permission_log.permission_log.make_perm_log",
		],
		"after_rename": "creqit.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"creqit.desk.notifications.clear_doctype_notifications",
			"creqit.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"creqit.automation.doctype.assignment_rule.assignment_rule.apply",
		],
		"on_trash": [
			"creqit.desk.notifications.clear_doctype_notifications",
			"creqit.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
		],
		"on_update_after_submit": [
			"creqit.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"creqit.automation.doctype.assignment_rule.assignment_rule.apply",
			"creqit.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"creqit.core.doctype.file.utils.attach_files_to_document",
		],
		"on_change": [
			"creqit.social.doctype.energy_point_rule.energy_point_rule.process_energy_points",
			"creqit.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone",
		],
		"after_delete": ["creqit.core.doctype.permission_log.permission_log.make_perm_log"],
	},
	"Event": {
		"after_insert": "creqit.integrations.doctype.google_calendar.google_calendar.insert_event_in_google_calendar",
		"on_update": "creqit.integrations.doctype.google_calendar.google_calendar.update_event_in_google_calendar",
		"on_trash": "creqit.integrations.doctype.google_calendar.google_calendar.delete_event_from_google_calendar",
	},
	"Contact": {
		"after_insert": "creqit.integrations.doctype.google_contacts.google_contacts.insert_contacts_to_google_contacts",
		"on_update": "creqit.integrations.doctype.google_contacts.google_contacts.update_contacts_to_google_contacts",
	},
	"DocType": {
		"on_update": "creqit.cache_manager.build_domain_restriced_doctype_cache",
	},
	"Page": {
		"on_update": "creqit.cache_manager.build_domain_restriced_page_cache",
	},
}

scheduler_events = {
	"cron": {
		# 5 minutes
		"0/5 * * * *": [
			"creqit.email.doctype.notification.notification.trigger_offset_alerts",
		],
		# 15 minutes
		"0/15 * * * *": [
			"creqit.oauth.delete_oauth2_data",
			"creqit.website.doctype.web_page.web_page.check_publish_status",
			"creqit.twofactor.delete_all_barcodes_for_users",
			"creqit.email.doctype.email_account.email_account.notify_unreplied",
			"creqit.utils.global_search.sync_global_search",
			"creqit.deferred_insert.save_to_db",
		],
		# 10 minutes
		"0/10 * * * *": [
			"creqit.email.doctype.email_account.email_account.pull",
		],
		# Hourly but offset by 30 minutes
		"30 * * * *": [
			"creqit.core.doctype.prepared_report.prepared_report.expire_stalled_report",
		],
		# Daily but offset by 45 minutes
		"45 0 * * *": [
			"creqit.core.doctype.log_settings.log_settings.run_log_clean_up",
		],
	},
	"all": [
		"creqit.email.queue.flush",
		"creqit.monitor.flush",
		"creqit.automation.doctype.reminder.reminder.send_reminders",
	],
	"hourly": [
		"creqit.model.utils.link_count.update_link_count",
		"creqit.model.utils.user_settings.sync_user_settings",
		"creqit.desk.page.backups.backups.delete_downloadable_backups",
		"creqit.desk.form.document_follow.send_hourly_updates",
		"creqit.integrations.doctype.google_calendar.google_calendar.sync",
		"creqit.email.doctype.newsletter.newsletter.send_scheduled_email",
		"creqit.website.doctype.personal_data_deletion_request.personal_data_deletion_request.process_data_deletion_request",
	],
	"daily": [
		"creqit.desk.notifications.clear_notifications",
		"creqit.desk.doctype.event.event.send_event_digest",
		"creqit.sessions.clear_expired_sessions",
		"creqit.email.doctype.notification.notification.trigger_daily_alerts",
		"creqit.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"creqit.desk.form.document_follow.send_daily_updates",
		"creqit.social.doctype.energy_point_settings.energy_point_settings.allocate_review_points",
		"creqit.integrations.doctype.google_contacts.google_contacts.sync",
		"creqit.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
		"creqit.automation.doctype.auto_repeat.auto_repeat.set_auto_repeat_as_completed",
	],
	"daily_long": [
		"creqit.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_daily",
		"creqit.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_daily",
		"creqit.email.doctype.auto_email_report.auto_email_report.send_daily",
		"creqit.integrations.doctype.google_drive.google_drive.daily_backup",
	],
	"weekly_long": [
		"creqit.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_weekly",
		"creqit.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_weekly",
		"creqit.desk.form.document_follow.send_weekly_updates",
		"creqit.utils.change_log.check_for_update",
		"creqit.social.doctype.energy_point_log.energy_point_log.send_weekly_summary",
		"creqit.integrations.doctype.google_drive.google_drive.weekly_backup",
		"creqit.desk.doctype.changelog_feed.changelog_feed.fetch_changelog_feed",
	],
	"monthly": [
		"creqit.email.doctype.auto_email_report.auto_email_report.send_monthly",
		"creqit.social.doctype.energy_point_log.energy_point_log.send_monthly_summary",
	],
	"monthly_long": [
		"creqit.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_monthly"
	],
}

sounds = [
	{"name": "email", "src": "/assets/creqit/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/creqit/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/creqit/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/creqit/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/creqit/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/creqit/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/creqit/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/creqit/sounds/chime.mp3"},
]

setup_wizard_exception = [
	"creqit.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception",
	"creqit.desk.page.setup_wizard.setup_wizard.log_setup_wizard_exception",
]

before_migrate = ["creqit.core.doctype.patch_log.patch_log.before_migrate"]
after_migrate = ["creqit.website.doctype.website_theme.website_theme.after_migrate"]

otp_methods = ["OTP App", "Email", "SMS"]

user_data_fields = [
	{"doctype": "Access Log", "strict": True},
	{"doctype": "Activity Log", "strict": True},
	{"doctype": "Comment", "strict": True},
	{
		"doctype": "Contact",
		"filter_by": "email_id",
		"redact_fields": ["first_name", "last_name", "phone", "mobile_no"],
		"rename": True,
	},
	{"doctype": "Contact Email", "filter_by": "email_id"},
	{
		"doctype": "Address",
		"filter_by": "email_id",
		"redact_fields": [
			"address_title",
			"address_line1",
			"address_line2",
			"city",
			"county",
			"state",
			"pincode",
			"phone",
			"fax",
		],
	},
	{
		"doctype": "Communication",
		"filter_by": "sender",
		"redact_fields": ["sender_full_name", "phone_no", "content"],
	},
	{"doctype": "Communication", "filter_by": "recipients"},
	{"doctype": "Email Group Member", "filter_by": "email"},
	{"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
	{"doctype": "Email Queue", "filter_by": "sender"},
	{"doctype": "Email Queue Recipient", "filter_by": "recipient"},
	{
		"doctype": "File",
		"filter_by": "attached_to_name",
		"redact_fields": ["file_name", "file_url"],
	},
	{
		"doctype": "User",
		"filter_by": "name",
		"redact_fields": [
			"email",
			"username",
			"first_name",
			"middle_name",
			"last_name",
			"full_name",
			"birth_date",
			"user_image",
			"phone",
			"mobile_no",
			"location",
			"banner_image",
			"interest",
			"bio",
			"email_signature",
		],
	},
	{"doctype": "Version", "strict": True},
]

global_search_doctypes = {
	"Default": [
		{"doctype": "Contact"},
		{"doctype": "Address"},
		{"doctype": "ToDo"},
		{"doctype": "Note"},
		{"doctype": "Event"},
		{"doctype": "Blog Post"},
		{"doctype": "Dashboard"},
		{"doctype": "Country"},
		{"doctype": "Currency"},
		{"doctype": "Newsletter"},
		{"doctype": "Letter Head"},
		{"doctype": "Workflow"},
		{"doctype": "Web Page"},
		{"doctype": "Web Form"},
	]
}

override_whitelisted_methods = {
	# Legacy File APIs
	"creqit.utils.file_manager.download_file": "download_file",
	"creqit.core.doctype.file.file.download_file": "download_file",
	"creqit.core.doctype.file.file.unzip_file": "creqit.core.api.file.unzip_file",
	"creqit.core.doctype.file.file.get_attached_images": "creqit.core.api.file.get_attached_images",
	"creqit.core.doctype.file.file.get_files_in_folder": "creqit.core.api.file.get_files_in_folder",
	"creqit.core.doctype.file.file.get_files_by_search_text": "creqit.core.api.file.get_files_by_search_text",
	"creqit.core.doctype.file.file.get_max_file_size": "creqit.core.api.file.get_max_file_size",
	"creqit.core.doctype.file.file.create_new_folder": "creqit.core.api.file.create_new_folder",
	"creqit.core.doctype.file.file.move_file": "creqit.core.api.file.move_file",
	"creqit.core.doctype.file.file.zip_files": "creqit.core.api.file.zip_files",
	# Legacy (& Consistency) OAuth2 APIs
	"creqit.www.login.login_via_google": "creqit.integrations.oauth2_logins.login_via_google",
	"creqit.www.login.login_via_github": "creqit.integrations.oauth2_logins.login_via_github",
	"creqit.www.login.login_via_facebook": "creqit.integrations.oauth2_logins.login_via_facebook",
	"creqit.www.login.login_via_creqit": "creqit.integrations.oauth2_logins.login_via_creqit",
	"creqit.www.login.login_via_office365": "creqit.integrations.oauth2_logins.login_via_office365",
	"creqit.www.login.login_via_salesforce": "creqit.integrations.oauth2_logins.login_via_salesforce",
	"creqit.www.login.login_via_fairlogin": "creqit.integrations.oauth2_logins.login_via_fairlogin",
	"creqit.api.validatetoken.validate_token": "creqit.api.validatetoken.validate_token"
}

ignore_links_on_delete = [
	"Communication",
	"ToDo",
	"DocShare",
	"Email Unsubscribe",
	"Activity Log",
	"File",
	"Version",
	"Document Follow",
	"Comment",
	"View Log",
	"Tag Link",
	"Notification Log",
	"Email Queue",
	"Document Share Key",
	"Integration Request",
	"Unhandled Email",
	"Webhook Request Log",
	"Workspace",
	"Route History",
	"Access Log",
	"Permission Log",
]

# Request Hooks
before_request = [
	"creqit.recorder.record",
	"creqit.monitor.start",
	"creqit.rate_limiter.apply",
]

after_request = [
	"creqit.monitor.stop",
]

# Background Job Hooks
before_job = [
	"creqit.recorder.record",
	"creqit.monitor.start",
]

if os.getenv("creqit_SENTRY_DSN") and (
	os.getenv("ENABLE_SENTRY_DB_MONITORING") or os.getenv("SENTRY_TRACING_SAMPLE_RATE")
):
	before_request.append("creqit.utils.sentry.set_sentry_context")
	before_job.append("creqit.utils.sentry.set_sentry_context")

after_job = [
	"creqit.recorder.dump",
	"creqit.monitor.stop",
	"creqit.utils.file_lock.release_document_locks",
	"creqit.utils.background_jobs.flush_telemetry",
]

extend_bootinfo = [
	"creqit.utils.telemetry.add_bootinfo",
	"creqit.core.doctype.user_permission.user_permission.send_user_permissions",
]

get_changelog_feed = "creqit.desk.doctype.changelog_feed.changelog_feed.get_feed"

export_python_type_annotations = True

standard_navbar_items = [
	{
		"item_label": "User Settings",
		"item_type": "Action",
		"action": "creqit.ui.toolbar.route_to_user()",
		"is_standard": 1,
	},
	{
		"item_label": "Workspace Settings",
		"item_type": "Action",
		"action": "creqit.quick_edit('Workspace Settings')",
		"is_standard": 1,
	},
	{
		"item_label": "Session Defaults",
		"item_type": "Action",
		"action": "creqit.ui.toolbar.setup_session_defaults()",
		"is_standard": 1,
	},
	{
		"item_label": "Reload",
		"item_type": "Action",
		"action": "creqit.ui.toolbar.clear_cache()",
		"is_standard": 1,
	},
	{
		"item_label": "View Website",
		"item_type": "Action",
		"action": "creqit.ui.toolbar.view_website()",
		"is_standard": 1,
	},
	{
		"item_label": "Apps",
		"item_type": "Route",
		"route": "/apps",
		"is_standard": 1,
	},
	{
		"item_label": "Toggle Full Width",
		"item_type": "Action",
		"action": "creqit.ui.toolbar.toggle_full_width()",
		"is_standard": 1,
	},
	{
		"item_label": "Toggle Theme",
		"item_type": "Action",
		"action": "new creqit.ui.ThemeSwitcher().show()",
		"is_standard": 1,
	},
	{
		"item_type": "Separator",
		"is_standard": 1,
		"item_label": "",
	},
	{
		"item_label": "Log out",
		"item_type": "Action",
		"action": "creqit.app.logout()",
		"is_standard": 1,
	},
]

standard_help_items = [
	{
		"item_label": "About",
		"item_type": "Action",
		"action": "creqit.ui.toolbar.show_about()",
		"is_standard": 1,
	},
	{
		"item_label": "Keyboard Shortcuts",
		"item_type": "Action",
		"action": "creqit.ui.toolbar.show_shortcuts(event)",
		"is_standard": 1,
	},
	{
		"item_label": "System Health",
		"item_type": "Route",
		"route": "/app/system-health-report",
		"is_standard": 1,
	},
	{
		"item_label": "creqit Support",
		"item_type": "Route",
		"route": "https://creqit.io/support",
		"is_standard": 1,
	},
]

# log doctype cleanups to automatically add in log settings
default_log_clearing_doctypes = {
	"Error Log": 14,
	"Email Queue": 30,
	"Scheduled Job Log": 7,
	"Submission Queue": 7,
	"Prepared Report": 14,
	"Webhook Request Log": 30,
	"Unhandled Email": 30,
	"Reminder": 30,
	"Integration Request": 90,
	"Activity Log": 90,
	"Route History": 90,
}

# These keys will not be erased when doing creqit.clear_cache()
persistent_cache_keys = [
	"changelog-*",  # version update notifications
	"insert_queue_for_*",  # Deferred Insert
	"recorder-*",  # Recorder
	"global_search_queue",
]
doc_events = {
    "Leads": {
        "on_update": "creqit.sync_contacts.sync_table_orgl",
        "on_trash": "creqit.sync_contacts.sync_table_orgl"
    },
    "Opportunity": {
        "on_update": "creqit.sync_contacts.sync_table_orgl",
        "on_trash": "creqit.sync_contacts.sync_table_orgl"
    }
}

 
