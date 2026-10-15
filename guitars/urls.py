from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("guitars/<int:pk>/", views.guitar_detail, name="guitar_detail"),
    path("configurator/", views.configurator, name="configurator"),
    path("cart/", views.cart, name="cart"),
    path("cart/<int:pk>/update/", views.cart_update, name="cart_update"),
    path("cart/<int:pk>/remove/", views.cart_remove, name="cart_remove"),
    path("cart/checkout/", views.cart_checkout, name="cart_checkout"),
    path("about/", views.about, name="about"),
    path("feedback/", views.feedback, name="feedback"),
    path("dss/recommend/", views.dss_recommend, name="dss_recommend"),
    path("auth/login/", views.auth_login, name="auth_login"),
    path("auth/register/", views.auth_register, name="auth_register"),
    path("auth/logout/", views.auth_logout, name="auth_logout"),
]
