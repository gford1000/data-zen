class RequestContext(object):
	"""
	Contextual information required to process the API request
	"""
	def __init__(self, version, meta_type, path, request):
		"""
		At creation of the context, should know the API version, the meta_type
		of the request, the URL and the request method
		"""
		self.version = version
		self.meta_type = meta_type
		self.path = path
		self.method = request.method
		self.requestor = request.remote_user 
		self.task_context = None
		self.namespace = None
		self.exec_fn = None

