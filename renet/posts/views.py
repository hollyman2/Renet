from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from posts.models import Like, Comment, Post, ReplyComment

User = get_user_model()


class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        user = request.user

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



