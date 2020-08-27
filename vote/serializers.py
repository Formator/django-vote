import json
from rest_framework import serializers


class VoteBaseSerializer(serializers.ModelSerializer):
    user_voted = serializers.SerializerMethodField()

    class Meta:
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
