from django.contrib import admin
from django.utils import timezone
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Wishlist, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_featured', 'is_new_arrival', 'is_bestseller']
    list_filter = ['category', 'is_featured', 'is_new_arrival', 'is_bestseller']
    list_editable = ['price', 'stock', 'is_featured', 'is_new_arrival', 'is_bestseller']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'size']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'first_name', 'last_name', 'email',
        'total_amount', 'status', 'delivered_at', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['order_number', 'email', 'first_name', 'last_name']
    inlines = [OrderItemInline]

    # ✅ Only truly auto fields go here — NOT delivered_at
    readonly_fields = ['order_number', 'created_at', 'updated_at']

    actions = ['mark_as_delivered', 'mark_as_shipped', 'mark_as_confirmed']

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'status', 'payment_method', 'notes')
        }),
        ('Customer Details', {
            'fields': (
                ('first_name', 'last_name'),
                'email', 'phone',
            )
        }),
        ('Shipping Address', {
            'fields': (
                'address',
                ('city', 'state'),
                ('pincode', 'country'),
            )
        }),
        ('Financials', {
            'fields': ('total_amount',)
        }),
        ('Delivery & Return Window', {
            'description': 'Set "Delivered at" to activate the 7-day return window for the customer.',
            'fields': ('delivered_at',),  # ✅ Editable — not in readonly_fields
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.action(description='✅ Mark selected orders as Delivered (sets delivered date now)')
    def mark_as_delivered(self, request, queryset):
        now = timezone.now()
        updated = queryset.exclude(status='delivered').update(status='delivered', delivered_at=now)
        self.message_user(request, f'{updated} order(s) marked as Delivered. Return window starts now.')

    @admin.action(description='🚚 Mark selected orders as Shipped')
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} order(s) marked as Shipped.')

    @admin.action(description='✔ Mark selected orders as Confirmed')
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} order(s) marked as Confirmed.')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'created_at']
    list_filter = ['rating']


admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(CartItem)

