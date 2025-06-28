from django.urls import path
from . import views
urlpatterns = [
    path('' ,  views.Front_page),
    path('Login_page/' , views.Login_page , name= 'Login_page'),
    path('registration/' , views.registration , name= 'registration'),
    path('rg_Front_page/' , views.rg_Front_page , name= 'rg_Front_page'),
    path('signaction/' , views.signaction , name= 'signaction'),
    path('loginaction/' , views.loginaction , name= 'loginaction'),
    path('login_error/' , views.login_error , name= 'login_error'),
    path('portfolio/' , views.portfolio , name= 'portfolio'),
    path('portfolio_analysis/' , views.portfolio_analysis , name= 'portfolio_analysis'),
    path('about/' , views.about , name= 'about'),
    path('conact/' , views.contact , name= 'contact'),
    ]