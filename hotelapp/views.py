from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import Register,Room,Booking_room
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import datetime
from django.core.mail import send_mail




# Create your views here.
def index(request):
    unique_rooms = []
    seen_types = set()

    rooms = Room.objects.filter(room_available=True).order_by('-room_rating')

    for room in rooms:
        if room.room_type not in seen_types:
            unique_rooms.append(room)
            seen_types.add(room.room_type)

    return render(request, "index.html", {
        'rooms': unique_rooms[:4]   # show top 4 unique rooms
    })

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
    return render(request,'blog/banquet.html')

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
            booked = Booking_room.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in
            ).exists()

            if not booked:
                available_rooms.append(room)

        available_rooms = available_rooms[:required_rooms]

    return render(request, 'availability.html', {'rooms': available_rooms})

def banquet(request):
    return render(request,'blog/banquet.html')

def meeting(request):
    return render(request,'blog/meeting.html')

def booking_sucess(request):
    return render("Success.html")

def initiate_booking(request,id):
    if not request.session.get('user_id'):
        return redirect('login')
    
    user =Register.objects.get(id=request.session['user_id'])
    room =get_object_or_404(Room,id=id)

    check_in = datetime.strptime(request.POST['check_in'],"%Y-%m-%d").date()
    check_out = datetime.strptime(request.POST['check_out'],"%Y-%m-%d").date()
    payment_method = request.POST['payment_method']

    nights = (check_out - check_in).days
    total_amount = nights * room.room_price


    booking = Booking_room.objects.create(
        user=user,
        room=room,
        check_in=check_in,
        check_out=check_out,
        nights=nights,
        total_amount=total_amount,
        payment_method=payment_method,
        # payment_id=order['id']
    )

    return render(request,"room_details.html")