from django.urls import path
from django.conf.urls import url
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.start,name='start'), 
    path('index/',views.index,name='index'), 
    path('index/<int:subject_id>/',views.index,name='index'), 
    path('login/',views.loginPage,name='login'), 
    path('logout/',views.logoutUser,name='logout'), 
    path('register/',views.registerPage,name='register'), 
    path('user/',views.userPage,name='user'), 
    path('subject/<int:subject_id>/',views.subject,name='subject'), 
    path('text/<int:subject_id>/<int:text_id>/',views.text,name='text'),
    path('pdf/<int:subject_id>/<int:text_id>/',views.to_pdf,name='to_pdf'),
    path('search/',views.search,name='search'),
    path('profil/',views.profil,name='profil'),
    #test
    path('test/',views.test,name='test'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)