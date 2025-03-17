from django.contrib import admin
from django.urls import path
from hospitalapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('adminlogin/', views.admin_login_view, name='adminlogin'),
    path('', views.register, name='register'),
    path('innerpage/', views.inner, name='inner'),
    path('appointment/', views.Appoint, name='appointment'),
    path('show/', views.show, name='show'),
    path('edit/<int:id>/', views.edit_appointment, name='edit'),
    path('delete/<int:id>/', views.delete),
    path('pay/', views.pay, name='pay'),


    path('stk/', views.stk, name='stk'),
    path('token/', views.token, name='token'),
    path('transactions/', views.transactions_list, name='transactions'),

]
