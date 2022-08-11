from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Subscription, Contact

User = get_user_model()
# Register your models here.

admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(Contact)

