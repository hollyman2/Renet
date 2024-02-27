from rest_framework.serializers import ModelSerializer
from .models import Post, Comment, ReplyComment, Report


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post

        fields = (
            'picture',
            'video',
            'description',
            'author',
            'tags',
            'id',
        )
     

    def edit(self, data, post):
        

        
        post.email=data.get('email')
        post.picture=data.get('picture')
        post.video=data.get('video')
        post.description=data.get('description')
        
        post.tags=data.get('tags')
        post.edited=True
        post.save()
        
        print(post)

        return post

    def create(self, data, user):
        print(user)

        post = Post.objects.create(
            author=user,
            picture=data.get('picture'),
            video=data.get('video'),
            description=data.get('description'),
            tags=data.get('tags'),
        )
        return post


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment

        fields = (
            'post',
            'edited',
            'description',
            'author',
            'id',
        )
    

    def edit(self, data, comment):

        
        comment.description=data.get('description'),
        comment.edited=True
        comment.save()
        

        return comment

    def create(self, data, user, post):

        comment = Comment.objects.create(
            post=post,
            author=user,
            description=data.get('description'),
        )
        
        return comment


class AnswerSerializer(ModelSerializer):
    class Meta:

        model = ReplyComment
        fields = (
            'comment',
            'description',
            'edited',
            'author',
            'id',
        )
        

    def create(self, user, data, post, comment):

        answer = ReplyComment.objects.create(
            post=post,
            comment=comment,
            author=user,
            description=data.get('description'),
        )
        return answer

    def edit(self, data, answer):

        
        answer.description=data.get('description'),
        answer.edited=True
        
        answer.save() 
        

        return  answer

class ReportSerializer(ModelSerializer):

    class Meta:
        model = Report
        fields = [
            'author',
            'recipient',
            'post',
            'comment',
            'answer',
            'reason',
            'created',
            'id'
        ]
    