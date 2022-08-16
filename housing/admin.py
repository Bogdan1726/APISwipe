from django.contrib import admin
from .models import (
    ResidentialComplex, RegistrationAndPayment, ResidentialComplexBenefits,
    ResidentialComplexNews, GalleryResidentialComplex, Document, Apartment
)

# Register your models here.


admin.site.register(ResidentialComplex)
admin.site.register(RegistrationAndPayment)
admin.site.register(ResidentialComplexBenefits)
admin.site.register(ResidentialComplexNews)
admin.site.register(GalleryResidentialComplex)
admin.site.register(Document)
admin.site.register(Apartment)
