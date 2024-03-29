from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class Mbti(models.Model):
    MBTI_CHOICES = (
        ('CIMJ', 'CIMJ'),
        ('CIMR', 'CIMR'),
        ('NIMJ', 'NIMJ'),
        ('CITJ', 'CITJ'),
        ('NIMR', 'NIMR'),
        ('CITR', 'CITR'),
        ('NITJ', 'NITJ'),
        ('COMJ', 'COMJ'),
        ('NITR', 'NITR'),
        ('NOMJ', 'NOMJ'),
        ('COMR', 'COMR'),
        ('NOMR', 'NOMR'),
        ('COTJ', 'COTJ'),
        ('NOTJ', 'NOTJ'),
        ('COTR', 'COTR'),
        ('NOTR', 'NOTR'),
    )

    mbti = models.CharField(choices=MBTI_CHOICES, max_length=10)
    type = models.CharField(max_length=10)
    description = models.TextField()

    def __str__(self):
        return self.mbti


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, kakao_id, **extra_fields):
        if not kakao_id:
            raise ValueError('잘못된 형식의 요청입니다.')

        user = self.model(
            kakao_id=kakao_id,
            **extra_fields,
        )
        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, kakao_id='None', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        user = self.model(
            kakao_id=kakao_id,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    kakao_id = models.TextField()
    nickname = models.CharField(max_length=30, unique=True, null=True)
    profile_img = models.TextField(null=True)
    mbti = models.ForeignKey(Mbti, on_delete=models.SET_NULL, null=True)
    level = models.PositiveIntegerField(default=5)
    select_count = models.PositiveIntegerField(default=0)
    refresh_token = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'nickname'
    last_login = None
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.id)

    class Meta:
        managed = True
