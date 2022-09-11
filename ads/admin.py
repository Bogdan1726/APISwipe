from django.contrib import admin
from .models import (
    Announcement, Advertising, GalleryAnnouncement, Complaint, Apartment
)

# Register your models here.

admin.site.register(Announcement)
admin.site.register(Advertising)
admin.site.register(GalleryAnnouncement)
admin.site.register(Complaint)
admin.site.register(Apartment)
