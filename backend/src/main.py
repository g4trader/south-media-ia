import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.campaign import Campaign, Strategy, DeviceBreakdown
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp

app = Flask(__name__, static_folder='../static')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes with specific origins
CORS(app, 
     origins=[
         'https://south-media-ia.vercel.app',
         'https://south-media-ia-git-main-south-medias-projects.vercel.app',
         'https://south-media-ia-south-medias-projects.vercel.app',
         'http://localhost:3000',
         'http://localhost:8000'
     ],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
