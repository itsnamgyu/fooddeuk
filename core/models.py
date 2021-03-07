from django.contrib.auth import get_user_model
from django.db import models
from django.templatetags.static import static

User = get_user_model()


class Photo(models.Model):
    votes = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def update(self):
        selections = self.vote_set.values("selection").annotate(models.Count("user")).all()
        votes = 0
        total = 0
        for s in selections:
            votes += s["user__count"]
            total += Vote.selection_to_integer(s["selection"]) * s["user__count"]
        self.votes = votes
        self.total = total
        self.average = total /votes
        self.save()

    @property
    def src(self):
        if self.id > 982:
            return ""
        else:
            return static("core/img/photos/grad{:03d}.jpg".format(self.id))

    @property
    def thumb_src(self):
        if self.id > 982:
            return ""
        else:
            return static("core/img/thumbnails/grad{:03d}.jpg".format(self.id))

    @property
    def name(self):
        return "서강대단체{}.jpg".format(self.id)


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)

    GOOD = 'GD'
    OKAY = 'OK'
    BAD = 'BD'
    selection_choices = [
        (GOOD, 'Great (5)'),
        (OKAY, 'Okay (3)'),
        (BAD, 'Bad (1)'),
    ]
    selection = models.CharField(max_length=2, choices=selection_choices)

    @classmethod
    def selection_to_integer(cls, selection):
        if selection == cls.GOOD:
            return 5
        elif selection == cls.OKAY:
            return 3
        elif selection == cls.BAD:
            return 1
        else:
            raise AssertionError()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "photo"], name="user_photo_unique")
        ]
