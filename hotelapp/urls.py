from django.urls import path
from . import views
from . import admin_panel_views

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
    path('booking-sucess/',views.booking_sucess,name='booking_success'),
    path("success/<int:booking_id>/", views.payment_success_page, name="payment_success_page"),
    path("payment-success/", views.payment_success, name="payment_success"),

    # Custom themed admin panel (not Django's /admin/)
    path("admin-panel/login/", admin_panel_views.admin_login, name="admin_panel_login"),
    path("admin-panel/logout/", admin_panel_views.admin_logout, name="admin_panel_logout"),
    path("admin-panel/", admin_panel_views.admin_dashboard, name="admin_panel_dashboard"),
    path(
        "admin-panel/<str:model_name>/",
        admin_panel_views.admin_model_list,
        name="admin_panel_model_list",
    ),
    path(
        "admin-panel/<str:model_name>/add/",
        admin_panel_views.admin_model_add,
        name="admin_panel_model_add",
    ),
    path(
        "admin-panel/<str:model_name>/<int:pk>/edit/",
        admin_panel_views.admin_model_edit,
        name="admin_panel_model_edit",
    ),
    path(
        "admin-panel/<str:model_name>/<int:pk>/delete/",
        admin_panel_views.admin_model_delete,
        name="admin_panel_model_delete",
    ),
]
