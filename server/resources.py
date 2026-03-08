from flask import request, session, jsonify
from flask_restful import Resource
from models import db, User, Recipe

# -------------------------
# Signup
# -------------------------
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "Invalid username or password"}, 422

        user = User(username=username)
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        return {"id": user.id, "username": user.username}, 201

# -------------------------
# Login
# -------------------------
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return {"error": "Invalid username or password"}, 401

        session["user_id"] = user.id
        return {"id": user.id, "username": user.username}, 200

# -------------------------
# Logout
# -------------------------
class Logout(Resource):
    def delete(self):
        if "user_id" in session:
            session.pop("user_id")
            return {}, 204
        return {"error": "No active session"}, 401

# -------------------------
# CheckSession
# -------------------------
class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = User.query.get(user_id)
        return {"id": user.id, "username": user.username}, 200

# -------------------------
# RecipeIndex
# -------------------------
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.filter_by(user_id=user_id).all()
        data = [
            {
                "id": r.id,
                "title": r.title,
                "instructions": r.instructions,
                "minutes_to_complete": r.minutes_to_complete
            }
            for r in recipes
        ]
        return data, 200