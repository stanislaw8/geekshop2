from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.conf import settings
from common.views import CommonContextMixin
from users.forms import UserLoginForm, UserRegistrationForm, UserChangeForm
from users.models import User
from baskets.models import Basket
import smtplib, ssl
from django.http import HttpResponseRedirect
from email.message import EmailMessage
from django.contrib import messages


class UserLoginView(CommonContextMixin, LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    title = 'GeekShop - Авторизация'


class UserProfileView(CommonContextMixin, UpdateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/profile.html'
    title = 'GeekShop - Личный кабинет'

    def get_success_url(self):
        return reverse_lazy('users:profile', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['baskets'] = Basket.objects.filter(user=self.object)
        return context


def send_verify_mail(user):

    verify_link = reverse('users:verify', args=[user.email, user.activation_key])

    msg = EmailMessage()
    msg['From'] = 'гикшоп'
    msg['To'] = user.email
    msg['Subject'] = f'подтверждение {user.username}'
    msg.set_content(f'для подтверждения регистрации {user.username}  на сайте {settings.DOMAIN_NAME} перейди по ссылке:  {settings.DOMAIN_NAME}{verify_link}')
    try:
        context=ssl.create_default_context()
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
            smtp.starttls(context=context)
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.send_message(msg)
            return 1
    except Exception as e:
        print('Ошибка отправки, свяжитесь с разрабом')
        print(f'error sending mail: {e.args}')
        return 0


def register(request):
    title = 'регистрация'
    
    if request.method == 'POST':
        register_form = UserRegistrationForm(request.POST, request.FILES)

        if register_form.is_valid():
            user = register_form.save()

            if send_verify_mail(user):
                messages.success(request, "Сообщение отправлено! Зайдите на почту и подтвердите учетную запись")
                return HttpResponseRedirect(reverse('users:login'))

            else:
                messages.error(request, 'Ошибка отправки сообщения, свяжитесь с разработчиком')
                return HttpResponseRedirect(reverse('users:login'))
        else:
            message = 'Введенные данные не валидны'
            register_form = UserRegistrationForm()
    else:
        message = 'Заполните поля'
        register_form = UserRegistrationForm()

    context = {'title': title, 'register_form': register_form, 'message': message}
    return render(request, 'users/register.html', context)


def verify(request, email, activation_key):
    try:
        user = User.objects.get(email=email)
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            return render(request, 'users/verification.html')
        else:
            print(f'error activation user: {user}')
            return render(request, 'users/verification.html')
    except Exception as e:

        print(f'error activation user : {e.args}')
        return HttpResponseRedirect(reverse('users:login'))


class UserLogoutView(LogoutView):
    pass
