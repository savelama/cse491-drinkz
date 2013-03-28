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

    def load_db(self, filename):
        drinkz.db.load_db(filename)
            
    def index(self, environ, start_response):
        data = """

<!DOCTYPE HTML>
<html>
<head>
<title>Index Page</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
<script type="text/javascript">
function showAlertButton() {
    alert("You pressed an alert button!");
}
</script>
</head>
<body>
<h1>Index Page</h1>
<p>
<br />
<a href='/recipes'>List Recipes</a><br />
<a href='/inventory'>List Inventory</a><br />
<a href='/liquor_types'>List Liquor Types</a><br/>
<a href='/form'>Convert Liquor Amount Form</a><br/><br/>
<input type="button" onclick="showAlertButton()" value="Show Alert Box"/>
</p>
</body>
</html>
"""
        start_response('200 OK', list(html_headers))
        return [data]

    def recipes(self, environ, start_response):
        content_type = 'text/html'
        text = """

<!DOCTYPE HTML>
<html>
<head>
<title>Recipe List</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>List of Recipes</h1>
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

        text += '</body></html>'

        data = text
        start_response('200 OK', list(html_headers))
        return [data]

    def liquor_types(self, environ, start_response):
        content_type = 'text/html'
        text = """
<!DOCTYPE HTML>
<html>
<head>
<title>Liquor Types List</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>List of Liquor Types</h1>
<ul>
    <li><a href='/'>Home</a></li>
    <li><a href='/recipes'>List Recipes</a></li>
    <li><a href='/inventory'>List Inventory</a></li>
    <li><a href='/liquor_types'>List Liquor Types</a></li>
</ul>
<hr />
<ul>
"""
        bottle_types = list(drinkz.db.get_all_bottle_types())
        for (m, l, t) in bottle_types:
            text += "\t<li>" + t + "</li>\n"
        text += '</ul>'
        text += '</body></html>'

        data = text
        start_response('200 OK', list(html_headers))
        return [data]

    def inventory(self, environ, start_response):
        content_type = 'text/html'
        text = """

<!DOCTYPE HTML>
<html>
<head>
<title>Liquor Inventory</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>Liquor Inventory</h1>
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
        text += '</body></html>'

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

        number, unit = amountToConvert.split();

        amountConverted = drinkz.db.ConvertToMilliters(number, unit)
        amountConverted = str(amountConverted) + ' ml'

        content_type = 'text/html'
        data = """
<!DOCTYPE HTML>
<html>
<head>
<title>Conversion Results</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>Conversion Results</h1><br/>
<p>
        """
        data += "Original amount: %s; Amount converted to mL: %s.  <br/><br/><a href='./'>return to index</a>" % (amountToConvert, amountConverted)
        data += "</p></body></html>"

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

<!DOCTYPE HTML>
<html>
<head>
<title>Conversion Form</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>Convert an Amount to Milliliters</h1><br/>
<form action='recv'>
Enter amount of liquor: <input type='text' name='liquorAmount' size'20'>
<input type='submit'>
</form>
</body>
</html>
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
