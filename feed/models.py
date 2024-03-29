from django.db import models
from django.db.models.functions import Cast

from user.models import User, Mbti


class DateTime(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(DateTime):
    LOCATION_CHOICES = (
        ('신촌동', '신촌동'),
        ('창천동', '창천동'),
        ('연희동', '연희동'),
        ('대현동', '대현동'),
        ('대신동', '대신동'),
        ('연남동', '연남동'),
        ('서교동', '서교동'),
        ('동교동', '동교동'),
        ('합정동', '합정동'),
        ('망원동', '망원동'),
        ('상수동', '상수동'),
    )
    TIME_CHOICES = (
        ('아침', '아침'),
        ('점심', '점심'),
        ('저녁', '저녁'),
        ('밤', '밤'),
    )

    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    location = models.TextField(choices=LOCATION_CHOICES)
    time = models.CharField(choices=TIME_CHOICES, max_length=10)
    drink = models.PositiveIntegerField()
    member_count = models.PositiveIntegerField()
    comment_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    selected_flag = models.BooleanField(default=False)

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
    place_img = models.TextField(null=True)
    description = models.TextField(blank=True)
    select_flag = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Scrap(DateTime):
    user = models.ForeignKey(User, related_name='scraps', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
