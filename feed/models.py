from django.db import models
from django.db.models.functions import Cast

from user.models import User, Mbti


class DateTime(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(DateTime):
    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    location = models.TextField()
    time = models.CharField(max_length=10)
    drink = models.PositiveIntegerField()
    member_count = models.PositiveIntegerField()
    comment_count = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True)

    def __str__(self):
        return str(self.id)


class Place(models.Model):
    place_id = models.TextField()
    place_name = models.TextField()
    category_name = models.TextField()
    phone = models.TextField(blank=True)
    road_address_name = models.TextField()
    region = models.TextField()
    place_x = models.TextField()
    place_y = models.TextField()
    place_url = models.TextField()

    class Meta:
        ordering = [
            Cast("place_id", output_field=models.IntegerField()),
        ]

    def __str__(self):
        return self.place_name


class Comment(DateTime):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    place_img = models.URLField(null=True)
    visit_flag = models.BooleanField(default=False)
    description = models.TextField(null=True)
    select_flag = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Scrap(DateTime):
    user = models.ForeignKey(User, related_name='scraps', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
