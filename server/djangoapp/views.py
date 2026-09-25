from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import logging
import json
import os

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
    try:
        data = json.loads(request.body)

        username = data["userName"]
        password = data["password"]

        user = authenticate(
            username=username,
            password=password
        )

        response_data = {
            "userName": username
        }

        if user is not None:
            login(request, user)

            response_data = {
                "userName": username,
                "status": "Authenticated"
            }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            "status": "Error",
            "message": str(e)
        })


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
# HELPER - LOAD DEALERS FROM JSON
# ---------------------------------------------------

def load_dealers_from_json():
    file_path = os.path.join(
        settings.BASE_DIR,
        "database",
        "data",
        "dealerships.json"
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    return data.get("dealerships", [])


# ---------------------------------------------------
# HELPER - LOAD REVIEWS FROM JSON
# ---------------------------------------------------

def load_reviews_from_json():
    file_path = os.path.join(
        settings.BASE_DIR,
        "database",
        "data",
        "reviews.json"
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    return data.get("reviews", [])


# ---------------------------------------------------
# GET ALL DEALERS / DEALERS BY STATE
# ---------------------------------------------------

def get_dealerships(request, state="All"):

    dealerships = None

    # Try Node/MongoDB first
    try:
        if state == "All":
            dealerships = get_request(
                "/fetchDealers"
            )
        else:
            dealerships = get_request(
                "/fetchDealers/" + state
            )

    except Exception as e:
        logger.warning(
            "Node dealer API unavailable: %s",
            e
        )

        dealerships = None

    # Fall back to JSON
    if dealerships is None:
        try:
            dealerships = load_dealers_from_json()

            if state != "All":
                dealerships = [
                    dealer
                    for dealer in dealerships
                    if (
                        dealer.get(
                            "state",
                            ""
                        ).lower()
                        == state.lower()
                        or
                        dealer.get(
                            "st",
                            ""
                        ).lower()
                        == state.lower()
                    )
                ]

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "dealers": [],
                "message": str(e)
            })

    return JsonResponse({
        "status": 200,
        "dealers": dealerships
    })


# ---------------------------------------------------
# GET ONE DEALER
# ---------------------------------------------------

def get_dealer_details(
    request,
    dealer_id
):

    dealer = None

    # Try Node/MongoDB first
    try:
        dealer = get_request(
            f"/fetchDealer/{dealer_id}"
        )

    except Exception as e:
        logger.warning(
            "Node dealer API unavailable: %s",
            e
        )

        dealer = None

    # Fall back to JSON
    if not dealer:
        try:
            dealerships = load_dealers_from_json()

            dealer = [
                item
                for item in dealerships
                if int(
                    item.get(
                        "id",
                        0
                    )
                ) == int(dealer_id)
            ]

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "dealer": [],
                "message": str(e)
            })

    if isinstance(
        dealer,
        dict
    ):
        dealer = [dealer]

    return JsonResponse({
        "status": 200,
        "dealer": dealer
    })


# ---------------------------------------------------
# GET REVIEWS FOR ONE DEALER
# ---------------------------------------------------

def get_dealer_reviews(
    request,
    dealer_id
):

    reviews = None

    # Try Node/MongoDB first
    try:
        reviews = get_request(
            f"/fetchReviews/dealer/{dealer_id}"
        )

    except Exception as e:
        logger.warning(
            "Node review API unavailable: %s",
            e
        )

        reviews = None

    # Fall back to JSON
    if reviews is None:
        try:
            all_reviews = load_reviews_from_json()

            reviews = [
                review
                for review in all_reviews
                if int(
                    review.get(
                        "dealership",
                        0
                    )
                ) == int(dealer_id)
            ]

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "reviews": [],
                "message": str(e)
            })

    return JsonResponse({
        "status": 200,
        "reviews": reviews
    })


# ---------------------------------------------------
# ADD A NEW REVIEW
# ---------------------------------------------------

@csrf_exempt
def add_review(request):

    if request.method == "POST":

        try:
            data = json.loads(
                request.body
            )

            print(
                "REVIEW DATA RECEIVED:",
                data
            )

            review_text = data.get(
                "review",
                ""
            )

            # Analyze sentiment
            try:
                sentiment_result = (
                    analyze_review_sentiments(
                        review_text
                    )
                )

                if sentiment_result is not None:
                    data["sentiment"] = (
                        sentiment_result.get(
                            "sentiment",
                            "neutral"
                        )
                    )
                else:
                    data["sentiment"] = "neutral"

            except Exception:
                data["sentiment"] = "neutral"

            # Try storing using Node/MongoDB
            try:
                response = post_review(
                    data
                )

                if response is not None:
                    return JsonResponse({
                        "status": 200,
                        "review": response
                    })

            except Exception as e:
                logger.warning(
                    "Node review API unavailable: %s",
                    e
                )

            # If Node/MongoDB is unavailable,
            # return the submitted review so the
            # deployed application can display it.
            return JsonResponse({
                "status": 200,
                "review": data
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