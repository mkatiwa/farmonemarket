#!/usr/bin/env python3
"""
Debug script to test POST requests to login and register endpoints
"""

import requests
import sys

def test_login_post():
    """Test POST request to login endpoint"""
    url = "http://127.0.0.1:8000/accounts/login/"
    
    # First get the page to obtain CSRF token
    session = requests.Session()
    
    try:
        # Get login page
        response = session.get(url)
        print(f"GET {url}: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to get login page: {response.text}")
            return
        
        # Extract CSRF token
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break
        
        if not csrf_token:
            print("Could not find CSRF token")
            return
        
        print(f"Found CSRF token: {csrf_token[:10]}...")
        
        # Test POST request
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = session.post(url, data=data)
        print(f"POST {url}: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            if 'Invalid email or password' in response.text:
                print("✓ POST request successful - got expected login error")
            else:
                print("✓ POST request successful - form processed")
        else:
            print(f"✗ POST request failed: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed - is Django server running?")
        print("Run: python manage.py runserver")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_register_post():
    """Test POST request to register endpoint"""
    url = "http://127.0.0.1:8000/accounts/register/"
    
    session = requests.Session()
    
    try:
        # Get register page
        response = session.get(url)
        print(f"GET {url}: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to get register page: {response.text}")
            return
        
        # Extract CSRF token
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break
        
        if not csrf_token:
            print("Could not find CSRF token")
            return
        
        print(f"Found CSRF token: {csrf_token[:10]}...")
        
        # Test POST request
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'email': 'newuser@example.com',
            'password': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'buyer',
            'phone': '1234567890',
            'address': 'Test Address'
        }
        
        response = session.post(url, data=data)
        print(f"POST {url}: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200 or response.status_code == 302:
            print("✓ POST request successful")
        else:
            print(f"✗ POST request failed: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed - is Django server running?")
        print("Run: python manage.py runserver")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("Testing POST requests to Django endpoints...")
    print("=" * 50)
    
    print("\n1. Testing Login POST:")
    test_login_post()
    
    print("\n2. Testing Register POST:")
    test_register_post()
    
    print("\n" + "=" * 50)
    print("Debug complete!")