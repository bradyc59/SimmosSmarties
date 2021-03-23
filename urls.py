from django.urls import path
from . import views
from .forms import UserLoginForm
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.index, name="index"),  # /app
    path('registration/', views.register, name="register"),  # /app/registration
    path('products/', views.all_products),
    path('category/<str:category_name>', views.products_by_category),
    path('names/<str:names>', views.products_by_names),
    path('product/<int:product_id>', views.product_single, name="product_single"),
    path('addproduct/', views.addproduct),
    path('usersignup/', views.CaUserSignupView.as_view(), name="registered"),
    path('adminsignup/', views.AdminSignupView.as_view(), name="Admin register"),
    path('login/', views.Login.as_view(template_name="login.html", authentication_form=UserLoginForm), name='login'),
    path('logout/', views.logout_view, name="logout"),
    path('addtobasket/<int:product_id>', views.add_to_basket, name="Add to basket"),
    path('remove/<int:product_id>', views.remove_from_basket, name="remove"),
    path('basket/', views.basket, name="basket"),
    path('checkout/', views.checkout, name="checkout"),
    path('orders/', views.orders, name="orders"),
    path('thanks/', views.thanks, name="thanks"),
    path('editproduct/', views.editproduct, name="edit product"),
    path('delete/<int:product_id>', views.delete_product, name="delete product")

]
