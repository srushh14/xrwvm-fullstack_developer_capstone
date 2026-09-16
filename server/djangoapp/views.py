# Django imports
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import logging
import json


# Get an instance of a logger
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)

    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)

    data = {"userName": username}

    if user is not None:
        login(request, user)
        data = {
            "userName": username,
            "status": "Authenticated"
        }

    return JsonResponse(data)


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------
def logout_request(request):
    logout(request)

    return JsonResponse({
        "status": "Logged out"
    })


# ---------------------------------------------------------
# Registration
# Will be implemented in the registration task
# ---------------------------------------------------------
# @csrf_exempt
# def registration(request):
#     pass


# ---------------------------------------------------------
# Get Dealerships
# Will be implemented in the dealership API task
# ---------------------------------------------------------
# def get_dealerships(request):
#     pass


# ---------------------------------------------------------
# Get Dealer Reviews
# ---------------------------------------------------------
# def get_dealer_reviews(request, dealer_id):
#     pass


# ---------------------------------------------------------
# Get Dealer Details
# ---------------------------------------------------------
# def get_dealer_details(request, dealer_id):
#     pass


# ---------------------------------------------------------
# Add Review
# ---------------------------------------------------------
# def add_review(request):
#     pass