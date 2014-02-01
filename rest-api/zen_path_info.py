import collections

ElementInfo = collections.namedtuple('ElementInfo', ['element_value', 'element_params'])
ParamInfo = collections.namedtuple('ParamInfo', ['name', 'value'])

class PathInfo(object):
    """
    The PathInfo object decomposes the provided url path and query parameters into
    ordered lists of ElementInfo and ParamInfo respectively.

    The elements can be retrieved by calling PathInfo.path_elements

    The query parameters can be retrieved by calling PathInfo.query_parameters

    The elements can also contain matrix parameters, which are available in the corresponding
    ElementInfo.element_params

    """
    def __init__(self, url_path, url_query_parameters):
        self.path_elements = []
        self.query_parameters = []
        self.slash_at_start = True
        self.slash_at_end = False
        self._create_path_info(url_path, url_query_parameters)

    def _create_path_info(self, path, query_string):
        """
        Deconstruct the path into a PathInfo tuple, with the elements decomposed into
        an ordered list of ElementInfo objects, anq query parameters decomposed into 
        an ordered list of ParamInfo objects.

        No validation is performed on the path or parameters (i.e. duplicates might exist)
        """

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

        # Expects to start with '/'
        if path[0] != '/':
            path = '/' + path
            self.slash_at_start = False

        # Not expecting to end with '/' - remove it if present
        if len(path) > 1 and path[len(path)-1] == '/':
            self.slash_at_end = True
            path = path[:-1]

        # Split each element in the path
        for path_value in path.split("/"):
            self.path_elements.append(_get_element_info(path_value))

        # Split query parameters in the path
        if len(query_string):
            for pi in _get_parameter_info(query_string, '&'):
                self.query_parameters.append(pi)

    def __str__(self):
        """ __str__ function for PathInfo """

        def _join_str(a, b, separator):
            """ Helper function to manage concatenation appropriately """
            if len(a) and len(b):
                return separator.join((a, b))
            elif len(a):
                return a
            else:
                return b

        def _params_str(param_list, separator):
            # Stringizes a parameter and its value
            ret_str = ''
            for p in param_list:
                if p.value != True:
                    ret_str = _join_str(ret_str, _join_str(p.name, p.value, '='), separator)
                else:
                    ret_str = _join_str(ret_str, p.name, separator)
            return ret_str       

        def _element_str(element):
            # Stringizes a specific element
            return _join_str(element.element_value, _params_str(element.element_params, ';'), ';')

        ret_str = ''
        if len(self.path_elements):
            for element in self.path_elements:
                ret_str = _join_str(ret_str, _element_str(element), '/')

        if len(self.query_parameters):
            query_str = _params_str(self.query_parameters, '&')
            ret_str = _join_str(ret_str, query_str, '?')

        if self.slash_at_end:
            ret_str = _join_str(ret_str, '/', '')

        if self.slash_at_start:
            ret_str = _join_str('/', ret_str, '')

        return ret_str

if __name__ == "__main__":

    def run_test(url):
        url_parts = url.split('?')
        url_path = url_parts[0]
        url_qp = url_parts[1] if len(url_parts) > 1 else '' 

        pi = PathInfo(url_path, url_qp)
        pis = str(pi)

        pi_parts = pis.split('?')

        passed = pi_parts[0] == url_path
        passed = passed and len(url_parts) == len(pi_parts)

        if passed and len(url_parts) > 1:
            passed = url_parts[1] == pi_parts[1]

        if passed:
            print 'Request:', url, '- passed'
        else:
            print 'Request:', url, '- failed (', pi_parts[0], ')'

    # Define some tests
    run_test('/')
    run_test('/a')
    run_test('a/')
    run_test('/a/b')
    run_test('/a/b/c')
    run_test('/a/b/c/')
    run_test('/a/b/c?x=1')
    run_test('a/b/c?x=1')
    run_test('/a/b/c?x=1&y=2')
    run_test('/a/b/c?x=1&y=2&z=3')
    run_test('/a;xx=yy/b/c?x=1&y=2&z=3')
    run_test('/a;xx=yy;zz=aa/b/c?x=1&y=2&z=3')
    run_test('/a;xx=yy;zz=aa;ii=jj/b/c?x=1&y=2&z=3')
    run_test('/a;xx=yy;zz=aa;ii=jj/b/c;rm=qq?x=1&y=2&z=3')
    run_test('a;xx=yy;zz=aa;ii=jj/b/c;rm=qq?x=1&y=2&z=3')




