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
    image_url: str = None  # ✅ 이 줄 추가