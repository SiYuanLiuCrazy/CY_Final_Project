"""
URL configuration for ppt_lable project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from myapp.views import create_folder_view, catalog_list_view, delete_catalog_view, create_subitem_view
urlpatterns = [
    path("admin/", admin.site.urls),
    path('create_folder/', create_folder_view, name='create_folder'),
    path('catalog_list/', catalog_list_view, name='catalog_list'),
    path('delete_catalog/<uuid:catalog_id>/', delete_catalog_view, name='delete_catalog'),
    path('create_subitem/', create_subitem_view, name='create_subitem'),
]
