import unittest
from flask import url_for
from app import create_app, db
from app.models.models import User, LoginHistory
from config import TestingConfig

class AuthRoutesTestCase(unittest.TestCase):
    """Test cases for authentication routes."""

    def setUp(self):
        """Set up test variables and initialize app context and database."""
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Remove session and drop all tables after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_success(self):
        """Test successful registration."""
        response = self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)

    def test_duplicate_username(self):
        """Test registration with a duplicate username."""
        # Register the first user
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })

        # Attempt to register the same username again
        response = self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test2@example.com'
        }, follow_redirects=True)
        
        self.assertIn(b'Username already exists.', response.data)

    def test_invalid_email(self):
        """Test registration with an invalid email format."""
        response = self.client.post(url_for('auth.register'), data={
            'username': 'testuser2',
            'password': 'testpass',
            'email': 'invalidemail'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email format', response.data)

    def test_successful_login(self):
        """Test successful login."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        response = self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(url_for("pr.view_post", _external=False), response.headers['Location'])  # Check for relative path

    def test_incorrect_password(self):
        """Test login with incorrect password."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        response = self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password.', response.data)

    def test_nonexistent_user(self):
        """Test login with a nonexistent user."""
        response = self.client.post(url_for('auth.login'), data={
            'username': 'nonuser',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password.', response.data)

    def test_successful_logout(self):
        """Test successful logout."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
        response = self.client.get(url_for('auth.logout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.headers['Location'])

    def test_login_recorded(self):
        """Test if login time and username are recorded."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
        login_history = LoginHistory.query.filter_by(username='testuser').first()
        self.assertIsNotNone(login_history)
        self.assertIsNone(login_history.logout_time)

    def test_logout_recorded(self):
        """Test if logout time is recorded."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.client.get(url_for('auth.logout'))
        login_history = LoginHistory.query.filter_by(username='testuser').first()
        self.assertIsNotNone(login_history.logout_time)

if __name__ == '__main__':
    unittest.main()
