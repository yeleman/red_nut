#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django import forms
#~ from django.shortcuts import render, RequestContext, redirect
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login as django_login, \
                                                logout as django_logout
from django.shortcuts import render_to_response, redirect, \
                                                    HttpResponseRedirect

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Nom d'utilisateur")
    password = forms.CharField(max_length=100, label="Mot de passe",\
                               widget=forms.PasswordInput)

def login(request):
    """ page de connection """
    form = LoginForm()
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    else:
        c = {'categorie': 'login'}
        c.update(csrf(request))

        if request.method == 'POST':

            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    state = "Your Account is not active,\
                                        please contact the site admin."
            else:
                c.update({'state': u"Votre nom d'utilisateur et / ou \
                                    votre mot de passe est incorrect. \
                                    Veuillez réessayer."})

        c.update({'form': form})

    return render_to_response('login_django.html', c)
