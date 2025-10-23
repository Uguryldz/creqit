import creqit


def execute():
	"""Remove stale docfields from legacy version"""
	creqit.db.delete("DocField", {"options": "Data Import", "parent": "Data Import Legacy"})
