from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('upload',views.upload,name='upload'),
    path('saved',views.saved,name='saved'),
    path('edit',views.edit,name='edit'),
    path('research',views.research,name='research'),
    path('save',views.save,name='save'),
    path('trash',views.trash,name='trash'),
    path('create',views.create,name='create')
]