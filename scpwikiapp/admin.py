from django.contrib import admin
from .models import PDFDocument
# Register your models here.

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title','file')