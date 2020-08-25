from math import sqrt

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from vote.managers import VotableManager

UP = 0
DOWN = 1


class VoteManager(models.Manager):

    def filter(self, *args, **kwargs):
        if 'content_object' in kwargs:
            content_object = kwargs.pop('content_object')
            content_type = ContentType.objects.get_for_model(content_object)
            kwargs.update({
                'content_type': content_type,
                'object_id': content_object.pk
            })

        return super(VoteManager, self).filter(*args, **kwargs)


class Vote(models.Model):
    ACTION_FIELD = {UP: 'num_vote_up', DOWN: 'num_vote_down'}

    user_id = models.BigIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    action = models.PositiveSmallIntegerField(default=UP)
    create_at = models.DateTimeField(auto_now_add=True)

    objects = VoteManager()

    class Meta:
        unique_together = ('user_id', 'content_type', 'object_id', 'action')
        index_together = ('content_type', 'object_id')

    @classmethod
    def votes_for(cls, model, instance=None, action=UP):
        ct = ContentType.objects.get_for_model(model)
        kwargs = {"content_type": ct, "action": action}
        if instance is not None:
            kwargs["object_id"] = instance.pk

        return cls.objects.filter(**kwargs)


class VoteModel(models.Model):
    vote_score = models.IntegerField(default=0, db_index=True)
    num_vote_up = models.PositiveIntegerField(default=0, db_index=True)
    num_vote_down = models.PositiveIntegerField(default=0, db_index=True)
    votes = VotableManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.vote_score = self.calculate_vote_score
        super(VoteModel, self).save(*args, **kwargs)

    @property
    def calculate_vote_score(self):
        votes = self.num_vote_down + self.num_vote_up
        if votes == 0:
            return 0

        #confidence level
        z = 1.44  #1.44 = 85%, 1.96 = 95%
        p = float(self.num_vote_up) / votes

        left = p + 1 / (2 * votes) * z * z
        right = z * sqrt(p * (1 - p) / votes + z * z / (4 * votes * votes))
        under = 1 + 1 / votes * z * z

        return (left - right) / under

    @property
    def is_voted_up(self):
        try:
            return self._is_voted_up
        except AttributeError:
            return False

    @is_voted_up.setter
    def is_voted_up(self, value):
        self._is_voted_up = value

    @property
    def is_voted_down(self):
        try:
            return self._is_voted_down
        except AttributeError:
            return False

    @is_voted_down.setter
    def is_voted_down(self, value):
        self._is_voted_down = value
