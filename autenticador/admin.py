from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.admin.sites import NotRegistered

# Re-registra usando o admin padrão do Django (já inclui is_staff em "Permissions")
try:
    admin.site.unregister(User)
except NotRegistered:
    pass
admin.site.register(User, DjangoUserAdmin)
