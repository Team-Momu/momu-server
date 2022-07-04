from django.db import models


class DateTime(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Mbti(models.Model):
	mbti_choices = [
		('entw', 'ENTW'),
	]

	mbti = models.CharField(max_length=10, choices=mbti_choices)
	description = models.TextField()

	def __str__(self):
		return self.mbti


class User(DateTime):
	level_choices = [
		(2, '황금 접시'),
		(3, '은접시'),
		(4, '유리접시'),
		(5, '종이접시'),
	]

	kakao_id = models.TextField(null=True, blank=True)
	nickname = models.CharField(max_length=30, unique=True)
	profile_img = models.URLField(null=True, blank=True)
	mbti = models.ForeignKey(Mbti, on_delete=models.CASCADE)
	level = models.PositiveIntegerField(choices=level_choices)
	select_count = models.PositiveIntegerField(default=0)
	refresh_token = models.TextField(null=True, blank=True)

	def __str__(self):
		return self.nickname
