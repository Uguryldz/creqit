# Copyright (c) 2021, creqit Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE

from creqit.exceptions import ValidationError


class NewsletterAlreadySentError(ValidationError):
	pass


class NoRecipientFoundError(ValidationError):
	pass


class NewsletterNotSavedError(ValidationError):
	pass
