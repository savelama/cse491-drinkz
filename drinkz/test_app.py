import drinkz.db
import drinkz.app
import urllib

def test_index():

	drinkz.db._reset_db()
	drinkz.db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
	drinkz.db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

	drinkz.db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
	drinkz.db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')

	drinkz.db.add_bottle_type('Gray Goose', 'vodka', 'unflavored vodka')
	drinkz.db.add_to_inventory('Gray Goose', 'vodka', '1 liter')

	drinkz.db.add_bottle_type('Rossi', 'extra dry vermouth', 'vermouth')
	drinkz.db.add_to_inventory('Rossi', 'extra dry vermouth', '24 oz')

	r1 = drinkz.recipes.Recipe('scotch on the rocks', [('blended scotch', '4 oz')])
	drinkz.db.add_recipe(r1)

	r2 = drinkz.recipes.Recipe('vodka martini', [('unflavored vodka', '6 oz'),
	                                            ('vermouth', '1.5 oz')])
	drinkz.db.add_recipe(r2)

	r3 = drinkz.recipes.Recipe('vomit inducing martini', [('orange juice',
	                                                      '6 oz'),
	                                                     ('vermouth',
	                                                      '1.5 oz')])
	drinkz.db.add_recipe(r3);

	r4 = drinkz.recipes.Recipe('whiskey bath', [('blended scotch', '5.5 liter')])
	drinkz.db.add_recipe(r4)

	environ = {}
	environ['PATH_INFO'] = '/recipes'

	d = {}
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h

	app_obj = drinkz.app.SimpleApp()
	results = app_obj(environ, my_start_response)

	text = "".join(results)
	status, headers = d['status'], d['headers']

	assert text.find('vomit inducing martini') != -1, text
	assert text.find('scotch on the rocks') != -1, text
	assert text.find('vodka martini') != -1, text
	assert text.find('whiskey bath') != -1, text

	assert ('Content-type', 'text/html') in headers
	assert status == '200 OK'