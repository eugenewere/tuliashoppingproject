"""clare_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static

from Tulia_admin import views
from Tulia_admin.views import GeneratePDF, GenerateProductPDF
from clare_project import settings
app_name='TuliaAdmin'
urlpatterns = [

    path('', views.home , name='home'),
    path('logout/', views.logout_view, name='logout'),

    path('products/', views.products , name='products'),
    path('addproducts/', views.addproducts , name='addproducts'),
    path('deleteproducts/<int:product_id>', views.deleteproducts , name='deleteproducts'),
    path('featured/product/change/status/', views.product_featured, name='product_featured'),

    path('category/', views.category , name='category'),
    path('addcategory/', views.addcategory , name='addcategory'),
    path('deletecategory/<int:category_id>', views.deletecategory, name='delete_category'),
    path('editcategory/<int:category_id>', views.editcategory, name='edit_category'),
    path('view_sub_category/<int:category_id>', views.view_sub_category, name='view_sub_category'),

    path('brand/', views.brand , name='brand'),
    path('add_brand/', views.add_brand, name='add_brand'),
    path('delete/brand/<int:brand_id>', views.brand_delete, name='delete_brand'),
    path('edit/brand/<int:brand_id>', views.brand_edit, name='brand_edit'),



    path('carousel/', views.carousel , name='carousel'),
    path('addcarousel/', views.addcarousel , name='addcarousel'),
    path('carousel/delete/<int:carousel_id>', views.carousel_delete, name='carousel-delete'),
    path('carousel/edit/<int:carousel_id>', views.carousel_edit, name='carousel-edit'),

    path('variants/', views.variants, name='variants'),
    path('addvariants/', views.addvariants, name='addvariants'),
    path('variants/delete/<int:variant_id>', views.variant_delete, name='variant_delete'),
    path('variants/edit/<int:variant_id>', views.variant_edit, name='variant_edit'),

   path('variantsOptions/add/', views.variants_options, name='variants-options'),
   path('variantsOptions/delete/<int:variant_option_id>', views.variants_options_delete, name='variants-options-delete'),
   path('variantsOptions/edit/<int:variant_option_id>', views.variants_options_edit, name='variants-options-edit'),

    path('viewregions/', views.view_regions, name='view-regions'),
    path('regions/edit/<int:region_id>', views.edit_regions, name='edit-regions'),
    path('regions/delete/<int:region_id>', views.delete_regions, name='delete-regions'),


    path('orders/', views.orders, name='orders'),
    path('buyerOrders/<str:reference_code>', views.buyerOrders, name='buyer_orders'),

    path('payments/', views.payments, name='payments'),
    path('editpayments/<int:Order_payment_id>', views.edit_payments, name='updated_payments'),

    path('orders/chart/', views.ListOrders, name='orders_chart'),

    path('allreports/', views.viewAllReports, name='view_all_reports'),
    path('pdf/orders/', GeneratePDF.as_view(), name='orders_generated_pdf'),
    path('productspdf/', GenerateProductPDF.as_view(), name='products_generated_pdf'),

]