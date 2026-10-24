from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "guitars"

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.GuitarListView.as_view(), name="catalog"),
    path("guitars/<int:pk>/", views.GuitarDetailView.as_view(), name="guitar_detail"),
    path("guitars/<int:pk>/reviews/add/", views.ReviewCreateView.as_view(), name="review_create"),
    path("reviews/<int:pk>/edit/", views.ReviewUpdateView.as_view(), name="review_update"),
    path("reviews/<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
    path("staff/orders/", views.StaffOrdersListView.as_view(), name="staff_orders"),
    path("login/", auth_views.LoginView.as_view(template_name="guitars/login.html"), name="login"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("logout/", views.auth_logout, name="auth_logout"),
    path("configurator/", views.configurator, name="configurator"),
    path("cart/", views.cart, name="cart"),
    path("cart/<int:pk>/update/", views.cart_update, name="cart_update"),
    path("cart/<int:pk>/remove/", views.cart_remove, name="cart_remove"),
    path("cart/checkout/", views.cart_checkout, name="cart_checkout"),
    path("favorites/", views.favorites_list, name="favorites"),
    path("favorites/toggle/<int:pk>/", views.favorite_toggle, name="favorite_toggle"),
    path("about/", views.about, name="about"),
    path("feedback/", views.feedback, name="feedback"),
    path("dss/recommend/", views.dss_recommend, name="dss_recommend"),
]
