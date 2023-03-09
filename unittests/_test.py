# import the necessary modules
import pytest
from flask import Flask, url_for, session
from flask_login import login_user, LoginManager, logout_user, current_user, login_required, UserMixin
from app import app
from app.views import User

@pytest.fixture()
def client():
    return app.test_client()

# define the test cases
def test_registration_successful(client):
    with client:
        response = client.post('/register', data=dict(email='testuser@example.com', password='password', confirm_password='password'), follow_redirects=True)
        assert response.status_code == 200
        assert current_user.is_authenticated

def test_registration_existing_user(client):
    with client:
        response = client.post('/register', data=dict(email='testuser@example.com', password='password', confirm_password='password'), follow_redirects=True)
        assert response.status_code == 200
        assert not(current_user.is_authenticated)
    
def test_login_successful(client):
    with client:
        response = client.post('/login', data=dict(email='testuser@example.com', password='password'), follow_redirects=True)
        assert response.status_code == 200
        assert current_user.is_authenticated

def test_login_invalid_email(client):
    with client:
        response = client.post('/login', data=dict(email='testuser', password='password'), follow_redirects=True)
        assert response.status_code == 200
        assert not(current_user.is_authenticated)

def test_login_incorrect_password(client):
    with client:
        response = client.post('/login', data=dict(email='testuser@example.com', password='wrongpassword'), follow_redirects=True)
        assert response.status_code == 200
        assert not(current_user.is_authenticated)

def test_add_project(client):
    with client:
        client.post('/login', data=dict(email='testuser@example.com', password='password'), follow_redirects=False)
        response = client.post('/addProject', data=dict(project_name='test project', client_name='test client', methodology='Agile', budget='5000',owner='testuser@example.com',start_date='2023-01-01',deadline='2023-02-01'), follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == url_for("home")


 


