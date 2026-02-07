from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import Register,Room,Booking
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    rooms = Room.objects.filter(room_available=True).order_by('-room_rating')[:4]
    return render(request,"index.html",{'rooms':rooms})

def room(request):
    room_list = Room.objects.filter(room_available=True).order_by('room_price')
    paginator = Paginator(room_list,6)
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number) 
    return render(request,'rooms.html',{'rooms': rooms} )

def about(request):
    return render(request,'about-us.html')

def room_details(request,id):
    room = get_object_or_404(Room,id=id)
    previous_page = request.META.get('HTTP_REFERER')
    return render(request,'room-details.html', {'room':room ,'previous_page': previous_page})

def blog(request):
    return render(request,'blog.html')

def gallery(request):
    return render(request,'gallery.html')

def contact(request):
    return render(request,'contact.html')

def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Register.objects.get(email=email,password=password)
        except:
            return render(request,'auth/login.html',{
                "error" : "Credentials are not Matched"
            })
        request.session['user_id'] = user.id
        return redirect("index")
        
    return render(request, 'auth/login.html')
    

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_pass = request.POST.get('conf_password')

        if password != confirm_pass:
            return render(request, 'auth/signup.html', {
                'error': 'Passwords do not match'
            })

        if Register.objects.filter(username=username).exists():
            return render(request, 'auth/signup.html', {
                'error': 'Username already exists'
            })

        Register.objects.create(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(request, 'auth/signup.html')

def profile(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    customer = Register.objects.get(id=user_id)
    return render(request, 'profile.html', {'customer': customer})

def logout(request):
    request.session.flush()
    return redirect("login")

def room_available(request):
    return render(request,"availablity.html")

def check_availability(request):
    # 🔐 manual login check
    if not request.session.get('user_id'):
        return redirect('login')

    available_rooms = []

    if request.method == 'POST':
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")
        persons = int(request.POST.get("persons"))
        required_rooms = int(request.POST.get("rooms"))

        all_rooms = Room.objects.filter(
            room_capacity__gte=persons,
            room_available=True
        )

        for room in all_rooms:
            booked = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in
            ).exists()

            if not booked:
                available_rooms.append(room)

        available_rooms = available_rooms[:required_rooms]

    return render(request, 'availability.html', {'rooms': available_rooms})

def book_room(request, room_id):
    if not request.session.get('user_id'):
        return redirect('login')

    user = Register.objects.get(id=request.session['user_id'])
    room = get_object_or_404(Room, id=room_id)

    Booking.objects.create(
        user=user,
        room=room,
        check_in=request.POST.get('check_in'),
        check_out=request.POST.get('check_out')
    )

    return redirect('profile')

def banquet(request):
    return render(request,'blog/banquet.html')

def meeting(request):
    return render(request,'blog/meeting.html')
