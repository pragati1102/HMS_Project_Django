from django.contrib import admin
from .models import Register,Room,Booking_room

# Register your models here.
@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("username","email","password")

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_num","room_type","room_price","room_rating","room_available")

@admin.register(Booking_room)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'room',
        'get_room_type',
        'check_in',
        'check_out',
        'payment_method',
        'total_amount',
    )

    def get_room_type(self, obj):
        return obj.room.room_type

    get_room_type.short_description = "Room Type"