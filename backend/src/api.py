import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():

    drinks = Drink.query.all()

    drinks_list = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(payload):

    drinks = Drink.query.all()
    drinks_detailed_list = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_detailed_list
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_drink(payload):

    new_request = request.get_json()

    if new_request is None:
        abort(400)

    new_title = new_request.get('title', None)
    new_recipe = new_request.get('recipe', None)

    if all(v is not None for v in [new_title, new_recipe]):
        try:
            new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
            print('new drink created')
            new_drink.insert()
            print('new drink in the database')

            print(new_drink.long())

            return jsonify({
                'success': True,
                'drinks': [new_drink.long()]
            })

        except Exception as e:
            print(e)
            abort(422)

    else:
        abort(400)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def patch_drink(payload, id):

    drink_to_patch = Drink.query.filter_by(id=id).one_or_none()

    if drink_to_patch is None:
        abort(404)

    updated_info = request.get_json()

    new_title = updated_info.get('title', None)
    new_recipe = updated_info.get('recipe', None)

    if new_title:
        drink_to_patch.title = new_title

    if new_recipe:
        drink_to_patch.recipe = json.dumps(new_recipe)

    try:
        drink_to_patch.update()
    except Exception as e:
        print(e)
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink_to_patch.long()]
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):

    try:
        drink_to_delete = Drink.query.filter_by(id=id).one_or_none()
    except Exception as e:
        print(e)
        abort(400)

    if drink_to_delete is None:
        abort(404)

    try:
        drink_to_delete.delete()
    except Exception as e:
        print(e)
        abort(400)

    return jsonify({
        'success': True,
        'delete': id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


@app.errorhandler(401)
def unauthorized_access(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized access'
    }), 401


@app.errorhandler(403)
def forbiden_access(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'forbiden access'
    }), 403


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handler_for_autherror(error):
    print('Handling a AuthError')
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
