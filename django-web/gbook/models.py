# gbook/models.py
from django.db import models
from django.contrib.auth.models import User

class GuestBookEntry(models.Model):
    title = models.CharField(max_length=200, verbose_name='제목')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자', default=1)
    message = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    views = models.PositiveIntegerField(default=0, verbose_name='조회수')

    def __str__(self):
        return f"{self.title} - {self.author.username}"

    class Meta:
        verbose_name = '방명록'
        verbose_name_plural = '방명록'

class GuestBookFile(models.Model):
    entry = models.ForeignKey(GuestBookEntry, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    class Meta:
        verbose_name = '첨부파일'
        verbose_name_plural = '첨부파일'
