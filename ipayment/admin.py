from django.contrib import admin

from models import Confirmation

class ConfirmationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Confirmation, ConfirmationAdmin)

