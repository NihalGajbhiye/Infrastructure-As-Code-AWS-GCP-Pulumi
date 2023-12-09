from flask import Flask, request, abort
from config import Config
from app.extension import db
from flask_migrate import Migrate
from app.extension import logger, statsd
from sqlalchemy import text
from uuid import uuid4
from app.helper_func import create_response
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from app.models import User, Assignment
from datetime import datetime
from app.helper_func import (
    is_valid_email, 
    is_valid_password, 
    load_users_from_csv,
    validate_datetime_format, 
    create_response)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logger.info('Flask app "MyFlaskApp starting up.')
    logger.info("Using config: %s", config_class)


    db.init_app(app)

    Migrate(app, db)

    with app.app_context():
        db.create_all()
        load_users_from_csv()
        logger.info("Connected to database successfully.")
    logger.info("Flask app ready to serve requests .")

    # API Implementation
    def basic_auth_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.authorization

            if not auth or not auth.username or not auth.password:
                abort(401, description = "Basic Auth Credentials missing!!!!!")
            
            if not is_valid_email(auth.username):
                abort(401, description = "Invalid Email!!")
            
            if not is_valid_password(auth.password):
                abort(401, description = "Invalid Email!!")

            try:
                user = User.query.filter_by(email = auth.username).first()
            except SQLAlchemyError:
                abort(503, description="Connection database not successful!!")
            
            if not user or not user.verify_password(auth.password):
                abort(401, description= "Invalid email or password!!")

            return fn(*args, **kwargs)
        return wrapper
    
    # Health check API
    @app.route("/healthz", methods=["GET"])
    def health_check():
        if request.data or request.args:
            abort(400, description="Request body must be empty")
        try:
            db.session.execute(text("SELECT * FROM user;"))
            return create_response(200)
        except SQLAlchemyError:
            abort(503, description="Database connection error")
    
    def get_user_id_from_basic_auth():
        auth = request.authorization
        if not auth:
            return None
    
        user = User.query.filter_by(email=auth.username).first()
        if not user or not user.verify_password(auth.password):
            return None
        return user.id
    
    def get_email_from_basic_auth():
        auth = request.authorization

        if not auth:
            return None
        return auth.username
    
    # Get All Assignment
    @app.route("/v1/assignments", methods=["GET"])
    @basic_auth_required
    def get_assignments():
        statsd.incr(".assignments.get")
        assignments = Assignment.query.all()
        logger.info("Assignments retrieved successfully!!")
        return create_response(
            200, [assignment.serialize() for assignment in assignments]
        )
    
    # Get Specific Assignment 
    @app.route("/v1/assignments/<string:ass_id>", methods=["GET"])
    @basic_auth_required
    def get_assignment(ass_id):
        statsd.incr(".assignments.get")
        assignment = Assignment.query.get_or_404(ass_id)
        logger.info("Assignment retrieved successfully")
        return create_response(200, assignment.serialize())

    # Assignment Create
    @app.route("/v1/assignments", methods=["POST"])
    @basic_auth_required
    def create_assignment():
        statsd.incr(".assignments.create")
        data = request.get_json()
        if not data:
            abort(400, description = "Request body must be present")
        name = data.get("name")
        points = data.get("points")
        number_of_attempts = data.get("number_of_attempts")
        deadline = data.get("deadline")

        if not all([name, points, number_of_attempts, deadline]):
            abort(400, description = "Missing required fields")

        if not (1 <= points <= 100):
            abort(400, description = "Points must between 1 and 100")

        if not (1 <= number_of_attempts <= 100):
            abort(400, description = "No of attempts must between 1 and 100")

        try:
            valid_flag, processed_deadline = validate_datetime_format(deadline)
        
            if not valid_flag:
                abort(400, description = "Invalid Deadline format")
            
        except ValueError:
            abort(400, description = "Invalid Deadline format")
        
        current_user_id = get_user_id_from_basic_auth()
        assignment = Assignment(
            id = str(uuid4()),
            name = name,
            points = points,
            number_of_attempts = number_of_attempts,
            deadline = processed_deadline,
            created_by = current_user_id
        )

        assignment.assignment_updated = datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        db.session.add(assignment)
        db.session.commit()
        logger.info("Assignment created successfully")
        return create_response(201, assignment.serialize())

    # update Assignment
    @app.route("/v1/assignments/<string:ass_id>", methods= ['PUT'])
    @basic_auth_required
    def update_assignment(ass_id):
        statsd.incr(".assignments.update")
        assignment = Assignment.query.get_or_404(ass_id)
        user_id = get_user_id_from_basic_auth()

        if assignment.created_by != user_id:
            abort(403, description = "You don't have the permission to update the assignment")
        
        data = request.get_json()

        neccessary_args = ["name", "points", "number_of_attempts", "deadline"]
        for arg in neccessary_args:
            if not data.get(arg) or data[arg] == "":
                abort(400, description = "Missing required Fields")

        
        assignment.name = data["name"]
        assignment.points = data["points"]
        assignment.number_of_attempts = data["number_of_attempts"]
        assignment.deadline = data["deadline"]

        try:
            valid_flag, processed_deadline = validate_datetime_format(data["deadline"])
            if not valid_flag:
                abort(400, description = "Invalid Date Format")
                assignment.deadline = processed_deadline
        except ValueError:
            abort(400, description = "Invalid Date Format")

        assignment.assignment_updated = datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        db.session.commit()
        logger.info("Assignment Updated Successfully")

        return create_response(204)
    
    # Delete Assignment

    @app.route("/v1/assignments/<string:ass_id>", methods = ['DELETE'])
    @basic_auth_required
    def delete_assignment(ass_id):
        statsd.incr(".assignments.delete")
        if request.data or request.args:
            abort(400, description = "Request body must be empty")
        assignment = Assignment.query.get_or_404(ass_id)
        user_id = get_user_id_from_basic_auth()

        if assignment.created_by != user_id:
            abort(403, description="Forbidden: you do not have permission to delete assignment")
        
        db.session.delete(assignment)
        db.session.commit()

        logger.info("Assignment Deleted Successfully")
        return create_response(204)

    return app