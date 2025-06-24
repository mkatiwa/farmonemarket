from django.http import Http404
from django.shortcuts import render

def test_404(request):
    """Test view to trigger 404 error"""
    raise Http404("This is a test 404 error")

def test_500(request):
    """Test view to trigger 500 error"""
    raise Exception("This is a test 500 error")