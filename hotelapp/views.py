from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import Register,Room,Booking_room
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import datetime
from django.core.mail import send_mail
import razorpay
from django.conf import settings

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
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    previous_page = request.META.get('HTTP_REFERER')
    user = None
    if request.session.get("user_id"):
        user = Register.objects.get(id=request.session['user_id'])

    return render(request,'room-details.html', {'room':room ,'previous_page': previous_page,'user':user,'check_in': check_in,
        'check_out': check_out
        })

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
    bookings = Booking_room.objects.filter(user=customer).order_by('-created_at')
    return render(request, 'profile.html', {'customer': customer, 'bookings': bookings})

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
    check_in = None
    check_out = None

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

    return render(request, 'availability.html', {'rooms': available_rooms,'check_in': check_in,
        'check_out': check_out
        })

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
    room = get_object_or_404(Room,id=id)

    if request.method =="POST":

        check_in = datetime.strptime(request.POST['check_in'],"%Y-%m-%d").date()
        check_out = datetime.strptime(request.POST['check_out'],"%Y-%m-%d").date()
        # payment_method = request.POST['payment_method']

    # ❗ Validate dates
        if check_out <=check_in:
            return redirect(request,"room_details",{
                "room": room,
                "user": user,
                "error": "Check-out must be after check=in"
            })
    
    # ❗ Overlap check (SAME LOGIC AS AVAILABILITY)
        overlap = Booking_room.objects.filter(
            room = room,
            check_in__lt = check_out,
            check_out__gt=check_in,
            payment_status = "SUCCESS"
        ).exists()

        if overlap:
            return redirect("room_details",{
                "room":room,
                "user":user,
                "error":"Room Already booked for selected dates"
            })
    
    # ✅ Calculate nights and total
        nights = (check_out - check_in).days
        total_amount = nights * room.room_price

        # 🔵 CREATE CLIENT HERE
        client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))

        payment = client.order.create({
            "amount":int(total_amount*100),
            "currency":"INR",
            "payment_capture" :"1"
        })

        booking =Booking_room.objects.create(
            user =user,
            room = room,
            check_in=check_in,
            check_out=check_out,
            nights=nights,
            total_amount=total_amount,
            payment_method="Card",
            payment_id=payment['id'],
            payment_status="PENDING"
        )

        return render(request,"payment.html",{
            "booking": booking,
            "payment": payment,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": int(total_amount * 100)
        })
    
    return redirect("room_details", id=id)

def payment_success(request):

    payment_id = request.GET.get('payment_id')
    booking_id = request.GET.get('booking_id')

    booking = Booking_room.objects.get(id=booking_id)

    booking.payment_id = payment_id
    booking.payment_status = "SUCCESS"
    booking.save()

    # ✅ Send Confirmation Email
    send_mail(
        "Room Booking Confirmation",
        f"""
        Dear {booking.user.username},

        Your booking is confirmed.

        Room: {booking.room.room_type}
        Check-in: {booking.check_in}
        Check-out: {booking.check_out}
        Nights: {booking.nights}
        Total Paid: ₹{booking.total_amount}

        Thank you!
        """,
        "your_email@gmail.com",
        [booking.user.email],
        fail_silently=False,
    )

    return render(request, "success.html", {"booking": booking})

     