import datetime

def _join_str(a, b, separator):
    """ Helper function to manage concatenation appropriately """
    if len(a) and len(b):
        return separator.join((a, b))
    elif len(a):
        return a
    else:
        return b

def _pi_str(self):
    """ __str__ function for PathInfo """

    def params_str(param_list, separator):
        # Stringizes a parameter and its value
        ret_str = ''
        for p in param_list:
            if p.value != True:
                ret_str = _join_str(ret_str, _join_str(p.name, p.value, '='), separator)
            else:
                ret_str = _join_str(ret_str, p.name, separator)
        return ret_str       

    def element_str(element):
        # Stringizes a specific element
        return _join_str(element.element_value, params_str(element.element_params, ';'), ';')

    ret_str = ''
    if len(self.path_elements):
        for element in self.path_elements:
            ret_str = _join_str(ret_str, element_str(element), '/')

    if len(self.query_parameters):
        query_str = params_str(self.query_parameters, '&')
        ret_str = _join_str(ret_str, query_str, '?')

    return _join_str('/', ret_str, '')

ElementInfo = collections.namedtuple('ElementInfo', ['element_value', 'element_params'])
ParamInfo = collections.namedtuple('ParamInfo', ['name', 'value'])
PathInfo = collections.namedtuple('PathInfo', ['path_elements', 'query_parameters'])
PathInfo.__str__ = _pi_str



METHOD_GET = 'GET'
METHOD_POST = 'POST'

API_VERSION_1_0 = '1.0'

DESCRIPTION = 'description'
PARAMETERS = 'parameters'

ASPECTS = 'aspects'
ASPECT_VALUE_TYPES = 'value_types'
ASPECT_VALUE_RULES = 'value_rules'
ASPECT_CODE_RULES = 'code_rules'
ASPECT_DEPENDENTS = 'dependents'
ASPECT_HISTORY = 'history'
CONTEXT = 'context'
CONTEXT_DEFINED_PARAMETERS = 'defined_parameters'
CONTEXT_ASPECT_APPLICABILITY = 'aspect_applicability'
NAMESPACE = 'namespace'

CONTEXT_AS_OF = 'as_of'

def as_of_date_default():
	return datetime.datetime.utcnow()
def as_of_user_supplied(date_str):
	# To do: parse date that was supplied
	return as_of_date_default()

NAMESPACE_DATA = { 'global':
						{ DESCRIPTION:'',
                          PARAMETERS:{},
                          ASPECTS:[ASPECT_VALUE_TYPES, ASPECT_VALUE_RULES, ASPECT_CODE_RULES, ASPECT_DEPENDENTS, ASPECT_HISTORY] 
                        } 
                 }

API_VERSION_ASPECT_INFO = { 
			API_VERSION_1_0 : {
				ASPECTS:
					{  ASPECT_VALUE_TYPES:[METHOD_POST, METHOD_GET],
	                   ASPECT_VALUE_RULES:[METHOD_GET, METHOD_POST],
	                   ASPECT_CODE_RULES:[METHOD_GET, METHOD_POST],
	                   ASPECT_DEPENDENTS:[METHOD_GET],
	                   ASPECT_HISTORY:[METHOD_GET]
	                },
	            CONTEXT:
	            	{
	            		CONTEXT_DEFINED_PARAMETERS:
	            			{
	            				CONTEXT_AS_OF:(as_of_date_default, as_of_user_supplied)
	            			},
	            		CONTEXT_ASPECT_APPLICABILITY:
	            			{
	            				ASPECT_VALUE_TYPES:[CONTEXT_AS_OF],
	            				ASPECT_VALUE_RULES:[CONTEXT_AS_OF],
	            				ASPECT_CODE_RULES:[CONTEXT_AS_OF],
	            				ASPECT_DEPENDENTS:[],
	            				ASPECT_HISTORY:[]
	            			}
	            	}
            }}

def _check_no_parameters(element, element_value=None):
	"""
	Helper function since several elements should not have parameters defined
	"""
	if element_value:
		# Expected value for this element
		if element.element_value != element_value:
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
	context_values = base_context if not None else dict()
	# Iterate over the parameter set to retrieve each parameter's default values and update
	for param_name, (param_default_creator, parse_fn_for_user_value) in parameter_set.items():
		# Initially will be using the default
		param_is_defaulted = True
		param_value = param_default_creator()
		# Look for parameter within supplied element
		for supplied_param in element.element_params:
			if supplied_param.name == param_name:
				# Found parameter in element, so use that instead
				param_is_defaulted = False
				param_value = parse_fn_for_user_value(supplied_param.value)
				break
		context_values[param_name] = (param_is_defaulted, param_value)

	# Check for unexpected additional parameters supplied by the user
	for supplied_param in element.element_params:
		if not context_values.get(supplied_param.name):
			# Additional, unknown parameter was supplied
			return ((400, 'Unknown context parameter supplied: ' + supplied_param.name),None)
	
	# All good
	return ((200, ''), context_values) 	

def _version_1_0_aspect_checker(element_list, context, namespace, method):
	"""
	Determines the validity of the requested aspect for the specified namespace.

	Also verifies that the method type can be used on this aspect, and that the 
	set of non-default context parameters is correct as well.
	"""

	

def _version_1_0_namespace_existence_checker(element_list, context, namespace, method):
	"""
	Determines the validity of the namespace requested, and extracts any additional
	parameters that have been specified with the namespace processing
	"""
	# Expect an element to be available
	if not len(element_list):
		return ((404, 'Bad request'), None, None)

	namespace_element = element_list[0]

	# Retrieve the details of the namespace 
	matched_namespace = NAMESPACE_DATA.get(namespace_element.element_value, None)
	if not matched_namespace:
		return ((400, 'Unknown namespace "{}" specified'.format(namespace_element.element_value)),None, None)

	# Create extended context from optional additional namespace parameters
	((status, error_message), extended_context) = _build_context(namespace_element, matched_namespace[PARAMETERS], context)
	if status != 200:
		return ((status, error_message), None, None)

	# Namespace has been validated
	return ((status, ''), extended_context, namespace_element.element_value)


def _version_1_0_namespace_element_checker(element_list, context, namespace, method):
	"""
	Validates that we have simply a "namespace" element with no adornment
	"""
	# Expect an element to be available
	if not len(element_list):
		return ((404, 'Bad request'), None, None)

	check_state = _check_no_parameters(element_list[0], NAMESPACE)
	return (check_state, context, namespace)

def _version_1_0_context_checker(element_list, context, namespace, method):
	"""
	Validates the "context" element in the URL
	"""
	# Expect an element to be available
	if not len(element_list):
		return ((404, 'Bad request'), None, None)

	# First element should be "context", with zero or more matrix parameters
	context_element = element_list[0]

	if context_element.element_value != CONTEXT:
		return ((400, 'No context element specified'), None, None)

	# Create base level context parameters
	((status, error_message), context_values) = _build_context(context_element, API_VERSION_ASPECT_INFO[API_VERSION_1_0][CONTEXT][CONTEXT_DEFINED_PARAMETERS])
	if status != 200:
		return ((status, error_message), None, None)

	# All good - return context as well
	return ((200,''), context_values, None)

def _version_1_0_validation_builder():
	"""
	Provides the sequence of validation steps to perform on the URL for version 1.0 of the API
	"""
	validation_sequence = []
	validation_sequence.append(_version_1_0_context_checker)
	validation_sequence.append(_version_1_0_namespace_element_checker)
	validation_sequence.append(_version_1_0_namespace_existence_checker)
	return validation_sequence

def _version_1_0_request_validator(element_list, method):
	"""
	Iterates the supplied elements from the URL, sequentially involving the validator functions.
	Processing stops at the first error.
	"""
	context = None
	namespace = None
	for validator in _version_1_0_validation_builder():
		((status, error_message), context, namespace) = validator(element_list[1:], context, namespace, method)
		if status != 200:
			return (status, error_message)
	return (200, '')

""" The set of validators for each version of the API """
_API_VERSIONS = {API_VERSION_1_0:_version_1_0_request_validator}

def validate_request_details(path_info, method):
	""" 
	All API requests should be of the form /<version>/context[matrix parameters]/namespace/...
	so use this information to identify correct validator
	"""

	# Must have some elements
	if not len(path_info.path_elements):
		return (404, 'Incorrect path specified')

	version_element = path_info.path_elements[0]
	
	# Version should not have any matrix parameters
	(status, error) = _check_no_parameters(version_element)
	if status != 200:
		return (status, error)

	# Retrieve validator from the version list
	version_validator = _API_VERSIONS[version_element.element_value]
	if not version_validator:
		return (404, 'Invalid version of API specified: ' + version_element.element_value)

	# Attempt to validate the request with the correct validator
	try:
		return version_validator(path_info.path_elements[1:], method)
	except Exception as e:
		return (500, e.message)
