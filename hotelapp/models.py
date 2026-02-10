from django.db import models

# Create your models here.
class Register(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=8)

    def __str__(self):
        return self.email
    

class Room(models.Model):
    room_num = models.CharField(max_length=4)
    room_type =models.CharField(max_length=50)
    room_price = models.DecimalField(decimal_places=2,max_digits=10)
    room_image = models.ImageField(upload_to='rooms/')
    room_service = models.CharField(max_length=100)
    room_capacity = models.CharField(max_length=10)
    room_description = models.CharField(max_length=200)
    room_available = models.BooleanField(default=True)
    room_rating = models.FloatField(default=0)

    def __str__(self):
        return self.room_num
    
class Booking_room(models.Model):
    PAYMENT_CHOICES = [
        ('UPI','UPI'),
        ('CASH','cash'),
        ('Card','Credit card')
    ]

    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    check_in = models.DateField()
    check_out = models.DateField()
    nights = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10,decimal_places=2)

    payment_method = models.CharField(max_length=10,choices=PAYMENT_CHOICES)
    payment_id = models.CharField(max_length=100,blank=True,null=True)
    payment_status = models.CharField(max_length=20,default="PENDING")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.room.room_type}"







