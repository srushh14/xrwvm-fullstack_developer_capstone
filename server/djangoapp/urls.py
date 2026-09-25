from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'

urlpatterns = [

    # Login
    path(
        'login',
        views.login_user,
        name='login'
    ),

    # Register
    path(
        'register',
        views.register_user,
        name='register'
    ),

    # Logout
    path(
        'logout',
        views.logout_request,
        name='logout'
    ),

    # Car Makes and Models
    path(
        'get_cars',
        views.get_cars,
        name='get_cars'
    ),

    # All Dealers
    path(
        'get_dealers',
        views.get_dealerships,
        name='get_dealers'
    ),

    # Dealers filtered by State
    path(
        'get_dealers/<str:state>',
        views.get_dealerships,
        name='get_dealers_by_state'
    ),

    # Individual Dealer Details
    path(
        'dealer/<int:dealer_id>',
        views.get_dealer_details,
        name='dealer_details'
    ),

    # Reviews for Individual Dealer
    path(
        'reviews/dealer/<int:dealer_id>',
        views.get_dealer_reviews,
        name='dealer_reviews'
    ),

    # Add New Review
    path(
        'add_review',
        views.add_review,
        name='add_review'
    ),

] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)