from django.contrib import admin
from django.urls import path
from hospitalapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('', views.register, name='register'),
    path('innerpage/', views.inner, name='inner'),
    path('appointment/', views.Appoint, name='appointment'),
    path('show/', views.show, name='show'),
    path('edit/<int:id>/', views.edit_appointment, name='edit'),
    path('delete/<int:id>/', views.delete),
]
