#! /user/bing/env python
import simplejson
import app
import db
import recipes
import cStringIO
import sys
import copy

def call_remote(method, params, id):

	d = dict(method=method, params=params, id=id)
	encoded = simplejson.dumps(d)

	lines = []

	for line in encoded:
		lines.append(line)

	newlines = copy.copy(lines)


	environ = {}
	environ['PATH_INFO'] = '/rpc'
	environ['REQUEST_METHOD'] = 'POST'
	environ['CONTENT_LENGTH'] = len(encoded)
	environ['wsgi.input'] = cStringIO.StringIO(''.join(newlines))

	d = {}
	def my_start_response(s, h, return_in=d):
		d['status'] = s
		d['headers'] = h

	simpleApp = app.SimpleApp()
	response = simpleApp(environ, my_start_response)

	results = simplejson.loads(response[0])

	return results

def test_rpc_ConvertToMilliters():

	results = call_remote(method='ConvertToMilliters', params=['1000 oz'], id=1)
	assert results['result'] == 29573.5, results['result']

def test_rpc_AddLiquorType():

	db._reset_db()
	call_remote(method='AddLiquorType', params=['Jack Daniels', 'Old No. 7', 'whiskey'], id=1)
	assert db._check_bottle_type_exists('Jack Daniels', 'Old No. 7')

def test_rpc_AddToInventory():

	db._reset_db()
	call_remote(method='AddLiquorType', params=['Jack Daniels', 'Old No. 7', 'whiskey'], id=1)
	call_remote(method='AddToInventory', params=['Jack Daniels', 'Old No. 7', '1000 ml'], id=1)

	assert db.check_inventory('Jack Daniels', 'Old No. 7')

def test_rpc_AddRecipe():
	
	db._reset_db()
	call_remote(method='AddRecipe', params=['rum and coke', 'rum,2 oz,coke,4 oz'], id=1)
	assert db.get_recipe('rum and coke')

def test_rpc_GetLiquorTypes():
	db._reset_db()
	call_remote(method='AddLiquorType', params=['Jack Daniels', 'Old No. 7', 'whiskey'], id=1)

	results = call_remote(method='GetLiquorTypes', params=[], id=1)
	assert results['result'] == [['Jack Daniels', 'Old No. 7', 'whiskey']]

def test_rpc_GetLiquorInventory():
	db._reset_db()
	call_remote(method='AddLiquorType', params=['Jack Daniels', 'Old No. 7', 'whiskey'], id=1)
	call_remote(method='AddToInventory', params=['Jack Daniels', 'Old No. 7', '1000 ml'], id=1)
	results = call_remote(method='GetLiquorInventory', params=[], id=1)

	assert results['result'] == [['Jack Daniels', 'Old No. 7']]

def test_rpc_GetRecipes():
	db._reset_db()
	call_remote(method='AddRecipe', params=['rum and coke', 'rum,2 oz,coke,4 oz'], id=1)
	results = call_remote(method='GetRecipes', params=[], id=1)

	assert results['result'] == ['rum and coke']