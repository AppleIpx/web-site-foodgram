from django.core.management.base import BaseCommand

from web_site import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("ingredients.csv", 'r', encoding="utf-8") as file:
            for line in file:
                element = line.split(",")
                models.Ingredient.objects.get_or_create(name=element[0], measurement_unit=element[1])
