from django.urls import path
from . import views
app_name = 'im'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('ru', views.homepage_rus, name='homepage_rus'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  
    path('403/', views.custom_403_view, name='403_forbidden'),

    path('sales/', views.sales, name='sales'),
    path('sales/ru', views.sales_rus, name='sales_rus'),
    path('sales_man/ru/<str:manufacturer>/', views.sales_man_rus, name='sales_man_rus'),
    path('sales_cat/ru/<str:category>/', views.sales_cat_rus, name='sales_cat_rus'),
    path('sales_subcat/ru/<str:subcategory>/', views.sales_subcat_rus, name='sales_subcat_rus'),
    path('sales_region/ru/<str:region>/', views.sales_region_rus, name='sales_region_rus'),
    path('sales_client/ru/<str:client_type>/', views.sales_client_rus, name='sales_client_rus'),
    path('sales_manager/ru/<str:manager>/', views.sales_manager_rus, name='sales_manager_rus'),
    path('products/', views.product_list, name='product_list'),
    path('product/search/', views.product_detail_search, name='product_detail_search'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/ru/<int:id>/', views.product_detail_rus, name='product_detail_rus'),
    path('simulate-demand/', views.simulate_demand, name='simulate_demand'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('calculate-statistics/',views.calculate_statistics_view, name='calculate_statistics'),
    path('calculate-statistics-form/', views.calculate_statistics_form, name='calculate_statistics_form'),
    path('place-order/', views.place_order_view, name='place_order'),
    path('stores/', views.store_list, name='store_list'),
]

