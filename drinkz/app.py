#! /usr/bin/env python
from wsgiref.simple_server import make_server
import urlparse
import simplejson
from Cookie import SimpleCookie
import db
import recipes
import uuid

dispatch = {
    '/' : 'index',
    '/recipes' : 'recipes',
    '/inventory' : 'inventory',
    '/liquor_types' : 'liquor_types',
    '/error' : 'error',
    '/form' : 'form',
    '/addliquortype' : 'addliquortype',
    '/addtoinventory': 'addtoinventory',
    '/addrecipe': 'addrecipe',
    '/recv' : 'recv',
    '/recv2': 'recv2',
    '/recv3': 'recv3',
    '/recv4': 'recv4',
    '/rpc'  : 'dispatch_rpc',
    '/login_1' : 'login1',
    '/login1_process' : 'login1_process',
    '/logout' : 'logout',
    '/status' : 'status'
}

usernames = {}

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
        db.load_db(filename)
            
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
<script type='text/javascript' src='http://code.jquery.com/jquery-1.9.1.min.js'></script>
<script type="text/javascript">
function showAlertButton() {
    $.ajax({
        type: 'POST',
        url: '/rpc',
        dataType: 'json',
        data: JSON.stringify({method: 'showAlert', params: [], id: '0'}),
        success: function(data) {
            alert(data.result);
        },
        error: function(data) {
            alert(data.error);
        }
    });
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
<a href='/form'>Convert Liquor Amount Form</a><br/>
<a href='/addliquortype'>Add a liquor type</a><br/>
<a href='/addtoinventory'>Add liquor to inventory</a><br/>
<a href='/addrecipe'>Add a recipe</a><br/>
<a href='/login_1'>Login Page</a><br/>
<a href='/logout'>Logout Page</a><br/>
<a href='/status'>Status Page</a><br/>
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
        recipes = list(db.get_all_recipes())
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
        bottle_types = list(db.get_bottle_types())
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
        liquor_inventory = list(db.get_liquor_inventory())
        for (m,l) in liquor_inventory:
            amount = db.get_liquor_amount(m,l)
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

    def addrecipe(self, environ, start_response):
        data = formAddRecipe()

        start_response('200 OK', list(html_headers))
        return [data]

    def addliquortype(self, environ, start_response):
        data = formAddLiquorType()

        start_response('200 OK', list(html_headers))
        return [data]

    def addtoinventory(self, environ, start_response):
        data = formAddToInventory()

        start_response('200 OK', list(html_headers))
        return [data]
   
   # Used to convert amount to milliliters
    def recv(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        amountToConvert = results['liquorAmount'][0]

        amountConverted = db.convert_to_ml(amountToConvert)
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

    # Used to add liquor types to the database
    def recv2(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        liquorMfg = results['liquorMfg'][0]
        liquorName = results['liquorName'][0]
        liquorType = results['liquorType'][0]

        db.add_bottle_type(liquorMfg, liquorName, liquorType)

        content_type = 'text/html'
        data = """
<!DOCTYPE HTML>
<html>
<head>
<title>Liquor Type Added</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>Liquor Type Successfully Added!</h1><br/>
<a href='./'>Return to index</a>
<p>
        """
        start_response('200 OK', list(html_headers))
        return [data]

    # Used to add liquor types to the database
    def recv3(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        liquorMfg = results['liquorMfg'][0]
        liquorName = results['liquorName'][0]
        liquorAmount = results['liquorAmount'][0]

        bottleTypeExists = db._check_bottle_type_exists(liquorMfg, liquorName)
        if(bottleTypeExists == True):
            db.add_to_inventory(liquorMfg, liquorName, liquorAmount)

        content_type = 'text/html'
        data = """
<!DOCTYPE HTML>
<html>
<head>
<title>Liquor Amount Added</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>"""
        if(bottleTypeExists == True):
            data += "<h1>Liquor Successfully Added to Inventory!</h1><br/>"
        else:
            data += "<h1>Error! Liquor bottle type could not be found. Liquor not added.</h1>"
        data += "<a href='./'>Return to index</a></body></html>"


        start_response('200 OK', list(html_headers))
        return [data]

    # Used to add recipes to the database
    def recv4(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        recipeName = results['recipeName'][0]
        ingredients = results['ingredients'][0].split(',')

        Ingredients = []
        i = 0
        while i < len(ingredients):
            Ingredients.append((ingredients[i], ingredients[i+1]))
            i+=2

        db.add_recipe(recipes.Recipe(recipeName, Ingredients))

        content_type = 'text/html'
        data = """
<!DOCTYPE HTML>
<html>
<head>
<title>Liquor Amount Added</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body><h1>Liquor Successfully Added to Inventory!"""

        #data += Ingredients[1][0]
        data += """
</h1><br/>
</body>
</html>"""

        start_response('200 OK', list(html_headers))
        return [data]


    # Used to log in a user
    def login1(self, environ, start_response):

        content_type = 'text/html'
        data = """
<!DOCTYPE HTML>
<html>
<head>
<title>Login Page</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body><h1>Login Page</h1><br/><br/>

<form action='login1_process'>
Username: <input type='text' name='name' size='15'>
<input type='submit' value='log in'>
</form>
<br/><br/>
<a href="/">Return to Index</a>

</body>
</html>"""


        start_response('200 OK', list(html_headers))
        return [data]

    def login1_process(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        name = results['name'][0]
        content_type = 'text/html'

        # authentication would go here -- is this a valid username/password,
        # for example?

        k = str(uuid.uuid4())
        usernames[k] = name

        headers = list(html_headers)
        headers.append(('Location', '/status'))
        headers.append(('Set-Cookie', 'name1=%s' % k))

        start_response('302 Found', headers)
        return ["Redirect to /status..."]

    def logout(self, environ, start_response):
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name1' in c:
                key = c.get('name1').value
                name1_key = key

                if key in usernames:
                    del usernames[key]
                    print 'DELETING'

        pair = ('Set-Cookie',
                'name1=deleted; Expires=Thu, 01-Jan-1970 00:00:01 GMT;')
        headers = list(html_headers)
        headers.append(('Location', '/status'))
        headers.append(pair)

        start_response('302 Found', headers)
        return ["Redirect to /status..."]

    def status(self, environ, start_response):
        start_response('200 OK', list(html_headers))

        name1 = ''
        name1_key = '*empty*'
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name1' in c:
                key = c.get('name1').value
                name1 = usernames.get(key, '')
                name1_key = key

        content_type = 'text/html'
        data = """
<!DOCTYPE HTML>
<html>
<head>
<title>Status Page</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body><h1>Status Page</h1><br/><br/><p>"""

        if(name1_key != "*empty*"):
            data += "Logged in as: "
            data += name1
            data += """
    </p><br/>"""

            data += """
    <p>Your key is:
            """
            data += name1_key
        else:
            data += "You are logged out"
        data += """
 </p><br/><br/>
<a href="/">Return to Index</a>
</body>
</html>"""


        return [data]
                
        #title = 'login status'
        #template = env.get_template('status.html')
        #return str(template.render(locals()))


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

    # RPC Function for Homework #5

    def rpc_ConvertToMilliters(self, amount):
        return db.convert_to_ml(amount);

    def rpc_AddToInventory(self, mfg, liquor, amount):
        db.add_to_inventory(mfg, liquor, amount);

    def rpc_AddLiquorType(self, mfg, liquorName, liquorType):
        db.add_bottle_type(mfg, liquorName, liquorType);

    def rpc_AddRecipe(self, recipeName, ingredients):

        ingredients = ingredients.split(',')
        Ingredients = []
        i = 0
        while i < len(ingredients):
            Ingredients.append((ingredients[i], ingredients[i+1]))
            i+=2

        db.add_recipe(recipes.Recipe(recipeName, Ingredients));

    def rpc_GetLiquorTypes(self):
        return list(db.get_bottle_types());

    def rpc_GetLiquorInventory(self):
        return list(db.get_liquor_inventory());

    def rpc_GetRecipes(self):
        recipes = list(db.get_all_recipes());
        recipeNames = list()

        for r in recipes:
            recipeNames.append(r._name)

        return recipeNames

    def rpc_showAlert(self):
        return "This is a JavaScript alert triggered by an AJAX call!";

    
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
Enter amount of liquor: <input type='text' name='liquorAmount' size='20'>
<input type='submit'>
</form>
</body>
</html>
"""

def formAddToInventory():
    return """
<!DOCTYPE HTML>
<html>
<head>
<title>Add To Inventory Form</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>Add Liquor to the Inventory Database</h1><br/>
<form action='recv3'>
<input type='hidden' name='formType' value='addLiquor'>
Enter liquor manufacturer: <input type='text' name='liquorMfg' size'30'><br />
Enter liquor name: <input type='text' name='liquorName' size'30'><br />
Enter liquor amount: <input type='text' name='liquorAmount' size'30'><br/>
<input type='submit'>
</form>
</body>
</html>
    """

def formAddLiquorType():
    return """

<!DOCTYPE HTML>
<html>
<head>
<title>Add Liquor Type Form</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>Add a Liquor Type to the Database</h1><br/>
<form action='recv2'>
<input type='hidden' name='formType' value='addLiquorType'>
Enter liquor manufacturer: <input type='text' name='liquorMfg' size'30'><br />
Enter liquor name: <input type='text' name='liquorName' size'30'><br />
Enter liquor type: <input type='text' name='liquorType' size'30'><br />
<input type='submit'>
</form>
</body>
</html>
"""

def formAddRecipe():
    return """
<!DOCTYPE HTML>
<html>
<head>
<title>Add Recipe Form</title>
<style type='text/css'>
h1 {text-decoration:underline; text-align:center; color:red;}
body { font-size:14px; }
</style>
</head>
<body>
<h1>Add a Recipe</h1><br/>
<form action='recv4' name='formType' value='addRecipe'>
Enter recipe name: <input type='text' name='recipeName' size'30'><br />
Enter ingredients*: <input type='text' name='ingredients' size'100'><br />
*Add recipe ingredients in the following format: ingredient, amount, ingredient, amount, etc.<br/>
(e.g. "unflavored vodka,6 oz,vermouth,1.5 oz" )<br/><br/>
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
