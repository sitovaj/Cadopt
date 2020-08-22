import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Cat, Curator
from auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route("/")
    def hello():
        return "Hello World!"

    @app.route("/cats")
    def get_cat_list():
        selection = Cat.query.order_by('id').all()
        if len(selection) == 0:
            return jsonify({
                'success': False,
                'message': 'No cats for now'
            })
        formatted_cats = [cat.serialize_cat() for cat in selection]

        return jsonify({
            'success': True,
            'cats': formatted_cats
        }), 200

    @app.route("/cats/<id>")
    def get_cat_id(id):
        body = request.get_json()  # get request information sent within URL
        selection = Cat.query.filter(Cat.id == id).one_or_none()
        if selection is None:
            return jsonify({
                'success': False,
                'message': 'Id not found'
            }), 400
        return jsonify({
            'success': True,
            'cats': selection.serialize_cat()
        }), 200

    @app.route("/cats", methods=['POST'])
    @requires_auth('post:cats')
    def new_cat(payload):
        body = request.get_json()
        if body is None:
            abort(404)
        new_name = body.get('name', None)
        new_gender = body.get('gender', None)
        new_birthday = body.get('birthday', None)
        new_color = body.get('color', None)
        new_city = body.get('city', None)
        new_image = body.get('image', None)
        new_status = body.get('status', None)
        new_curator = body.get('curator_id', None)

        try:
            cat = Cat(name=new_name, gender=new_gender, birthday=new_birthday,
                      color=new_color, city=new_city, image=new_image, status=new_status, curator_id=new_curator)
            cat.insert()
            return jsonify({
                'success': True,
                'cat': cat.serialize_cat()
            })
        except Exception:
            abort(422)

    @app.route('/cats/<id>', methods=['PATCH'])
    @requires_auth('patch:cats')
    def patch_cats(payload, id):
        body = request.get_json()  # get request information sent within URL
        try:
            cat = Cat.query.filter(Cat.id == id).one_or_none()
            if not cat:
                abort(404)
            if 'status' in body:
                cat.status = body.get('status')
            if 'gender' in body:
                cat.gender = body.get('gender')            
            if 'city' in body:
                cat.city = body.get('city')
            cat.update()

            return jsonify({
                'success': True,
                'cat': cat.serialize_cat()
            })
        except Exception:
            abort(400)


    @app.route('/cats/<id>', methods=['DELETE'])
    @requires_auth('delete:cats')
    def delete_cats(payload, id):
        try:
            cat = Cat.query.filter(Cat.id == id).one_or_none()
            if not cat:
                abort(404)
            cat.delete()

            return jsonify({
                'success': True,
                'delete': id
            })
        except Exception:
            abort(400)

    @app.route("/curators")
    def get_curator_list():
        selection = Curator.query.order_by('id').all()
        if len(selection) == 0:
            return jsonify({
                'success': False,
                'message': 'No curator for now'
            })
        formatted_curators = [curator.serialize_curator()
                              for curator in selection]

        return jsonify({
            'success': True,
            'curators': formatted_curators
        }), 200

    @app.route("/curators/<id>")
    def get_curator_id(id):
        body = request.get_json()
        selection = Curator.query.filter(Curator.id == id).one_or_none()
        if selection is None:
            return jsonify({
                'success': False,
                'message': 'Id not found'
            })
        return jsonify({
            'success': True,
            'curators': selection.serialize_curator()
        }), 200

    @app.route('/curators', methods=['POST'])
    @requires_auth('post:curators')
    def new_curator(payload):
        body = request.get_json()
        if body is None:
            abort(404)
        new_name = body.get('name', None)
        new_legal_number = body.get('legal_number', None)
        new_phone = body.get('phone', None)
        new_email = body.get('email', None)
        new_facebook = body.get('facebook', None)
        try:
            curator = Curator(name=new_name, legal_number=new_legal_number,
                            phone=new_phone, email=new_email, facebook=new_facebook, cats=[])
            curator.insert()
            return jsonify({
                'success': True,
                'curators': curator.serialize_curator()
            })
        except Exception:
            abort(422)

    @app.route('/curators/<id>', methods=['DELETE'])
    @requires_auth('delete:curators')
    def delete_curators(payload, id):
        try:
            selection = Curator.query.filter(Curator.id == id).one_or_none()
            if not selection:
                abort(404)
            selection.delete()

            return jsonify({
                'success': True,
                'delete': id
            })
        except Exception:
            abort(400)

# Error handlers

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request, server couldnt understand it"
        }), 400

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity, check your request"
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "Unauthorized request"
        }), 401

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
