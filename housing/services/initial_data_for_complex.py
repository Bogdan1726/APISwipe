from housing.models import ResidentialComplexBenefits, RegistrationAndPayment
from users.models import Contact


def create_data_for_residential_complex(instance):
    ResidentialComplexBenefits.objects.create(
        residential_complex=instance
    )
    RegistrationAndPayment.objects.create(
        formalization='Юстиция',
        payment_options='Ипотека',
        purpose='Жилое помещение',
        contract_sum='Неполная',
        residential_complex=instance
    )
    Contact.objects.create(
        residential_complex=instance,
        type='Отдел продаж'
    )
