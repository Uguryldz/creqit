import creqit


def execute():
	creqit.reload_doctype("Translation")
	creqit.db.sql(
		"UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0"
	)
