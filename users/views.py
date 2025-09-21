import time
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.contrib import messages
from services.models import Query
from users.forms import MyRegForm
from users.func_for_help import get_random_code
from users.models import CustomUser
from django.core.mail import send_mail
from config import settings
from django.core.cache import cache
from django.contrib import messages
import requests 
from django.contrib.auth import login 
from django.db import connection


class CustomLoginView(LoginView):
    authentication_form = AuthenticationForm
    model = CustomUser


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('serv_for_money:login') )


def my_registration(request):
    
    if request.user.is_authenticated:
            print("Вы уже авторизированны.")
            return HttpResponseRedirect(reverse('serv_for_money:serv_pars') )
    form = MyRegForm(request.POST) 
    if request.method == 'POST':
        print('1111111111111111111111111')

        if form.is_valid():
            print('444444444444444444444444', form.cleaned_data)
            reg_form_passw_value1 = form.cleaned_data.get('password1')
            reg_form_passw_value2 = form.cleaned_data.get('password2')
            reg_form_email_value = form.cleaned_data.get('email')
            reg_form_phonenumber_value = form.cleaned_data.get('phone_number')
            if reg_form_email_value in [i.email for i in CustomUser.objects.all()] or reg_form_phonenumber_value in \
                [i.phone_number for i in CustomUser.objects.all()]:
                print('reg_form_email_vaqlue', reg_form_email_value)
                print('Account already exists')
                messages.error(request, 'Account already exists')

                # messages.add_message(request, messages.INFO, 'Account created successfully')
                time.sleep(2)
                return HttpResponseRedirect(reverse('users:login') )
            elif not reg_form_passw_value1 == reg_form_passw_value2:
                messages.warning(request, 'Passwords not equal')
                context = { 
                    'form':form
                            } 
                return render(request, 'registration/register.html', context)
            
            """Здесь надо сгенерировать ссылку и отправить ее на емэйл, после сгенировать код и отправить с телефона"""
            code=get_random_code()
            link = reverse('users:confirm_reg', kwargs={'code':code, 'email': reg_form_email_value})
            print('11111111111111111222222222222222233333333333333', code)
            
            res = send_mail(
            subject='Подтвердите почту',
            message=f'http://127.0.0.1:8000/{link}',
            recipient_list=[reg_form_email_value],
            from_email=settings.EMAIL_HOST_USER
                )
            cache.set_many({'code':code, 'email': reg_form_email_value, 'phone_num':reg_form_phonenumber_value, 'password':reg_form_passw_value1}, timeout=100)
            cache_voc = cache.get_many(['code', 'email', 'phone_num', 'password'])
            # print('cache_voc1', cache_voc)
            if res:
                print(f'sending email to {reg_form_email_value}')
                print('request.__dict__', {k:v for (k,v)  in request._post.items()})#{'csrfmiddlewaretoken': '4gQ2kHKpiitdnOEPUGOEbiTkrjQi54nJquMdYH9wztPp3MMWqE2nbIks7AWr0Qp4', 'password1': 'qwer', 'password2': 'qwer', 'email': 'andreymazo@mail.ru', 'phone_number': '79211111111', 'submit': 'Register'}
                print('cache_voc1', cache_voc)
                return HttpResponseRedirect(reverse('users:notify_html'))#, kwargs={'code':code, 'email': reg_form_email_value}))
            
            else:#емэйл не прошел
                messages.error(request, 'Email not sent. Try again')
                return HttpResponseRedirect(reverse('users:my_registration'))
            
            # customuser = CustomUser.objects.create_user( email=reg_form_email_value, phone_number = reg_form_phonenumber_value,\
            #                                             password = reg_form_passw_value2)
            # # customuser.set_password(reg_form_passw_value1)
            # # customuser.save()
            # messages.success(request, 'Account created successfully')

            # time.sleep(3)
            # return HttpResponseRedirect(reverse('serv_for_money:serv_pars') )
 
    else: 
        form = MyRegForm() 
    context = { 
        'form':form
    } 
    return render(request, 'registration/register.html', context) 

def notify_html(request):
    try:
        cache_voc = cache.get_many(['code', 'email', 'phone_num', 'password'])
        code = cache_voc.get('code')
        email=cache_voc.get('email')
        phone_num=cache.get('phone_num')
        password=cache.get('password')
        print('cache_voc2', cache_voc)
        context = {'code':code,
               'email':email,
               'phone_num':phone_num,
               'password':password}
    except AttributeError as e:
        print(e)

    except ValueError as e:
        print(e)
        
    return render(request=request, template_name='users/templates/registration/notify.html', context=context)


def confirm_reg_email(request, **kwargs):
    #Если больше 100 секунд после отсылки емэйла, то тут пустой словарь в кэше
    # context = {}
    try:
        cache_voc = cache.get_many(['code', 'email', 'phone_num'])
        code = cache_voc.get('code')
        email=cache_voc.get('email')
        phone_num=cache.get('phone_num')
        password=cache.get('password')
        print('cache_voc3', cache_voc)
        
        context = {'code':code,
               'email':email,
               'phone_num':phone_num,
               'password':password}
    except AttributeError as e:
        print(e)
    except ValueError as e:
        print(e)
    
    print('fffffffffffffffff',  request.META.get('PATH_INFO'))# Через рекчест мета путь подберем код из ссылки, мы его с предыдущего ендпоинта послали
    path_info = request.META.get('PATH_INFO')
    parts = path_info.split('/')
    confirmation_code = parts[2]
    print('cc', code, confirmation_code)
    if confirmation_code==code:# Сравниваем что пришло из ссылки и то, что в кэше
        print('+++++++++++++++++ Переходим к отсылке смс и проверке телефона ++++++++++++++++++++++++')
        return HttpResponseRedirect(reverse('users:send_sms'))
    elif confirmation_code!=code:
        print('Вы прошли по неправильной ссылке. Заполните форму регистрации заново' \
        ' и пройдите по действительной ссылке')
        messages.error(request, "Вы прошли по неправильной или устаревшей ссылке. Заполните форму регистрации заново' \
        ' и пройдите по действительной ссылке")
        return HttpResponseRedirect(reverse('users:my_registration'))
        
"""Пока не делаем проверку телефона, просто его сохраняем, стоимость одного смс более 2 руб"""
def send_sms(request):
    #Если больше 100 секунд после отсылки емэйла, то тут пустой словарь в кэше
    try:
        cache_voc = cache.get_many(['code', 'email', 'phone_num'])
        code = cache_voc.get('code')
        email=cache_voc.get('email')
        phone_num=cache.get('phone_num')
        password=cache.get('password')
        print('cache_voc4', cache_voc)
        """Если дошел до сюда, значит проверка емэйла прошла. Берем пока данные из кэша и создаем пользователя. Потом запилим с отправкой кода и проверкой телефона"""
        customuser = CustomUser.objects.create_user( email=email, phone_number = phone_num,\
                                                        password = password)
        login(request=request, user=customuser)

        context = {'code':code,
            'email':email,
            'phone_num':phone_num,
            'password':password,
            'user':customuser,
            'user_id':customuser.id}
        return render(request=request, template_name='users/templates/registration/hello.html', context=context)
    except AttributeError as e:
        print(e)
        """Если оказались здесь, значит кэш пустой"""
        messages.error(request, 'Произошла ошибка (возможно долго проходили по ссылке). Залогиньтесь, если есть аккаунт, либо начните регистрацию заново')
        return HttpResponseRedirect(reverse('users:login'))
    except ValueError as e:
        print(e)
        """Если оказались здесь, значит кэш пустой"""
        messages.error(request, 'Произошла ошибка (возможно долго проходили по ссылке). Залогиньтесь, если есть аккаунт, либо начните регистрацию заново')
        return HttpResponseRedirect(reverse('users:login'))
    # code = get_random_code()
    # phone_num = cache.get('phone_num')
    # url =f'https://sms.ru/sms/send?api_id=A7B7B5D2-3F22-EDC8-21B6-43E0D20680E0&to={phone_num}&msg={code}d&json=1'
    # response = requests.get(url)
    
    # return render(request=request, template_name='users/templates/registration/send_sms.html', context=context)

def delete_query_table(request):

    with connection.cursor() as cursor:
        table_name = 'services_query'
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY;")
    return HttpResponseRedirect(reverse('users:home'))

def home(request):
    return render(request=request, template_name='users/templates/registration/hello.html')
