# store/models.py
from django.db import models
from dataclasses import dataclass
from datetime import date

@dataclass
class Product:
    number: int
    name: str
    price: int
    manufacturer: str
    made_date: date
# Create your models here.
