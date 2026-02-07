from django.contrib import admin
from .models import Register,Room,Booking

# Register your models here.
@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("username","email","password")

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_num","room_type","room_price","room_rating","room_available")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('check_in','check_out','user','room')
