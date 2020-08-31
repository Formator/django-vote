import json
from rest_framework import serializers
from .models import VoteModel


class VoteBaseSerializer(serializers.ModelSerializer):
    user_voted = serializers.SerializerMethodField()

    class Meta:
        model = VoteModel
        abstract = True

    def get_user_voted(self, obj):
        user_id = self.context['request'].user.pk
        instance = getattr(obj.votes, 'get')(user_id)
        if instance:
            if instance.action == 0:
                return 'UP'
            else:
                return 'DOWN'
        return instance

    def create(self, validated_data):
        user_id = self.context['request'].user.pk
        obj = self.Meta.model.objects.create(**validated_data)
        _, instance = obj.votes.up(user_id)
        return instance