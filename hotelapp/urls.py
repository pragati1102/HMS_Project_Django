from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('room/',views.room,name='room'),
    path('about/',views.about,name='about'),
    path('room_details/<int:id>',views.room_details,name='room_details'),
    path('blog/',views.blog,name='blog'),
    path('gallery/',views.gallery,name='gallery'),
    path('contact/',views.contact,name='contact'),
    path('login/',views.login_page,name='login'),
    path('signup/',views.signup,name='signup'),
    path('profile/',views.profile,name='profile'),
    path('logout/',views.logout,name='logout'),
    path('room_avaliable/',views.room_available,name='room_avaliable'),
    path('banquet',views.banquet,name='banquet'),
    path('meeting',views.meeting,name='meeting'),
    path('initiate-booking/<int:id>/', views.initiate_booking, name='initiate_booking'),

    # path('book_room/<int:id>/', views.book_room, name='book_room'),
    path('booking-sucess/',views.booking_sucess,name='booking_success')

]