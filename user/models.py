from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class Mbti(models.Model):
	mbti_choices = [
		('entw', 'ENTW'),
	]

	mbti = models.CharField(max_length=10, choices=mbti_choices)
	description = models.TextField()

	def __str__(self):
		return self.mbti


class UserManager(BaseUserManager):
	use_in_migrations = True

	def create_user(self, kakao_id, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)

		if not kakao_id:
			raise ValueError('잘못된 형식의 요청입니다.')

		user = self.model(
			kakao_id=kakao_id,
			**extra_fields,
		)
		user.set_unusable_password()
		user.save()
		return user

	def create_superuser(self, kakao_id, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if not kakao_id:
			raise ValueError('잘못된 형식의 요청입니다.')

		user = self.model(
			kakao_id=kakao_id,
			**extra_fields,
		)
		user.set_unusable_password()
		user.save()
		return user


class User(AbstractBaseUser, PermissionsMixin):
	level_choices = [
		(2, '황금 접시'),
		(3, '은접시'),
		(4, '유리접시'),
		(5, '종이접시'),
	]

	kakao_id = models.TextField()
	nickname = models.CharField(max_length=30, unique=True, null=True)
	profile_img = models.URLField(null=True)
	mbti = models.ForeignKey(Mbti, on_delete=models.SET_NULL, null=True)
	level = models.PositiveIntegerField(choices=level_choices, null=True)
	select_count = models.PositiveIntegerField(default=0)
	refresh_token = models.TextField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	USERNAME_FIELD = 'id'
	last_login = None
	REQUIRED_FIELDS = ['kakao_id']

	objects = UserManager()

	def __str__(self):
		return str(self.id)

	class Meta:
		managed = True
