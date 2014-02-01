import datetime

METHOD_GET = 'GET'
METHOD_POST = 'POST'

API_VERSION_1_0 = '1.0'

DESCRIPTION = 'description'
PARAMETERS = 'parameters'
DEFAULT_GENERATOR = 'default_fn'
VALUE_PARSER = 'parser_fn'

ASPECTS = 'aspects'
ASPECT_VALUE_TYPES = 'value_types'
ASPECT_VALUE_RULES = 'value_rules'
ASPECT_CODE_RULES = 'code_rules'
ASPECT_DEPENDENTS = 'dependents'
ASPECT_HISTORY = 'history'

DATA = 'data'
MODEL = 'model'

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
	            				CONTEXT_AS_OF: 
	            					{
	            						DESCRIPTION:'The chronological time in the system at which the request is to be executed.  Defaults to now.',
	            						DEFAULT_GENERATOR:as_of_date_default,
	            						VALUE_PARSER:as_of_user_supplied
	            					}
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
