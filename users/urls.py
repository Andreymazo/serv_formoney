from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from users.apps import UsersConfig
from users.views import CustomLoginView, confirm_reg_email, delete_query_table, home, log_out, my_registration, notify_html, send_sms

app_name = UsersConfig.name

urlpatterns = [

    path('', CustomLoginView.as_view(template_name='users/templates/registration/login.html'), name='login'),
    path('log_out', log_out, name='log_out'),
    path('my_registration', my_registration, name='my_registration'),
    path('notify_html', notify_html, name='notify_html'),
    path('confirm_reg/<str:code>/<str:email>', confirm_reg_email, name='confirm_reg'),
    path('send_sms', send_sms, name='send_sms'),
    path('delete_query_table', delete_query_table, name='delete_query_table'),
    path('home', home, name='home'),
    

]