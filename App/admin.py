from django.contrib import admin
from .models import PDFDocument
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


admin.site.unregister(User)

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file')

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username',)

admin.site.register(User, CustomUserAdmin)
