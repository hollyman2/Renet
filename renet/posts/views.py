from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from posts.models import Like, Comment, Post, ReplyComment
from rest_framework.views import APIView
from .models import Post, Comment, ReplyComment
from rest_framework.response import Response
from rest_framework import status
from . import serializers

User = get_user_model()

def get_user(request):
    auth_header = str(request.headers.get('Authorization'))
    if auth_header is None:
        return Response(
            {'error': 'Токен не валиден или пользователь не авторизован'},
        )
    
    try:
        decoded_data = AccessToken(
            auth_header
        )
        user_id = decoded_data['user_id']
        user = User.objects.get(id=user_id)

        return user
    
    except: 

        return None
        


class LikeAPIView(APIView):
    def post(self, request, *args, **kwargs):

        user = get_user(request)

        object_id = request.data.get('object_id')
        object_type = request.data.get('object_type')

        if object_type == 'post':
            obj = get_object_or_404(Post, id=object_id)
            like, created = Like.objects.get_or_create(user=user, post=obj)
        elif object_type == 'comment':
            obj = get_object_or_404(Comment, id=object_id)
            like, created = Like.objects.get_or_create(user=user, comment=obj)
        elif object_type == 'reply_comment':
            obj = get_object_or_404(ReplyComment, id=object_id)
            like, created = Like.objects.get_or_create(user=user, reply_comment=obj)
        else:
            return Response({'error': 'Invalid object type'}, status=status.HTTP_400_BAD_REQUEST)

        if not created:
            like.delete()
            return Response(
                {'message': 'Лайк был удален'},
                status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'message': 'Лайк был добавлен'},
            status=status.HTTP_201_CREATED
        )

class PostsListView(APIView):

    def get(self, request):
        post = get_list_or_404(Post)
        post_serializer = serializers.PostSerializer(post, many=True)
        return Response(
            {'post': post_serializer.data},
            status=status.HTTP_200_OK
        )



class PostDetailView(APIView):

    def get(self, request, id):

        post = get_object_or_404(Post, id=id)
        post_serializer = serializers.PostSerializer(post)
        comments = get_list_or_404(Comment, post=post)
        comment_serializer = serializers.CommentSerializer(comments, many=True)
        return Response(
            {'post': post_serializer.data,
            'comments': comment_serializer.data},
            status=status.HTTP_200_OK
        )


class EditPostView(APIView):

    def post(self, request, id):
        user = get_user(request=request)
        post = get_object_or_404(Post, id=id)
        serializer = serializers.PostSerializer(post)
        if user.id == serializer.data.get('author'):
            serializer = serializers.PostSerializer(
                serializer.edit(
                    data=request.data,
                    post=post
                )
            )
            return Response(
                {'post': serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'You are not the owner'}
            )


class CreatePostView(APIView):

    def post(self, request):

        user = get_user(request=request)
        serializer = serializers.PostSerializer()
        serializer = serializers.PostSerializer(
            serializer.create(
                request.data,
                user=user
            )
        )

        return Response(
            {'post': serializer.data},
            status=status.HTTP_201_CREATED
        )
        


class CreateCommentView(APIView):

    def post(self, request, id):
        user = get_user(request=request)
        post = get_object_or_404(Post, id=id)
        serializer = serializers.CommentSerializer()
        
    
        serializer = serializers.CommentSerializer(
            serializer.create(
                data=request.data,
                user=user,
                post=post
            )
        )

        return Response(
            {'comment': serializer.data},
            status=status.HTTP_201_CREATED
           )
        
        
class EditCommentView(APIView):

    def post(self, request, id, commentid):
        user = get_user(request=request)
        comment = get_object_or_404(Comment, id=commentid)
        serializer = serializers.CommentSerializer(comment)
        if user.id == serializer.data.get('author'):

            serializer = serializers.CommentSerializer(
                serializer.edit(
                    data=request.data,
                    comment=comment
                )
            )

            return Response(
                {'comment': serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'You are not the owner'}
            )


class DeletetPostView(APIView):

    def get(self, request, id):
        user = get_user(request=request)
        post = get_object_or_404(Post, id=id)
        post_serializer = serializers.PostSerializer(post)
        if user.id == post_serializer.data.get('author'):
            post.delete()
            return Response(
                {'message': 'The post has been deleted'},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {'error': 'You are not the owner'}
            )


class DeletetCommentView(APIView):

    def get(self, request, id, commentid):
        user = get_user(request=request)
        comment = get_object_or_404(Comment, id=commentid)
        comment_serializer = serializers.CommentSerializer(comment)
        if user.id == comment_serializer.data.get('author'):
            comment.delete()

            return Response(
                {'message': 'The comment has been deleted'},
                status=status.HTTP_200_OK,

            )
        else:

            return Response(
                {'error': 'You are not the owner'}
            )


class DetailCommentView(APIView):

    def get(self, request, id, commentid):

        comment = get_object_or_404(Comment, id=commentid)
        answers = get_list_or_404(ReplyComment, comment=comment)
        comment_serializer = serializers.CommentSerializer(comment)
        answers_serializer = serializers.AnswerSerializer(answers, many=True)
        return Response(
            {'comments': comment_serializer.data,
             'answers': answers_serializer.data},
            status=status.HTTP_200_OK,
        )


class CreateAnswerView(APIView):

    def post(self, request, id, commentid):
        user = get_user(request=request)
        post = get_object_or_404(Post, id=id)
        comment = get_object_or_404(Comment, id=commentid)
      
        serializer = serializers.AnswerSerializer()
        serializer = serializers.AnswerSerializer(
            serializer.create(
                data=request.data,
                user=user,
                comment=comment,
                post=post
            )
        )
        
        return Response(
            {
                'answer': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    

class DeleteAnswerView(APIView):

    def get(self, request, id, commentid, answerid):
        user = get_user(request=request)
        answer = get_object_or_404(ReplyComment, id=answerid)
        answer_serializer = serializers.AnswerSerializer(answer)
        if user.id == answer_serializer.data.get('author'):
            answer.delete()

            return Response(
                {'message': 'The answer has been deleted'},
                status = status.HTTP_200_OK
            )
        else:

            return Response(
                {'error': 'You are not the owner'}
            )


class EditAnswerView(APIView):

    def post(self, request, id, commentid, answerid):
        user = get_user(request=request)
        answer = get_object_or_404(ReplyComment, id=answerid)
        answer_serializer = serializers.AnswerSerializer(answer)
        if user.id == answer_serializer.data.get('author'):
            serializer = serializers.AnswerSerializer()
            serializer = serializers.AnswerSerializer(
                serializer.edit(
                    data=request.data,
                    answer=answer
                )
            )

            return Response(
                {'answer': serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'You are not the owner'}
            )


