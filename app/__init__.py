from flask import Flask
from flask import request, jsonify
from app.jwt import JwtManager
from http import HTTPStatus

def create_app():
    app = Flask(__name__)
    
    # Import routes
    from app.routes.transaction_routes import transaction_bp
    from app.routes.transfer_routes import transfer_bp
    from app.routes.payee_routes import payee_bp
    from app.routes.category_routes import category_bp
    from app.routes.account_routes import account_bp
    from app.routes.user_routes import user_bp
    from app.routes.budget_routes import budget_bp
    
    # Register routes
    app.register_blueprint(transaction_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(payee_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(budget_bp)
    return app

def handle_route_action(action):
    if not JwtManager.check_token_valid(request):
        return "", HTTPStatus.UNAUTHORIZED
    try:
        id_user = JwtManager.get_id_user_from_token(request)
        result = action(id_user, request.json if request.is_json else None)
        responseBody = "" if (result is None) else jsonify(result)
        return responseBody, HTTPStatus.OK
    except Exception as error:
        print(f"Exception in handle_route_action() : {error}")
        return "", HTTPStatus.BAD_REQUEST
