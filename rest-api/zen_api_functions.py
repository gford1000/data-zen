import zen_path_data as pd

def _to_lower(value):
	"""
	TODO: Improve this, which is required to convert unicode to lower
	"""
	return str.lower(str(value))

def _check_no_parameters(element, element_value=None):
	"""
	Helper function since several elements should not have parameters defined
	"""
	if element_value:
		# Expected value for this element
		if _to_lower(element.element_value) != _to_lower(element_value):
			return (400, 'Expected element: ' + element_value)

	# Element should not have any matrix parameters
	if len(element.element_params):
		return (400, element.element_value + ' should not have matrix parameters specified')

	return (200, '')

def _build_context(element, parameter_set, base_context=None):
	"""
	Creates a context by starting with the base_context (if defined), then adding/replacing
	it's values with the defaults specified in the parameter set, and then finally replacing
	this value with the value specified in the element if it exists.

	If the element contains values that are not specified in the parameter_set, then this will
	generate an error.
	"""

	# Create the base context_value object
	context_values = base_context if base_context else dict()
	# Iterate over the parameter set to retrieve each parameter's default values and update
	found_params = []
	for param_name, param_details in parameter_set.items():
		# Initially will be using the default
		param_is_defaulted = True
		param_value = param_details[pd.DEFAULT_GENERATOR]()
		# Look for parameter within supplied element
		for supplied_param in element.element_params:
			if _to_lower(supplied_param.name) == _to_lower(param_name):
				# Found parameter in element, so use that instead
				found_params.append(supplied_param)
				param_is_defaulted = False
				param_value = param_details[pd.VALUE_PARSER](supplied_param.value)
				break
		context_values[param_name] = (param_is_defaulted, param_value)

	# Check for unexpected additional parameters supplied by the user
	for supplied_param in element.element_params:
		if supplied_param not in found_params and not context_values.get(supplied_param.name):
			# Additional, unknown parameter was supplied
			return ((400, 'Unknown context parameter supplied: ' + supplied_param.name),None)

	# All good
	return ((200, ''), context_values) 	

def _exec_noop(request_context):
	return {}

def _return_context_parameters(request_context):
	"""
	Returns the context parameters available for the version
	"""
	ret_vals = dict()
	for param_name, param_details in pd.API_VERSION_ASPECT_INFO[request_context.version][pd.CONTEXT][pd.CONTEXT_DEFINED_PARAMETERS].items():
		ret_vals[param_name] = param_details[pd.DESCRIPTION]
	return ret_vals

def _aspect_checker(aspect_element, request_context):
	"""
	Determines the validity of the requested aspect for the specified namespace.

	Also verifies that the method type can be used on this aspect, and that the 
	set of non-default context parameters is correct as well.
	"""

def _namespace_existence_checker(namespace_element, request_context):
	"""
	Determines the validity of the namespace requested, and extracts any additional
	parameters that have been specified with the namespace processing
	"""
	# Retrieve the details of the namespace 
	matched_namespace = pd.NAMESPACE_DATA.get(_to_lower(namespace_element.element_value), None)
	if not matched_namespace:
		return (400, 'Unknown namespace "{}" specified'.format(namespace_element.element_value))

	# Create extended context from optional additional namespace parameters
	((status, error_message), extended_context) = _build_context(namespace_element, matched_namespace[pd.PARAMETERS], context)
	if status != 200:
		return (status, error_message)

	# Namespace has been validated - update request context accordingly
	request_context.namespace = namespace_element.element_value
	request_context.task_context = extended_context
	return (200,'')

def _namespace_element_checker(element, request_context):
	"""
	Validates that we have simply a "namespace" element with no adornment
	"""
	return _check_no_parameters(element, pd.NAMESPACE)

def _context_checker(context_element, request_context):
	"""
	Validates the "context" element in the URL
	"""
	if _to_lower(context_element.element_value) != pd.CONTEXT:
		return ((400, 'No context element specified'), None, None)

	# Create base level context parameters
	((status, error_message), context_values) = _build_context(context_element, pd.API_VERSION_ASPECT_INFO[request_context.version][pd.CONTEXT][pd.CONTEXT_DEFINED_PARAMETERS])
	if status != 200:
		return (status, error_message)

	# All good - store task context in the request context
	request_context.task_context = context_values
	return (200, '')

def _stopped_get_only(request_context):
	"""
	Supplied method must be GET
	"""

	if request_context.method != pd.METHOD_GET:
		return (404, 'Invalid request - {}'.format(request_context.method))

	return (200,'')

def _stopped_put_only(request_context):
	"""
	Supplied method must be PUT
	"""

	if request_context.method != pd.METHOD_PUT:
		return (404, 'Invalid request - {}'.format(request_context.method))

	return (200,'')

