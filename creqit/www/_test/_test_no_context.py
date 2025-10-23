import creqit


# no context object is accepted
def get_context():
	context = creqit._dict()
	context.body = "Custom Content"
	return context
