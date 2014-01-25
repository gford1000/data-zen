"""
This defines the whole RESTful API that will run within flask
"""
import os
import collections
from flask import Flask, abort, request, jsonify

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

def _get_parameter_info(param_list_str, separator):
    """
    String should be splittable by the separator into <name>=<value> strings,
    which define the ParamInfo() information
    """
    params_list = []
    for param in param_list_str.split(separator):
        assignment = param.split("=")
        if len(assignment) == 1:
            # Store True to simplify later processing
            params_list.append(ParamInfo(assignment[0], True))
        else:
            params_list.append(ParamInfo(assignment[0], assignment[1]))
    return params_list


def _get_element_info(element):
    """
    Extracts element value and any parameters - here we are looking at a single element of the URL,
    which will be of the form <element_value>[;<element_param_name>=<element_param_value>], where
    an arbitrary number of parameters may be specified, or simply an element_param_name on its 
    own, which is acting as a boolean flag.
    """

    # Split by ";", the first value will be the element value, remainder are parameters
    items = element.split(";")
    ei = ElementInfo(items[0], [])

    if len(items) == 2:
        ei = ElementInfo(items[0], _get_parameter_info(items[1], ';'))       
    elif len(items) > 2:
        ei = ElementInfo(items[0], _get_parameter_info(';'.join(items[1:]), ';'))

    return ei

def _create_path_info(path, query_string):
    """
    Deconstruct the path into a PathInfo tuple, with the elements decomposed into
    an ordered list of ElementInfo objects, anq query parameters decomposed into 
    an ordered list of ParamInfo objects.

    No validation is performed on the path or parameters (i.e. duplicates might exist)
    """
    path_info = PathInfo([], [])

    # Split each element in the path
    for path_value in path.split("/"):
        path_info.path_elements.append(_get_element_info(path_value))

    # Split query parameters in the path
    if len(query_string):
        for pi in _get_parameter_info(query_string, '&'):
            path_info.query_parameters.append(pi)

    return path_info

app = Flask(__name__)

@app.route('/')
@app.route('/<path:varargs>')
def routing_start(varargs = None):
    if varargs:
        # Deconstruct string to ordered path with parameters
        path = _create_path_info(varargs, request.query_string)
        return "Done!"
        
    else:
        # Should never get here
        abort(404)

if __name__ == "__main__":
    app.run(debug=True)
