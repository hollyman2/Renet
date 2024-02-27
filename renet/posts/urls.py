from django.urls import path
from posts import views

app_name = 'posts'

urlpatterns = [
    path('like/', views.LikeAPIView.as_view(), name='like'),
    path('', views.PostsListView.as_view(), name='posts_list'),
    path('create/', views.CreatePostView.as_view(), name='post_create'),
    path('<id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<id>/report/', views.ReportPostView.as_view(), name='post_report'),
    path('<id>/comments/create/', views.CreateCommentView.as_view(), name='create_comment'),
    path('<id>/comments/<commentid>/', views.DetailCommentView.as_view(), name='detail_comment'),# тут будут ответы на него
    path('<id>/comments/<commentid>/report/', views.ReportCommentView.as_view(), name='comment_report'),# тут будут ответы на него
    path('<id>/comments/<commentid>/answers/create/', views.CreateAnswerView.as_view(), name='answer_create'),
    path('<id>/comments/<commentid>/answers/<answerid>/', views.DetailAnswerView.as_view(), name='answer_detail'),
    path('<id>/comments/<commentid>/answers/<answerid>/report/', views.ReportAnswerView.as_view(), name='answer_report'),

]
