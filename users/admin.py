from django.contrib import admin
from django.contrib.auth import get_user_model
from users.models import Subscription, Contact, Message, Filter, MessageFile, Notary

User = get_user_model()

# Register your models here.

admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(Contact)
admin.site.register(Message)
admin.site.register(MessageFile)
admin.site.register(Filter)
admin.site.register(Notary)
