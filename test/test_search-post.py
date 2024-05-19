import unittest
from app import create_app, db
from app.models import User, Post
from flask import url_for

class SearchPostTestCase(unittest.TestCase):

    # Set up the test environment before each test case
    def setUp(self):
        self.app = create_app('test_config')
        self.app.config.from_object('test_config')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    # Clean up the test environment after each test case
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # Test the search functionality by title
    def test_search_by_title(self):
        user = User(name='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        # Create two posts with different titles
        post1 = Post(title='First Post', content='This is the first post', user_id=user.id)
        post2 = Post(title='Second Post', content='This is the second post', user_id=user.id)
        db.session.add_all([post1, post2])
        db.session.commit()
        # Perform a search query by title
        response = self.client.get(url_for('pr.search'), query_string={'q': 'First', 'search_type': 'Titles'})

        # Verify the status code and check if the correct post is found
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'First Post', response.data)
        self.assertNotIn(b'Second Post', response.data)

    # Test the search functionality by content
    def test_search_by_content(self):
        user = User(name='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

        # Create two posts with different contents
        post1 = Post(title='First Post', content='This is the first post', user_id=user.id)
        post2 = Post(title='Second Post', content='This is the second post', user_id=user.id)
        db.session.add_all([post1, post2])
        db.session.commit()
        
        # Perform a search query by content
        response = self.client.get(url_for('pr.search'), query_string={'q': 'second', 'search_type': 'Descriptions'})
        # Verify the status code and check if the correct post is found
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Second Post', response.data)
        self.assertNotIn(b'First Post', response.data)

if __name__ == '__main__':
    unittest.main()
