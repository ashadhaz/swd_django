"""swd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from tools import user, address, other_info, cgpa, bonafide, leave, mess, images
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from graphene_django.views import GraphQLView
from schema.schema import schema
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

# REST
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token


urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^admin/', admin.site.urls),


    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    url(r'^gql', csrf_exempt(GraphQLView.as_view(batch=True, schema=schema))),

#    url(r'^login/', auth_views.login, {'template_name': 'admin/login.html'}),
#    url(r'^logout/', auth_views.logout),

    #REST
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),


    url(r'^', include('main.urls')),
    url(r'^create-users/', user.index, name='user'),
    url(r'^create-address/', address.index, name='address'),
    url(r'^other_info/', other_info.index, name='other_info'),
    url(r'^cgpa/', cgpa.index, name='cgpa'),
    url(r'^create-bonafide/', bonafide.index, name='bonafide'),
    url(r'^create-leave/', leave.index, name='leave'),
    url(r'^create-mess/', mess.index, name='mess'),
    url(r'^images/', images.insert, name='images'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
