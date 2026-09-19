from .models import CarMake, CarModel


def initiate():
    # Clear existing data to avoid duplicates
    CarModel.objects.all().delete()
    CarMake.objects.all().delete()

    # Create car makes
    toyota = CarMake.objects.create(
        name="Toyota",
        description="Japanese automobile manufacturer"
    )

    ford = CarMake.objects.create(
        name="Ford",
        description="American automobile manufacturer"
    )

    honda = CarMake.objects.create(
        name="Honda",
        description="Japanese automobile manufacturer"
    )

    # Create car models
    CarModel.objects.create(
        car_make=toyota,
        name="Camry",
        type="Sedan",
        year=2022
    )

    CarModel.objects.create(
        car_make=toyota,
        name="RAV4",
        type="SUV",
        year=2023
    )

    CarModel.objects.create(
        car_make=ford,
        name="Mustang",
        type="Coupe",
        year=2022
    )

    CarModel.objects.create(
        car_make=ford,
        name="Explorer",
        type="SUV",
        year=2023
    )

    CarModel.objects.create(
        car_make=honda,
        name="Civic",
        type="Sedan",
        year=2022
    )

    CarModel.objects.create(
        car_make=honda,
        name="CR-V",
        type="SUV",
        year=2023
    )

    print("Car makes and models populated successfully.")