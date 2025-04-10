from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Profile

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name'] 



class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price', 'category','image','stock']
    list_filter = ['category', 'price']
    search_fields = ['name', 'description']
    



class CartAdmin(admin.ModelAdmin):
    list_display=['user','created_at']
    readonly_fields=['created_at']
    ordering = ['-created_at']


class CartItemAdmin(admin.ModelAdmin):
    list_display=['cart','product','quantity']
    list_filter = ['product']
    search_fields = ['product__name']




class OrderAdmin(admin.ModelAdmin):
    list_display=['user','total','created_at','status','payment_status','payment_method']
    list_filter = ['status', 'payment_status', 'payment_method']
    readonly_fields = ['created_at']
    


class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','price']
    search_fields = ['order__id', 'product__name']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','bio','pic','location','phone']



admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
admin.site.register(Profile,ProfileAdmin)