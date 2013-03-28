import drinkz.recipes

"""
Database functionality for drinkz information.
"""

from cPickle import dump, load

# private singleton variables at module level
_bottle_types_db = set()
_inventory_db = dict()
_recipes_db = dict()

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db, _recipes_db
    _bottle_types_db = set()
    _inventory_db = dict()
    _recipes_db = dict()

def save_db(filename):
    fp = open(filename, 'wb')

    tosave = (_bottle_types_db, _inventory_db)
    dump(tosave, fp)

    fp.close()

def load_db(filename):
    global _bottle_types_db, _inventory_db
    fp = open(filename, 'rb')

    loaded = load(fp)
    (_bottle_types_db, _inventory_db) = loaded

    fp.close()

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass

class DuplicateRecipeName(Exception):
    pass

def add_bottle_type(mfg, liquor, typ):
    "Add the given bottle type into the drinkz database."
    _bottle_types_db.add((mfg, liquor, typ))

def _check_bottle_type_exists(mfg, liquor):
    for (m, l, _) in _bottle_types_db:
        if mfg == m and liquor == l:
            return True

    return False

def add_to_inventory(mfg, liquor, amount):
    "Add the given liquor/amount to inventory."
    amt_to_add = 0

    if not _check_bottle_type_exists(mfg, liquor):
        err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
        raise LiquorMissing(err)

    amt = convert_to_ml(amount)
    amt_to_add += amt

    if (mfg, liquor) in _inventory_db:
        currentAmt = _inventory_db[(mfg, liquor)]
        new_total_amt = currentAmt + amt_to_add

    else:
        new_total_amt = amt_to_add

    # just add it to the inventory database as a tuple, for now.
    _inventory_db[(mfg, liquor)] = new_total_amt

def check_inventory(mfg, liquor):
    for (m, l) in _inventory_db:
        if mfg == m and liquor == l:
            return True
        
    return False

def get_inventory_by_liquor_type(liquor_type, amount):
    liquor_in_stock = []
    for (m, l, t) in _bottle_types_db:
        if t == liquor_type:
            a = get_liquor_amount(m, l)

            liquor_in_stock.append((m, l, t, amount - a))

    return liquor_in_stock

def _check_liquor_type_exists(typ):
    for (_, _, t) in _bottle_types_db:
        if typ == t:
            return True

    return False

def get_liquor_amount(mfg, liquor):
    "Retrieve the total amount of any given liquor currently in inventory."
    if (mfg, liquor) in _inventory_db:
        return _inventory_db[(mfg, liquor)]

def get_liquor_inventory():
    "Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
    for (m, l) in _inventory_db:
        yield m, l

def get_bottle_types():
    "Retrieve all bottle types in our database, in tuple form (mfg, liquor, type)"
    for (m, l, t) in _bottle_types_db:
        yield m, l, t

def add_recipe(r):
    "Add a recipe to our database. If the recipe already exists, raise an exception"
    if (r._name not in _recipes_db):
        _recipes_db[r._name] = r

    else:
        err = "Duplicated recipe name: '%s'" % (r._name)
        raise DuplicateRecipeName(err)

def get_all_recipes():
    "Return all recipes currently in our database"
    for k, r in _recipes_db.iteritems():
        yield r

def get_recipe(name):
    "Get a single recipe from our database by name"
    if (name in _recipes_db):
        return _recipes_db[name]

def convert_to_ml(amount):
    try:
        (amt, unit) = amount.split()
        amt = float(amt)
        unit = unit.lower()
    except ValueError:
        print "ERROR: ValueError has occurred! Moving on..."
    except:
        print "ERROR! Moving on..."
        pass

    if unit == 'ml':
        amt = float(amt)

    elif unit == 'oz':
        amt = float(amt) * 29.5735

    elif unit == 'gallon':
        amt = float(amt) * 3785.41

    elif unit == 'liter':
        amt = float(amt) * 1000

    else:
        print "Unit not recognized! Moving on..."
        assert 0, amount

    return amt
