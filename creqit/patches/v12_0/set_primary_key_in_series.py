import creqit


def execute():
	# if current = 0, simply delete the key as it'll be recreated on first entry
	creqit.db.delete("Series", {"current": 0})

	duplicate_keys = creqit.db.sql(
		"""
		SELECT name, max(current) as current
		from
			`tabSeries`
		group by
			name
		having count(name) > 1
	""",
		as_dict=True,
	)

	for row in duplicate_keys:
		creqit.db.delete("Series", {"name": row.name})
		if row.current:
			creqit.db.sql("insert into `tabSeries`(`name`, `current`) values (%(name)s, %(current)s)", row)
	creqit.db.commit()

	creqit.db.sql("ALTER table `tabSeries` ADD PRIMARY KEY IF NOT EXISTS (name)")
