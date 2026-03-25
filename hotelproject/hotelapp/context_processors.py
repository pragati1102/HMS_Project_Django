from .models import Register

def navbar_user(request):
    user_id = request.session.get('user_id')

    if user_id:
        try:
            user = Register.objects.get(id=user_id)
            return {'nav_user': user}
        except Register.DoesNotExist:
            pass

    return {'nav_user': None}
