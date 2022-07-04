from django.db import models
from user.models import User, Mbti


class DateTime(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Post(DateTime):
	time_choices = [
		('brek', '아침'),
		('lun', '점심'),
		('din', '저녁'),
		('night', '밤'),
	]
	drink_choices = [
		(0, '안 마셔요'),
		(1, '한 잔만!'),
		(2, '마실래요'),
	]
	member_choices = [
		(1, '혼자'),
		(2, '둘이서'),
		(3, '3~4명'),
		(4, '5인 이상'),
	]

	user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
	location = models.TextField()
	time = models.CharField(max_length=10, choices=time_choices)
	drink = models.PositiveIntegerField(choices=drink_choices)
	member_count = models.PositiveIntegerField(choices=member_choices)
	comment_count = models.PositiveIntegerField(default=0)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.id


class Place(models.Model):
	place_id = models.TextField()
	place_name = models.TextField()
	category_name = models.TextField()
	phone = models.TextField()
	road_address_name = models.TextField()
	region = models.TextField()
	place_x = models.TextField()
	place_y = models.TextField()
	place_url = models.TextField()

	def __str__(self):
		return self.place_name


class Comment(DateTime):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
	place = models.ForeignKey(Place, on_delete=models.CASCADE)
	place_img = models.URLField(blank=True)
	visit_flag = models.BooleanField(default=False)
	description = models.TextField(blank=True)
	select_flag = models.BooleanField(default=False)

	def __str__(self):
		return self.id


class Scrap(DateTime):
	user = models.ForeignKey(User, related_name='scraps', on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
