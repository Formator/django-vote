from rest_framework import generics, mixins, status
from rest_framework.decorators import action
from rest_framework.views import Response

from vote.signals import post_voted


class CreateChangeDeleteVoteAPIView(mixins.CreateModelMixin,
                                    mixins.DestroyModelMixin,
                                    generics.GenericAPIView):
    """
    Concrete view for creating, changing and deleting Vote of an user for a model instance.
    """

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user_id = request.user.pk

        action_type = request.data.get('action', 'up')
        voted, instance = getattr(obj.votes, action_type)(user_id)
        if voted:
            post_voted.send(
                sender=self.queryset.model,
                obj=obj,
                user_id=user_id,
                action=action_type)

        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        user_id = request.user.pk

        deleted, instance = obj.votes.delete(user_id)
        if deleted:
            post_voted.send(
                sender=self.queryset.model,
                obj=obj,
                user_id=user_id,
                action='delete')

        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers)
        # return self.destroy(request, *args, **kwargs)


class VoteMixin:

    def get_instance(self, pk):
        return self.queryset.get(pk=pk)

    @action(detail=True, methods=('post', 'delete'))
    def vote(self, request, pk):
        obj = self.get_instance(pk)
        user_id = request.user.pk
        if request.method.lower() == 'post':
            action_type = request.data.get('action', 'up')
            voted, instance = getattr(obj.votes, action_type)(user_id)
            if voted:
                post_voted.send(
                    sender=self.queryset.model,
                    obj=obj,
                    user_id=user_id,
                    action=action_type)
            else:
                return Response(data={}, status=409)
        else:
            deleted = obj.votes.delete(user_id)
            if deleted:
                post_voted.send(
                    sender=self.queryset.model,
                    obj=obj,
                    user_id=user_id,
                    action='delete')
        return Response({})
