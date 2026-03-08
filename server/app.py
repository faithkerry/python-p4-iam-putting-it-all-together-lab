from flask import request, session
from flask_restful import Api, Resource

from config import app, db
from models import User, Recipe


api = Api(app)


# ---------------- SIGNUP ----------------

class Signup(Resource):

    def post(self):

        data = request.get_json()

        try:
            user = User(
                username=data["username"],
                image_url=data["image_url"],
                bio=data["bio"]
            )

            user.password_hash = data["password"]

            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            return user.to_dict(only=("id", "username", "image_url", "bio")), 201

        except Exception as e:
            return {"errors": [str(e)]}, 422


api.add_resource(Signup, "/signup")


# ---------------- CHECK SESSION ----------------

class CheckSession(Resource):

    def get(self):

        user_id = session.get("user_id")

        if user_id:
            user = User.query.get(user_id)
            return user.to_dict(only=("id", "username", "image_url", "bio")), 200

        return {"error": "Unauthorized"}, 401


api.add_resource(CheckSession, "/check_session")


# ---------------- LOGIN ----------------

class Login(Resource):

    def post(self):

        data = request.get_json()

        user = User.query.filter_by(username=data["username"]).first()

        if user and user.authenticate(data["password"]):

            session["user_id"] = user.id

            return user.to_dict(only=("id", "username", "image_url", "bio")), 200

        return {"error": "Unauthorized"}, 401


api.add_resource(Login, "/login")


# ---------------- LOGOUT ----------------

class Logout(Resource):

    def delete(self):

        if session.get("user_id"):

            session.pop("user_id")

            return "", 204

        return {"error": "Unauthorized"}, 401


api.add_resource(Logout, "/logout")


# ---------------- RECIPES ----------------

class RecipeIndex(Resource):

    def get(self):

        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()

        return [recipe.to_dict() for recipe in recipes], 200


    def post(self):

        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        try:

            recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=user_id
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201

        except Exception as e:
            return {"errors": [str(e)]}, 422


api.add_resource(RecipeIndex, "/recipes")


if __name__ == "__main__":
    app.run(port=5555, debug=True)