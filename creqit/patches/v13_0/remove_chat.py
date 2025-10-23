import click

import creqit


def execute():
	creqit.delete_doc_if_exists("DocType", "Chat Message")
	creqit.delete_doc_if_exists("DocType", "Chat Message Attachment")
	creqit.delete_doc_if_exists("DocType", "Chat Profile")
	creqit.delete_doc_if_exists("DocType", "Chat Token")
	creqit.delete_doc_if_exists("DocType", "Chat Room User")
	creqit.delete_doc_if_exists("DocType", "Chat Room")
	creqit.delete_doc_if_exists("Module Def", "Chat")

	click.secho(
		"Chat Module is moved to a separate app and is removed from creqit in version-13.\n"
		"Please install the app to continue using the chat feature: https://github.com/creqit/chat",
		fg="yellow",
	)
