from django.urls import path
from posts import views

app_name = 'posts'

urlpatterns = [
    path('like/', views.LikeAPIView.as_view(), name='like'),
    path('', views.PostsListView.as_view(), name='posts_list'),
    path('create/', views.CreatePostView.as_view(), name='post_create'),
    path('<id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<id>/edit/', views.EditPostView.as_view(), name='post_edit'),
    path('<id>/delete/', views.DeletetPostView.as_view(), name='post_delete'),
    path('<id>/comments/create/', views.CreateCommentView.as_view(), name='create_comment'),
    path('<id>/comments/<commentid>/delete/', views.DeletetCommentView.as_view(), name='delete_comment'),
    path('<id>/comments/<commentid>/', views.DetailCommentView.as_view(), name='detail_comment'),# тут будут ответы на него
    path('<id>/comments/<commentid>/edit/', views.EditCommentView.as_view(), name='edit_comment'),
    path('<id>/comments/<commentid>/answers/create/', views.CreateAnswerView.as_view(), name='answer_create'),
    path('<id>/comments/<commentid>/answers/<answerid>/delete/', views.DeleteAnswerView.as_view(), name='answer_delete'),
    path('<id>/comments/<commentid>/answers/<answerid>/edit/', views.EditAnswerView.as_view(), name='answer_delete'),
]
