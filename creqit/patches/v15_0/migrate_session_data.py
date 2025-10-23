import creqit
from creqit.utils import update_progress_bar


def execute():
	creqit.db.auto_commit_on_many_writes = True

	Sessions = creqit.qb.DocType("Sessions")

	current_sessions = (creqit.qb.from_(Sessions).select(Sessions.sid, Sessions.sessiondata)).run(
		as_dict=True
	)

	for i, session in enumerate(current_sessions):
		try:
			new_data = creqit.as_json(creqit.safe_eval(session.sessiondata))
		except Exception:
			# Rerunning patch or already converted.
			continue

		(
			creqit.qb.update(Sessions).where(Sessions.sid == session.sid).set(Sessions.sessiondata, new_data)
		).run()
		update_progress_bar("Patching sessions", i, len(current_sessions))
