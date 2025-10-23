import creqit


class MaxFileSizeReachedError(creqit.ValidationError):
	pass


class FolderNotEmpty(creqit.ValidationError):
	pass


class FileTypeNotAllowed(creqit.ValidationError):
	pass


from creqit.exceptions import *
