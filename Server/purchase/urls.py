from django.urls import path
from . import views

urlpatterns = [
    path('lists/', views.get_purchase_lists, name='get_purchase_lists'),
    path('lists/create/', views.create_purchase_list, name='create_purchase_list'),
    path('lists/uncompleted/', views.get_uncompleted_lists, name='get_uncompleted_lists'),
    path('lists/<int:list_id>/', views.get_purchase_list_detail, name='get_purchase_list_detail'),
    path('lists/<int:list_id>/update/', views.update_purchase_list, name='update_purchase_list'),
    path('lists/<int:list_id>/items/add/', views.add_purchase_item, name='add_purchase_item'),
    path('items/<int:item_id>/mark-purchased/', views.mark_item_purchased, name='mark_item_purchased'),
    path('items/<int:item_id>/mark-partial/', views.mark_item_partial, name='mark_item_partial'),
    path('items/<int:item_id>/carry-over-next-day/', views.carry_over_next_day, name='carry_over_next_day'),
]
