from rest_framework import serializers


def resident_complex_validator(obj, user):
    if obj.user != user and user.is_staff is False:
        raise serializers.ValidationError('You do not have access to this residential complex')
    return obj

