from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

from .models import CarMake, CarModel
from .restapis import (
    get_request,
    analyze_review_sentiments,
    post_review
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@csrf_exempt
def login_user(request):
    data = json.loads(request.body)

    username = data['userName']
    password = data['password']

    user = authenticate(
        username=username,
        password=password
    )

    data = {
        "userName": username
    }

    if user is not None:
        login(request, user)

        data = {
            "userName": username,
            "status": "Authenticated"
        }

    return JsonResponse(data)


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            username = data.get("userName")
            first_name = data.get("firstName")
            last_name = data.get("lastName")
            email = data.get("email")
            password = data.get("password")

            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    "status": "User already exists"
                })

            User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            return JsonResponse({
                "userName": username,
                "status": "Registered"
            })

        except Exception as e:
            return JsonResponse({
                "status": "Error",
                "message": str(e)
            })

    return JsonResponse({
        "status": "POST request required"
    })


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------

def logout_request(request):
    logout(request)

    return JsonResponse({
        "status": "Logged out"
    })


# ---------------------------------------------------
# GET CAR MAKES AND MODELS
# ---------------------------------------------------

def get_cars(request):
    car_makes = CarMake.objects.all()
    car_models = CarModel.objects.all()

    makes = []

    for make in car_makes:
        makes.append({
            "id": make.id,
            "name": make.name,
            "description": make.description
        })

    models = []

    for model in car_models:
        models.append({
            "id": model.id,
            "name": model.name,
            "type": model.type,
            "year": model.year,
            "car_make": model.car_make.name
        })

    return JsonResponse({
        "CarMakes": makes,
        "CarModels": models
    })


# ---------------------------------------------------
# GET ALL DEALERS / DEALERS BY STATE
# ---------------------------------------------------

def get_dealerships(request, state="All"):
    if state == "All":
        dealerships = get_request("/fetchDealers")
    else:
        dealerships = get_request(
            "/fetchDealers/" + state
        )

    if dealerships is not None:
        return JsonResponse({
            "status": 200,
            "dealers": dealerships
        })

    return JsonResponse({
        "status": 500,
        "dealers": []
    })


# ---------------------------------------------------
# GET ONE DEALER
# ---------------------------------------------------

def get_dealer_details(request, dealer_id):
    dealer = get_request(
        f"/fetchDealer/{dealer_id}"
    )

    if dealer is not None:

        # Dealer.jsx expects an array
        if isinstance(dealer, dict):
            dealer = [dealer]

        return JsonResponse({
            "status": 200,
            "dealer": dealer
        })

    return JsonResponse({
        "status": 500,
        "dealer": []
    })


# ---------------------------------------------------
# GET REVIEWS FOR ONE DEALER
# ---------------------------------------------------

def get_dealer_reviews(request, dealer_id):
    reviews = get_request(
        f"/fetchReviews/dealer/{dealer_id}"
    )

    if reviews is not None:
        return JsonResponse({
            "status": 200,
            "reviews": reviews
        })

    return JsonResponse({
        "status": 500,
        "reviews": []
    })


# ---------------------------------------------------
# ADD A NEW REVIEW
# ---------------------------------------------------

@csrf_exempt
def add_review(request):
    if request.method == "POST":

        try:
            data = json.loads(request.body)
            print("REVIEW DATA RECEIVED:", data)

            review_text = data.get(
                "review",
                ""
            )

            # Analyze the review sentiment
            sentiment_result = analyze_review_sentiments(
                review_text
            )

            if sentiment_result is not None:
                data["sentiment"] = sentiment_result.get(
                    "sentiment",
                    "neutral"
                )
            else:
                data["sentiment"] = "neutral"

            # Store the review in MongoDB through Node API
            response = post_review(data)

            if response is not None:
                return JsonResponse({
                    "status": 200,
                    "review": response
                })

            return JsonResponse({
                "status": 500,
                "message": "Could not add review"
            })

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            })

    return JsonResponse({
        "status": 405,
        "message": "POST request required"
    })