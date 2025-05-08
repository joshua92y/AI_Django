# bookstore/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    price = models.IntegerField()
    pubdate = models.DateField()
    description = models.TextField()
    image = models.CharField(max_length=255)  # 이미지 파일명만 저장 (예: 'images/book1.jpg')

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cart = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username}의 프로필"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '주문완료'),
        ('cancelled', '취소됨'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # ✅ 추가

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
    
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # ✅ 추가
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i}점") for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'reviewer', 'order')  # ✅ 한 주문당 하나만 허용

    def __str__(self):
        return f"{self.book.title} / {self.reviewer.username} / 주문#{self.order.id}"