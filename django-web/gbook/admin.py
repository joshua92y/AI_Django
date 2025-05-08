# gbook/admin.py

#관리자(admin) 페이지에 등록된 모델을 관리하기 위한 설정 파일입니다.
from django.contrib import admin
from .models import GuestBookEntry, GuestBookFile

class GuestBookFileInline(admin.TabularInline):
    model = GuestBookFile
    extra = 1

@admin.register(GuestBookEntry)
class GuestBookEntryAdmin(admin.ModelAdmin):
    inlines = [GuestBookFileInline]
    list_display = ('title', 'author', 'created_at', 'views')

@admin.register(GuestBookFile)
class GuestBookFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'entry', 'uploaded_at')