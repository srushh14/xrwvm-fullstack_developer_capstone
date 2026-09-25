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


# =========================================================
# LOGIN
# =========================================================

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


# =========================================================
# REGISTER
# =========================================================

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

            if User.objects.filter(
                username=username
            ).exists():

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


# =========================================================
# LOGOUT
# =========================================================

def logout_request(request):
    logout(request)

    return JsonResponse({
        "status": "Logged out"
    })


# =========================================================
# GET CAR MAKES AND MODELS
# =========================================================

def get_cars(request):

    car_makes = CarMake.objects.all()
    car_models = CarModel.objects.all()

    makes = []
    models = []

    # Try reading car data from Django database
    for make in car_makes:
        makes.append({
            "id": make.id,
            "name": make.name,
            "description": make.description
        })

    for model in car_models:
        models.append({
            "id": model.id,
            "name": model.name,
            "type": model.type,
            "year": model.year,
            "car_make": model.car_make.name
        })

    # -----------------------------------------------------
    # Render fallback
    # -----------------------------------------------------

    if len(makes) == 0:

        makes = [
            {
                "id": 1,
                "name": "Toyota",
                "description":
                    "Japanese automobile manufacturer"
            },
            {
                "id": 2,
                "name": "Ford",
                "description":
                    "American automobile manufacturer"
            },
            {
                "id": 3,
                "name": "Honda",
                "description":
                    "Japanese automobile manufacturer"
            }
        ]

    if len(models) == 0:

        models = [
            {
                "id": 1,
                "name": "Camry",
                "type": "Sedan",
                "year": 2022,
                "car_make": "Toyota"
            },
            {
                "id": 2,
                "name": "RAV4",
                "type": "SUV",
                "year": 2023,
                "car_make": "Toyota"
            },
            {
                "id": 3,
                "name": "Mustang",
                "type": "Coupe",
                "year": 2022,
                "car_make": "Ford"
            },
            {
                "id": 4,
                "name": "Explorer",
                "type": "SUV",
                "year": 2023,
                "car_make": "Ford"
            },
            {
                "id": 5,
                "name": "Civic",
                "type": "Sedan",
                "year": 2022,
                "car_make": "Honda"
            },
            {
                "id": 6,
                "name": "CR-V",
                "type": "SUV",
                "year": 2023,
                "car_make": "Honda"
            }
        ]

    return JsonResponse({
        "CarMakes": makes,
        "CarModels": models
    })


# =========================================================
# HELPER - DEALERS JSON FILE
# =========================================================

def get_dealers_file_path():

    return os.path.join(
        settings.BASE_DIR,
        "database",
        "data",
        "dealerships.json"
    )


# =========================================================
# HELPER - REVIEWS JSON FILE
# =========================================================

def get_reviews_file_path():

    return os.path.join(
        settings.BASE_DIR,
        "database",
        "data",
        "reviews.json"
    )


# =========================================================
# HELPER - LOAD DEALERS
# =========================================================

def load_dealers_from_json():

    file_path = get_dealers_file_path()

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data.get(
        "dealerships",
        []
    )


# =========================================================
# HELPER - LOAD REVIEWS
# =========================================================

def load_reviews_from_json():

    file_path = get_reviews_file_path()

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data.get(
        "reviews",
        []
    )


# =========================================================
# GET ALL DEALERS / DEALERS BY STATE
# =========================================================

def get_dealerships(
    request,
    state="All"
):

    dealerships = None

    # -----------------------------------------------------
    # Try Node/MongoDB first
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Render fallback
    # -----------------------------------------------------

    if dealerships is None:

        try:

            dealerships = (
                load_dealers_from_json()
            )

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


# =========================================================
# GET DEALER DETAILS
# =========================================================

def get_dealer_details(
    request,
    dealer_id
):

    dealer = None

    # -----------------------------------------------------
    # Try Node/MongoDB first
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Render fallback
    # -----------------------------------------------------

    if not dealer:

        try:

            dealerships = (
                load_dealers_from_json()
            )

            dealer = [
                item
                for item in dealerships

                if int(
                    item.get(
                        "id",
                        0
                    )
                )
                == int(dealer_id)
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


# =========================================================
# GET REVIEWS FOR DEALER
# =========================================================

def get_dealer_reviews(
    request,
    dealer_id
):

    reviews = None

    # -----------------------------------------------------
    # Try Node/MongoDB first
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Render fallback
    # -----------------------------------------------------

    if reviews is None:

        try:

            all_reviews = (
                load_reviews_from_json()
            )

            reviews = [
                review
                for review in all_reviews

                if int(
                    review.get(
                        "dealership",
                        0
                    )
                )
                == int(dealer_id)
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


# =========================================================
# ADD REVIEW
# =========================================================

@csrf_exempt
def add_review(request):

    if request.method != "POST":

        return JsonResponse({
            "status": 405,
            "message":
                "POST request required"
        })

    try:

        data = json.loads(
            request.body
        )

        review_text = data.get(
            "review",
            ""
        )

        # -------------------------------------------------
        # Sentiment Analysis
        # -------------------------------------------------

        try:

            sentiment_result = (
                analyze_review_sentiments(
                    review_text
                )
            )

            if sentiment_result:

                data["sentiment"] = (
                    sentiment_result.get(
                        "sentiment",
                        "neutral"
                    )
                )

            else:

                data["sentiment"] = (
                    "neutral"
                )

        except Exception:

            data["sentiment"] = (
                "neutral"
            )

        # -------------------------------------------------
        # Try Node/MongoDB first
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Render JSON fallback
        # -------------------------------------------------

        try:

            file_path = (
                get_reviews_file_path()
            )

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                review_file_data = (
                    json.load(file)
                )

            reviews = (
                review_file_data.get(
                    "reviews",
                    []
                )
            )

            # Generate next review ID

            max_id = 0

            for review in reviews:

                try:

                    review_id = int(
                        review.get(
                            "id",
                            0
                        )
                    )

                    if review_id > max_id:

                        max_id = review_id

                except Exception:

                    pass

            data["id"] = max_id + 1

            # Make sure dealership is integer

            if "dealership" in data:

                try:

                    data["dealership"] = int(
                        data["dealership"]
                    )

                except Exception:

                    pass

            reviews.append(
                data
            )

            review_file_data[
                "reviews"
            ] = reviews

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    review_file_data,
                    file,
                    indent=2
                )

            return JsonResponse({
                "status": 200,
                "review": data
            })

        except Exception as e:

            logger.error(
                "JSON review fallback failed: %s",
                e
            )

            return JsonResponse({
                "status": 500,
                "message": str(e)
            })

    except Exception as e:

        return JsonResponse({
            "status": 500,
            "message": str(e)
        })