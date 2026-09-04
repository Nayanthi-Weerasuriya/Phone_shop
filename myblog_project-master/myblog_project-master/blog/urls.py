from django.urls import path
from . import views


urlpatterns = [
   path('',views.welcome , name='welcome' ),
   path('sit',views.sit , name='sit' ),
   path('academic/', views.academic , name='aca'),
   path('create/', views.create_post , name='create'),
   path('viewall/', views.view_all , name='viewall'),
   path('delete/<int:post_id>/', views.delete_post,name='delete_post'),
   path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
]