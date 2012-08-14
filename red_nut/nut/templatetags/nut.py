#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django import template

register = template.Library()


@register.filter(name='capitalize')
def capitalize(value):
    return value.capitalize()


@register.filter(name='title')
def title(value):
    return value.title()
