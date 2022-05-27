from .models import Text, Image, Subject, UserProfile
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse
# import googlevisionapi
from django.shortcuts import render, redirect
from .forms import ImageForm
from .forms import TextForm
from .forms import CreateUserForm
from .forms import UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from django.contrib.auth.models import User
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
import reportlab
from django.http import FileResponse
from reportlab.pdfgen import canvas
import io
from django.template.loader import get_template
from xhtml2pdf import pisa

# from .decorators import allowed_users

import subprocess  # to add external scripts
import sys
sys.path.append(
    '/Users/rubenillouz/Documents/GitHub/fiches/ProjetFiches/googleapi')

# Create your views here.

# @allowed_users(allowed_roles=['admin'])


def some_view(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


def add_subject(request):
    user = request.user
    user_profiles = UserProfile.objects.filter(user=user)
    user_profile = user_profiles[0]  # en fait le tableau a qu'une case
    name = request.POST.get('add_subject')
    if name != "" and 'add_subject' in request.POST:
        subj = Subject(name=name)
        subj.save()
        user_profile.subjects.add(subj)


@login_required(login_url='login')
def start(request):
    return(redirect('index'))


@login_required(login_url='login')
def profil(request):
    # 1)On récupère les sujets
    user = request.user
    user_profiles = UserProfile.objects.filter(user=user)
    user_profile = user_profiles[0]  # en fait le tableau a qu'une case
    texts = Text.objects.filter(user=user)
    subjects = user_profile.subjects.all()

    UserForm = UserProfileForm(instance=user_profile)
    context = {'subjects': subjects, 'UserForm': UserForm}

    if request.method == 'POST':
        UserForm = UserProfileForm(request.POST,instance=user_profile )
        print(UserForm.errors)
        if UserForm.is_valid():
            UserForm.save()
            context = {'subjects': subjects, 'UserForm': UserForm}
            return render(request, 'Menu/profil.html', context)
    return render(request, 'Menu/profil.html', context)


@login_required(login_url='login')
def index(request, subject_id=None):
    # 1)On récupère les sujets
    user = request.user
    user_profiles = UserProfile.objects.filter(user=user)
    user_profile = user_profiles[0]  # en fait le tableau a qu'une case
    texts = Text.objects.filter(user=user)
    subjects = user_profile.subjects.all()
    current = ''  # current subject

    # inutile pour l'instant
    all_text_form = []
    for text in texts:
        # creation des forms avec tous les texts
        all_text_form += [TextForm(user, {'richtext': text})]

    # On s'occupe de ce qui est au milieu : traitement image et ecriture du texte
    image_form = ImageForm()
    if subject_id is not None:
        subject = Subject.objects.filter(id=subject_id)[0]
        richform = TextForm(user, {'subject': subject, 'user': user})
    else:
        richform = TextForm(user, {'user': user})

    if request.method == 'POST':
        form_type = request.POST.get("form_type")

        image_form = ImageForm(request.POST, request.FILES)
        richform = TextForm(user, request.POST, request.FILES)

        add_subject(request)

        if image_form.is_valid() and form_type == 'convertir':
            image_form.save()
            img_obj = image_form.instance
            # img_obj.image.url donne l'url de l'image et on transforme en texte
            text = googlevisionapi.transfo(img_obj.image.url)
            richform = TextForm(user, {'richtext': text, 'user': user})
            img_obj.delete()
            return render(request, 'Menu/index.html', {'image_form': image_form, 'richform': richform, 'subjects': subjects, 'current': current})

        if richform.is_valid() and form_type == 'enregistrer':
            richform.save()
            current_text = richform.instance
            current_text.user = user  # on ajout le nom d'utilisateur créant le texte au model
            if current_text.pdf:  # is there a pdf
                current_text.is_a_pdf = True  # on met true s'il s'agit bien d'un pdf
            current_text.save()
            subject_id = current_text.subject.id
            # if (subject_id not in user_profile.subjects):
            user_profile.subjects.add(current_text.subject)
            # print(user_profile.subjects)
            text_id = current_text.id
            # return render(request, 'Menu/index.html', {'image_form': image_form, 'richform':richform, 'subjects':subjects,'current':current})
            return(redirect('text', subject_id, text_id))

    return render(request, 'Menu/index.html', {'image_form': image_form, 'richform': richform, 'subjects': subjects, 'current': current})


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            user_profile = UserProfile(user=user)
            user_profile.save()
            messages.success(request, 'Compte créé pour '+username)
            return redirect('login')
    context = {'form': form}
    return(render(request, 'Menu/register.html', context))


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            context = messages.info(request, 'Username or password incorrect')
            return(render(request, 'Menu/login.html', context))
    context = {}
    return(render(request, 'Menu/login.html', context))


def logoutUser(request):
    logout(request)
    return(redirect('login'))


@login_required(login_url='login')
def userPage(request):
    us = request.user
    texts = Text.objects.filter(user=us)
    n = len(texts)
    subjects = user_profile.subjects.all()
    user = request.user
    richform = TextForm(user)
    form = ImageForm()
    all_text_form = []
    for text in texts:
        # pas besoin encore
        all_text_form += [TextForm(user, {'richtext': text, 'user': us})]
    context = {'form': form, 'richform': richform, 'texts': texts,
               'subjects': subjects, 'all_text_form': all_text_form}
    return(render(request, 'Menu/user.html', context))


@login_required(login_url='login')
def subject(request, subject_id):
    current = Subject.objects.get(pk=subject_id)
    # 1)On récupère les sujets et textes
    user = request.user
    user_profiles = UserProfile.objects.filter(user=user)
    user_profile = user_profiles[0]  # en fait le tableau a qu'une case
    subjects = user_profile.subjects.all()
    # current texts: appartiennent au bon sujet
    texts = Text.objects.filter(user=user, subject=current)
    text_in_current_subject = Text.objects.filter(subject=current, user=user)
    button_delete = False
    if len(text_in_current_subject) == 0:
        button_delete = True
    context = {'subjects': subjects, 'current': current, 'texts': texts,
               'subject_id': subject_id, 'button_delete': button_delete}
    if request.method == "POST":
        if 'delete' in request.POST:
            user_profile.subjects.remove(current)
            current.delete()
            return(redirect('index'))
        add_subject(request)
    return(render(request, 'Menu/subject.html', context))


@login_required(login_url='login')
def text(request, subject_id, text_id):
    user = request.user
    current_text = Text.objects.get(pk=text_id, user=user)

    current_subject = Subject.objects.get(pk=subject_id)  # current subject
    # 1)On récupère les sujets
    texts = Text.objects.filter(user=user)
    user_profiles = UserProfile.objects.filter(user=user)
    user_profile = user_profiles[0]  # en fait le tableau a qu'une case
    subjects = user_profile.subjects.all()

    # richform = TextForm({'richtext': current_text[0].richtext}) #creation du form avec le bon texte
    richform = TextForm(user, instance=current_text)

    is_a_pdf = current_text.is_a_pdf

    if request.method == 'POST':
        form_type = request.POST.get("form_type")
        button = request.POST.get("button")
        richform = TextForm(user, request.POST, instance=current_text)
        add_subject(request)
        if button == 'Delete':
            current_text.delete()
            return(redirect('subject', subject_id))
        if button == 'to_pdf':
            # si on change de sujet

            if (richform.instance.subject) != current_subject:  # si on change de sujet
                current_subject = richform.instance.subject
                # on ajoute le sujet s'il est nouveau  (pas besoin de tester s'il est)
                user_profile.subjects.add(richform.instance.subject)
            richform.user = request.user
            richform.save()  # prend les modifs en cours

            # puis pdf:
            # return(HttpResponse("ok"))
            return(redirect('to_pdf', current_subject.pk, text_id))  # a changer
        if button == 'view_pdf':
            # return(HttpResponse(current_text.pdf.path))

            return FileResponse(open(current_text.pdf.path, 'rb'), content_type='application/pdf')
            # return(HttpResponse("A faire"))©

        if richform.is_valid() and form_type == 'enregistrer':
            if (richform.instance.subject) != current_subject:  # si on change de sujet
                current_subject = (richform.instance.subject)
                # on ajoute le sujet s'il est nouveau  (pas besoin de tester s'il est)
                user_profile.subjects.add((richform.instance.subject))
            richform.user = request.user
            richform.save()
            return render(request, 'Menu/text.html', {'richform': richform, 'subjects': subjects, 'current_subject': current_subject, 'is_a_pdf': is_a_pdf})

    return render(request, 'Menu/text.html', {'richform': richform, 'subjects': subjects, 'current_subject': current_subject, 'is_a_pdf': is_a_pdf})


@login_required(login_url='login')
def to_pdf(request, subject_id, text_id):
    current_subject = Subject.objects.get(pk=subject_id)  # current subject
    #current_text = Text.objects.get(pk=text_id,user=request.user)
    current_text = Text.objects.get(pk=text_id)
    if current_text.is_a_pdf:
        return FileResponse(open(current_text.pdf.path, 'rb'), content_type='application/pdf')
    title = current_text.title
    richtext = current_text.richtext
    template_path = 'Menu/pdf.html'
    context = {'current_subject': current_subject,
               'richtext': richtext, 'title': title}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download:
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # else:
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required(login_url='login')
def search(request):
    user = request.user
    user_profiles = UserProfile.objects.filter(user=user)
    user_profile = user_profiles[0]  # en fait le tableau a qu'une case
    subjects = user_profile.subjects.all()
    context = {'subjects': subjects}
    if request.method == "POST":
        searched = request.POST.get('searched', False)
        texts = Text.objects.filter(title__contains=searched)
        texts |= Text.objects.filter(richtext__contains=searched)

        context = {'searched': searched, 'texts': texts, 'subjects': subjects}

        if not texts or not searched:
            context = {'texts': texts, 'subjects': subjects}
            return render(request, 'Menu/search.html', context)
        return render(request, 'Menu/search.html', context)

    return render(request, 'Menu/search.html', context)


@login_required(login_url='login')
def test(request):
    template_path = 'pdf.html'
    context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download:
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # else:
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
