#! /usr/bin/env python
from wsgiref.simple_server import make_server
import urlparse
import simplejson
import drinkz.db

dispatch = {
    '/' : 'index',
    '/recipes' : 'recipes',
    '/inventory' : 'inventory',
    '/liquor_types' : 'liquor_types',
    '/error' : 'error',
    '/form' : 'form',
    '/recv' : 'recv',
    '/rpc'  : 'dispatch_rpc'
}

html_headers = [('Content-type', 'text/html')]

class SimpleApp(object):
    def __call__(self, environ, start_response):

        path = environ['PATH_INFO']
        fn_name = dispatch.get(path, 'error')

        # retrieve 'self.fn_name' where 'fn_name' is the
        # value in the 'dispatch' dictionary corresponding to
        # the 'path'.
        fn = getattr(self, fn_name, None)

        if fn is None:
            start_response("404 Not Found", html_headers)
            return ["No path %s found" % path]

        return fn(environ, start_response)
            
    def index(self, environ, start_response):
        data = """
Visit:<br />
<a href='/recipes'>List Recipes</a><br />
<a href='/inventory'>List Inventory</a><br />
<a href='/liquor_types'>List Liquor Types</a><br/>
<a href='/form'>Convert Liquor Amount Form</a>
"""
        start_response('200 OK', list(html_headers))
        return [data]

    def recipes(self, environ, start_response):
        content_type = 'text/html'
        text = """
<h1>Matthew Savela's HW4 Output -- List of Recipes</h1>
<ul>
    <li><a href='/'>Home</a></li>
    <li><a href='/recipes'>List Recipes</a></li>
    <li><a href='/inventory'>List Inventory</a></li>
    <li><a href='/liquor_types'>List Liquor Types</a></li>
</ul>
<hr />
<ul>
"""
        recipes = list(drinkz.db.get_all_recipes())
        for r in recipes:
            missing_ingredients = r.need_ingredients()
            if len(missing_ingredients) == 0:
                haveIngredients = "Yes"
            else:
                haveIngredients = "No"

            text += "\t<li>" + r._name + " - " + haveIngredients + "</li>\n"
        text += '</ul>'

        data = text
        start_response('200 OK', list(html_headers))
        return [data]

    def liquor_types(self, environ, start_response):
        content_type = 'text/html'
        text = """
<h1>Matthew Savela's HW4 Output -- List of Liquor Types</h1>
<ul>
    <li><a href='/'>Home</a></li>
    <li><a href='/recipes'>List Recipes</a></li>
    <li><a href='/inventory'>List Inventory</a></li>
    <li><a href='/liquor_types'>List Liquor Types</a></li>
</ul>
<hr />
<ul>
"""
        bottle_types = list(drinkz.db.get_bottle_types())
        for (m, l, t) in bottle_types:
            text += "\t<li>" + t + "</li>\n"
        text += '</ul>'

        data = text
        start_response('200 OK', list(html_headers))
        return [data]

    def inventory(self, environ, start_response):
        content_type = 'text/html'
        text = """
<h1>Matthew Savela's HW4 Output -- Liquor Inventory</h1>
<ul>
    <li><a href='/'>Home</a></li>
    <li><a href='/recipes'>List Recipes</a></li>
    <li><a href='/inventory'>List Inventory</a></li>
    <li><a href='/liquor_types'>List Liquor Types</a></li>
</ul>
<hr />
<ul>
"""
        liquor_inventory = list(drinkz.db.get_liquor_inventory())
        for (m,l) in liquor_inventory:
            amount = drinkz.db.get_liquor_amount(m,l)
            text += "\t<li>" + m + " - " + l + " - " + str(amount) + "ml</li>\n"
        text += '</ul>'

        data = text
        start_response('200 OK', list(html_headers))
        return [data]

    def error(self, environ, start_response):
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response('200 OK', list(html_headers))
        return [data]

    def form(self, environ, start_response):
        data = form()

        start_response('200 OK', list(html_headers))
        return [data]
   
    def recv(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        amountToConvert = results['liquorAmount'][0]
        amountConverted = drinkz.db.convert_to_ml(amountToConvert)
        amountConverted = str(amountConverted) + ' ml'

        content_type = 'text/html'
        data = "Original amount: %s; Amount converted to mL: %s.  <a href='./'>return to index</a>" % (amountToConvert, amountConverted)

        start_response('200 OK', list(html_headers))
        return [data]

    def dispatch_rpc(self, environ, start_response):
        # POST requests deliver input data via a file-like handle,
        # with the size of the data specified by CONTENT_LENGTH;
        # see the WSGI PEP.
        
        if environ['REQUEST_METHOD'].endswith('POST'):
            body = None
            if environ.get('CONTENT_LENGTH'):
                length = int(environ['CONTENT_LENGTH'])
                body = environ['wsgi.input'].read(length)
                response = self._dispatch(body) + '\n'
                start_response('200 OK', [('Content-Type', 'application/json')])

                return [response]

        # default to a non JSON-RPC error.
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response('200 OK', list(html_headers))
        return [data]

    def _decode(self, json):
        return simplejson.loads(json)

    def _dispatch(self, json):
        rpc_request = self._decode(json)

        method = rpc_request['method']
        params = rpc_request['params']
        
        rpc_fn_name = 'rpc_' + method
        fn = getattr(self, rpc_fn_name)
        result = fn(*params)

        response = { 'result' : result, 'error' : None, 'id' : 1 }
        response = simplejson.dumps(response)
        return str(response)

    def rpc_hello(self):
        return 'world!'

    def rpc_add(self, a, b):
        return int(a) + int(b)
    
def form():
    return """
<form action='recv'>
Enter amount of liquor: <input type='text' name='liquorAmount' size'20'>
<input type='submit'>
</form>
"""

if __name__ == '__main__':
    import random, socket
    port = random.randint(8000, 9999)
    
    app = SimpleApp()
    
    httpd = make_server('', port, app)
    print "Serving on port %d..." % port
    print "Try using a Web browser to go to http://%s:%d/" % \
          (socket.getfqdn(), port)
    httpd.serve_forever()
