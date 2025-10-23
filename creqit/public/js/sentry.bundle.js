import * as Sentry from "@sentry/browser";

Sentry.init({
	dsn: creqit.boot.sentry_dsn,
	release: creqit?.boot?.versions?.creqit,
	autoSessionTracking: false,
	initialScope: {
		// don't use creqit.session.user, it's set much later and will fail because of async loading
		user: { id: creqit.boot.sitename },
		tags: { creqit_user: creqit.boot.user.name ?? "Unidentified" },
	},
	beforeSend(event, hint) {
		// Check if it was caused by creqit.throw()
		if (
			hint.originalException instanceof Error &&
			hint.originalException.stack &&
			hint.originalException.stack.includes("creqit.throw")
		) {
			return null;
		}
		return event;
	},
});
