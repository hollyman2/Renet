from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Like, Post, Comment, ReplyComment


@receiver(post_save, sender=Like)
def update_likes_count_on_add(sender, instance, created, **kwargs):
    if created:
        if instance.post:
            instance.post.count_of_likes = instance.post.get_post_likes.count()
            instance.post.save()
        elif instance.comment:
            instance.comment.count_of_likes = instance.comment.get_comment_likes.count()
            instance.comment.save()
        elif instance.reply_comment:
            instance.reply_comment.count_of_likes = instance.reply_comment.get_reply_comment_likes.count()
            instance.reply_comment.save()


@receiver(post_delete, sender=Like)
def update_likes_count_on_delete(sender, instance, **kwargs):
    if instance.post:
        instance.post.count_of_likes = instance.post.get_post_likes.count()
        instance.post.save()
    elif instance.comment:
        instance.comment.count_of_likes = instance.comment.get_comment_likes.count()
        instance.comment.save()
    elif instance.reply_comment:
        instance.reply_comment.count_of_likes = instance.reply_comment.get_reply_comment_likes.count()
        instance.reply_comment.save()
