from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages


def uregister(request):
    if request.user.is_authenticated:
        return redirect("users:details", name=request.user.username)
    else:
        if request.POST:
            # if request.POST.get('submit') == 'Log In':
            #     return views.index_login(request)
            if request.POST.get('submit') == 'Register':
                username = request.POST.get('username')
                password = request.POST.get('password')
                email = request.POST.get('email')
                rep_password = request.POST.get('rep_password')

                if password != rep_password:
                    messages.error(request, "Entered passwords do not match")
                    context = {
                        "reg_username": username,
                        "reg_email": email,
                    }
                    return render(request, "registration/register.html", context=context)

                if User.objects.filter(username = username).exists():
                    messages.error(request, "User Already Exists")
                    return render(request, "registration/register.html")


                user = authenticate(username=username, password=password)

                if user is None:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    messages.success(request, """New User Created<br/> You Can Now <a href='%s'>Login</a> with Your User Name""")
                    return redirect('index')

                else:
                    #messages.error(request, "This user already exists")
                    return redirect('register')
        else:
            return render(request, "registration/register.html")