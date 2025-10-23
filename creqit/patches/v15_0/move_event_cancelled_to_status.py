import creqit


def execute():
	Event = creqit.qb.DocType("Event")
	query = (
		creqit.qb.update(Event)
		.set(Event.event_type, "Private")
		.set(Event.status, "Cancelled")
		.where(Event.event_type == "Cancelled")
	)
	query.run()
