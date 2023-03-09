# import the necessary modules
import pytest
from flask import Flask, session
from app import app

# define the test cases
def test_registration_successful(client):
    response = client.post('/register', data=dict(email='testuser@example.com', password='password', confirm_password='password'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Thank you for registering, testuser@example.com!' in response.data
    assert session['logged_in'] == True
    assert session['user_email'] == 'testuser@example.com'

def test_registration_existing_user(client):
    response = client.post('/register', data=dict(email='testuser@example.com', password='password', confirm_password='password'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Email already registered, please log in' in response.data
    assert session.get('logged_in') is None
    assert session.get('user_email') is None

def test_registration_invalid_email(client):
    response = client.post('/register', data=dict(email='testuser', password='password', confirm_password='password'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email address' in response.data
    assert session.get('logged_in') is None
    assert session.get('user_email') is None

def test_registration_password_mismatch(client):
    response = client.post('/register', data=dict(email='testuser@example.com', password='password', confirm_password='wrongpassword'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Passwords do not match' in response.data
    assert session.get('logged_in') is None
    assert session.get('user_email') is None

def test_registration_empty_fields(client):
    response = client.post('/register', data=dict(email='', password='', confirm_password=''), follow_redirects=True)
    assert response.status_code == 200
    assert b'Please fill out all fields' in response.data
    assert session.get('logged_in') is None
    assert session.get('user_email') is None

def test_registration_empty_password(client):
    response = client.post('/register', data=dict(email='testuser@example.com', password='', confirm_password=''), follow_redirects=True)
    assert response.status_code == 200
    assert b'Please enter a password' in response.data
    assert session.get('logged_in') is None
    assert session.get('user_email') is None

def test_registration_empty_email(client):
    response = client.post('/register', data=dict(email='', password='password', confirm_password=''), follow_redirects=True)
    assert response.status_code == 200
    assert b'Please enter an email address' in response.data
    assert session.get('logged_in') is None
    assert session.get('user_email') is None
