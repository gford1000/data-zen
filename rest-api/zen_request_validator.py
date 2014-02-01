import datetime
import collections
import zen_api_functions as af
import zen_path_data as pd
import zen_path_info as pi
import zen_request_context as rc

class APITreeProcessor(object):
	"""
	Class that coordinates validationn of a given URL against a tree-based API definition,
	populating the RequestContext accordingly
	"""
	def __init__(self, validator_fn, executor_fn, stoppable, stopping_validator_fn, next_elements):
		"""
		Initialises an instance of the class with the required functions
		"""
		self.validator_fn = validator_fn
		self.executor_fn = executor_fn
		self.stoppable = stoppable
		self.stopping_validator_fn = stopping_validator_fn
		self.next_elements = next_elements

		# These should never happen
		if not self.validator_fn:
			raise Exception('Inconsistent initialisation of APITreeProcessor: no validator_fn specified')
		if not self.stoppable and len(self.next_elements) == 0:
			raise Exception('Inconsistent initialisation of APITreeProcessor: cannot stop but has no additional nodes')
		if self.stoppable:
			if not self.stopping_validator_fn:
				raise Exception('Inconsistent initialisation of APITreeProcessor: stoppable but no stopping_validator_fn specified')
			if not self.executor_fn:
				raise Exception('Inconsistent initialisation of APITreeProcessor: stoppable but no executor_fn specified')

	def handle_element(self, request_context, element, further_elements = []):
		"""
		Process the current element, using and updating the request context appropriately
		"""

		# Validate the current element
		(status, error_message) = self.validator_fn(element, request_context)

		if status != 200:
			# Validation failure
			return (status, error_message)

		if len(further_elements):
			# More API to process 
			if not len(self.next_elements):
				# More elements in URL than is allowed
				return (404, 'Path too long')

			# Loop through next elements to see if any can continue to valid end-point
			next_element = further_elements[0]
			next_elements = further_elements[1:]
			for processor in self.next_elements:
				(status, error_message) = processor.handle_element(request_context, next_element, next_elements)
				if status == 200:
					# Return at first complete API validation
					return (status, error_message)

			# If we got here then all APITreeProcessor instances failed to provide a validated URL
			return (404, 'Invalid Path')

		# That's all of the URL provided by the requestor
		# Determine is it is complete and accurate
		if not self.stoppable:
			# Can't stop here - invalid URL
			return (404, 'Path too short')

		# Could stop here - check it is valid to do so given prior data
		(status, error_message) = self.stopping_validator_fn(request_context)

		if status != 200:
			# Validation failure
			return (status, error_message)
		else:
			# Looks ok
			request_context.exec_fn = self.executor_fn
			return (200, '')

def _build_1_0_tree():
	"""
	Creates the tree of processors that can interrogate each branch of the API tree
	"""

	namespace_element = APITreeProcessor(
							af._namespace_element_checker,
							af._exec_noop,
							True,	# Returns the list of visible namespaces based on metadata type
							af._stopped_get_only,
							[])

	context_element = APITreeProcessor(
							af._context_checker,
							af._return_context_parameters,
							True,	# Returns the set of context parameters
							af._stopped_get_only,
							[namespace_element]
							)

	# Base of the API tree is the context, since the metadata type is already known
	return context_element


""" The set of api_builders for each version of the API, allowing differentiation by meta type """
_API_VERSIONS = {pd.API_VERSION_1_0: { 'data': _build_1_0_tree, 'model': _build_1_0_tree}}

def validate_request_details(request_context):
	""" 
	All API requests should be of the form /<version>/<metadata [data|model]>/...
	so use this information to identify correct validator
	"""

	# Retrieve api builder based on version and meta type
	api_builder_map = _API_VERSIONS.get(request_context.version, None)
	if not api_builder_map:
		return (500, 'Unknown version of API specified: ' + request_context.version)

	api_builder = api_builder_map.get(request_context.meta_type, None)
	if not api_builder:
		return (500, 'Unknown meta data type of API specified: ' + request_context.meta_type)

	# Attempt to validate the request with the correct validator
	try:
		processor = api_builder()
		return processor.handle_element(
								request_context,
								request_context.path.path_elements[1],
								request_context.path.path_elements[2:] if len(request_context.path.path_elements) > 1 else [])

	except Exception as e:
		return (500, e.message)


if __name__ == "__main__":

	class test_request(object):
		def __init__(self, method, requestor):
			self.method = method
			self.remote_user = requestor

	def run_test(version, meta, url, method, expected_status=200):
		url_parts = url.split('?')
		url_path = url_parts[0]
		url_qp = url_parts[1] if len(url_parts) > 1 else ''

		request_context = rc.RequestContext(version, meta, pi.PathInfo(url_path, url_qp), test_request(method, None))
		(status, error_message) = validate_request_details(request_context)

		if status == expected_status:
			print "Testing:", url, method, "- passed"
		else:
			print "Testing:", url, method, "- failed", '({})'.format(status), error_message

	# Run some tests
	run_test('','', '', pd.METHOD_GET, 500)
	run_test('1.0','', '', pd.METHOD_GET, 500)
	run_test('1.0','model', '', pd.METHOD_GET, 500)
	run_test('1.0','model', '/context', pd.METHOD_GET, 200)
	run_test('1.0','model', '/context', pd.METHOD_POST, 404)
	run_test('1.0','model', '/context;a=b', pd.METHOD_GET, 400)
	run_test('1.0','model', '/context;as_of=b', pd.METHOD_GET, 200)
	run_test('1.0','model', '/context;as_of=b', pd.METHOD_GET, 200)
	run_test('1.0','model', '/context;as_Of=b/namesp', pd.METHOD_GET, 404)
	run_test('1.0','model', '/context;as_of=b/namespace', pd.METHOD_GET, 200)
	run_test('1.0','model', '/context;as_of=b/namespAce', pd.METHOD_GET, 200)
	run_test('1.0','model', '/context;as_of=b/namespAce', pd.METHOD_POST, 404)
	run_test('1.0','model', '/context;as_of=b/namespace/fred', pd.METHOD_GET, 200)
