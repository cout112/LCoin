  

from django.contrib import admin
from django.urls import path, include
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.authenticated, name='authenticated'),
    path('signup', views.signup, name='signup'),
    path('login_authenticate', views.login_authenticate, name='login_authenticate'),
    path('logout_user', views.logout_user, name='logout_user'),
	path('change_node', views.change_node, name='change_node'),
	path('check_transaction', views.check_transaction, name='check_transaction'),
	path('send_transaction', views.send_transaction, name='send_transaction'),
	path('mine_request', views.mine_request, name='mine_request'),
	path('new_account', views.new_account, name='new_account'),

]