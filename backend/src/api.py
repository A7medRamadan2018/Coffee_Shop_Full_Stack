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
 uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
 implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
     drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]
    if not all_drinks:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


'''
 implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drink_details(jwt):
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)

    drinks_formatted = [drink.long() for drink in drinks]
    return jsonify(
        {"success": True,
         "drinks": drinks_formatted}
    ), 200


'''
 implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200  and
        json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    data = request.get_json()
    title = data['title']
    recipe = json.dumps(data['recipe'])
    try:
        drink = Drink(title=title, recipe=recipe)
        if not drink:
            abort(404)
        drink.insert()
        return jsonify({
            'drinks': [drink.long()],
            'success': True
        })
    except IndexError:
        abort(400)


'''
 implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    data = request.get_json()
    title = data['title']
    drink.title = title
    drink.update()
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
 implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    drink.delete()
    return jsonify({
        'success': True,
        'delete': id
    })
# Error Handling


'''
 implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
 implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


'''
 implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def authentication_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unaothorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
