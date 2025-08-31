import os
from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    # Try individual environment variables
    db_host = os.environ.get('DB_HOST')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME', 'postgres')
    db_port = os.environ.get('DB_PORT', '5432')
    
    if all([db_host, db_user, db_password]):
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=require"

if database_url:
    # Azure PostgreSQL URL format fix (if needed)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local development with SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_app.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    users_count = User.query.count()
    return render_template_string('''
    <h1>Hello, Azure! Flask App with PostgreSQL</h1>
    <p>Total users in database: {{ count }}</p>
    <h2>Add a User:</h2>
    <form method="POST" action="/add_user">
        <input type="text" name="name" placeholder="Name" required><br><br>
        <input type="email" name="email" placeholder="Email" required><br><br>
        <button type="submit">Add User</button>
    </form>
    <h2>All Users:</h2>
    <ul>
    {% for user in users %}
        <li>{{ user.name }} ({{ user.email }}) - {{ user.created_at }}</li>
    {% endfor %}
    </ul>
    ''', count=users_count, users=User.query.all())

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    
    if name and email:
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return f"User with email {email} already exists!"
        
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return f"User {name} added successfully!"
    
    return "Name and email are required!"

@app.route('/api/users')
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

if __name__ == "__main__":
    # Use PORT environment variable provided by Azure, fallback to 8000 for local development
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
