import uuid

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

Account = get_user_model()


class Post(models.Model):
    VIDEO_VALIDATOR = FileExtensionValidator(allowed_extensions=['mp4', ])

    id = models.UUIDField(
        'UUID',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    picture = models.ImageField(
        'Picture',
        upload_to='posts_pictures/%Y/%m/%d/',
        null=True,
        blank=True
    )
    video = models.FileField(
        'Video',
        upload_to='posts_videos/images/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[VIDEO_VALIDATOR, ]
    )
    description = models.TextField(
        'Description',
        max_length=500,
    )
    tags = TaggableManager()
    author = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='get_posts',
        verbose_name='Author'
    )
    date_created = models.DateTimeField(
        'Date created',
        auto_now_add=True
    )

    def get_absolute_url(self):
        return reverse(
            'profile_detail',
            args=[str(self.id)]
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='get_comments',
        verbose_name='Post'
    )
    author = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='get_user_comments',
        verbose_name='Author'
    )
    description = models.TextField(
        'Description',
        max_length=500,
    )

    def __str__(self):
        return self.description[:50]

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

class ReplyComment(Comment):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='get_reply_comment'
    )

    def __str__(self):
        return self.comment.description[:50]

    class Meta:
        verbose_name = 'Repy to comment'
        verbose_name_plural = 'Replies to comment'
