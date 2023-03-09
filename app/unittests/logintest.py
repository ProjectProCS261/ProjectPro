# import the necessary modules
import pytest
from app import login

# define the test cases
def test_login_successful(client):
    response = client.post('/login', data=dict(email='testuser@example.com', password='password'), follow_redirects=True)
    assert b'Welcome, testuser@example.com!' in response.data

def test_login_invalid_email(client):
    response = client.post('/login', data=dict(email='testuser', password='password'), follow_redirects=True)
    assert b'Invalid email address' in response.data

def test_login_incorrect_password(client):
    response = client.post('/login', data=dict(email='testuser@example.com', password='wrongpassword'))


