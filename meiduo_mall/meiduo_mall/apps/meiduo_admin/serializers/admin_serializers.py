from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from users.models import User


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'groups', 'user_permissions', 'mobile', 'email',
                  'password')
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        # groups = validated_data.pop('groups')
        # user_permissions = validated_data.pop('user_permissions')
        # instance = User.objects.create_superuser(**validated_data)
        # instance.groups.set(groups)
        # instance.user_permissions.set(user_permissions)
        # instance.save()
        # return instance

        validated_data['password'] = make_password(validated_data['password'])
        validated_data['is_staff'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)