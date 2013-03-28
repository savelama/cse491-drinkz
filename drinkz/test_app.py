import drinkz.db
import drinkz.app
import urllib

def test_index():
	environ = {}
	environ['PATH_INFO'] = '/recipes'

	d = {}
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h

	app_obj = drinkz.app.SimpleApp()
	
	try:
		app_obj.load_db('bin/drinkz_db')
	except IOError:
		print "ERROR! The specified db file does not exist, no data was loaded. Moving on..."
		return

	results = app_obj(environ, my_start_response)

	text = "".join(results)
	status, headers = d['status'], d['headers']

	assert text.find('vomit inducing martini') != -1, text
	assert text.find('scotch on the rocks') != -1, text
	assert text.find('vodka martini') != -1, text
	assert text.find('whiskey bath') != -1, text

	assert ('Content-type', 'text/html') in headers
	assert status == '200 OK'