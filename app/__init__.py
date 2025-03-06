from flask import Flask
from app.jwt import JwtManager
from app.routes.about_routes import about_bp
from app.routes.transaction_routes import transaction_bp
from app.routes.transfer_routes import transfer_bp
from app.routes.payee_routes import payee_bp
from app.routes.category_routes import category_bp
from app.routes.account_routes import account_bp
from app.routes.user_routes import user_bp
from app.routes.budget_routes import budget_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(payee_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(about_bp)
    return app
