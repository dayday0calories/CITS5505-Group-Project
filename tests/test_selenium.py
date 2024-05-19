import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

class SeleniumTestCase(unittest.TestCase):
    """Selenium tests for the application."""

    def setUp(self):
        """Set up the test driver and application URL."""
        self.driver = webdriver.Chrome() 
        self.base_url = "http://localhost:5000"  

    def tearDown(self):
        """Quit the driver after each test."""
        self.driver.quit()

    def test_register(self):
        """Test user registration."""
        driver = self.driver
        driver.get(self.base_url + "/auth/register")

        # Find the registration form elements
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        email = driver.find_element(By.NAME, "email")
        submit = driver.find_element(By.NAME, "submit")

        # Fill in the form
        username.send_keys("seleniumuser")
        password.send_keys("testpass")
        email.send_keys("selenium@example.com")
        submit.click()

        # Wait for redirect and check if registration was successful
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Login"))
        )
        self.assertIn("Please log in", driver.page_source)

    def test_login(self):
        """Test user login."""
        driver = self.driver
        driver.get(self.base_url + "/auth/login")

        # Find the login form elements
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        submit = driver.find_element(By.NAME, "submit")

        # Fill in the form
        username.send_keys("seleniumuser")
        password.send_keys("testpass")
        submit.click()

        # Wait for redirect and check if login was successful
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )
        self.assertIn("Logout", driver.page_source)

    def test_post_creation(self):
        """Test post creation."""
        driver = self.driver
        self.test_login()  # Log in first

        driver.get(self.base_url + "/pr/new_post")

        # Find the new post form elements
        title = driver.find_element(By.NAME, "title")
        content = driver.find_element(By.NAME, "content")
        submit = driver.find_element(By.NAME, "submit")

        # Fill in the form
        title.send_keys("Selenium Test Post")
        content.send_keys("This is a test post created by Selenium.")
        submit.click()

        # Wait for redirect and check if post was created
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Selenium Test Post"))
        )
        self.assertIn("Selenium Test Post", driver.page_source)

    def test_reply_creation(self):
        """Test reply creation."""
        driver = self.driver
        self.test_login()  # Log in first

        # Assume there's a post to reply to
        driver.get(self.base_url + "/pr/view_post")

        # Find the reply form elements
        content = driver.find_element(By.NAME, "content")
        submit = driver.find_element(By.NAME, "submit")

        # Fill in the form
        content.send_keys("This is a test reply created by Selenium.")
        submit.click()

        # Wait for the reply to appear
        time.sleep(3)  # Add a delay to wait for the page to update (adjust as necessary)

        # Check if reply was created
        self.assertIn("This is a test reply created by Selenium.", driver.page_source)

    def test_notifications_view(self):
        """Test viewing notifications."""
        driver = self.driver
        self.test_login()  # Log in first

        driver.get(self.base_url + "/notifications/")

        # Check if notifications are visible
        self.assertIn("Notifications", driver.page_source)

if __name__ == '__main__':
    unittest.main()
