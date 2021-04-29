# -*- coding: utf-8 -*-
# @Author: Phu Hoang
# @Date:   2017-01-19 17:20:24
# @Last Modified by:   Phu Hoang
# @Last Modified time: 2017-01-19 18:57:18

from django import template

import re

from django.urls import reverse


class _Menu:
    parents = []
    children = []
    models_icon = {}

    def clear(self):
        self.parents = []
        self.children = []

    def add(self, label, link='', icon='', id_='', parent=''):

        if id_ == '':
            id_ = label

        if parent != '':
            child = {
                id_: {
                    'label': label,
                    'link': link,
                    'icon': icon,
                    'children': []
                }
            }

            self.children.append(child)

            for idx, parent_item in enumerate(self.parents):

                if parent in parent_item:
                    self.parents[idx][parent]['children'].append(child)
                else:
                    for idx, child_item in enumerate(self.children):
                        if parent in child_item:
                            self.children[idx][parent]['children'].append(child)

        else:
            self.parents.append({
                id_: {
                    'label': label,
                    'link': link,
                    'icon': icon,
                    'children': []
                }
            })

    def render(self, context, menus=None):
        menus = {} if menus is None else menus
        request = context['request']

        r = ''

        if len(menus) <= 0:
            # sorted(self.parents)
            menus = self.parents
            if (request.path == reverse('admin:index')):
                r = '<li class="nav-item"><a href="' + reverse(
                    'admin:index') + '" class="nav-link active"><i class="nav-icon fas fa-tachometer-alt"></i> <p>Home</p></a></li>'
            else:
                r = '<li class="nav-item"><a href="' + reverse(
                    'admin:index') + '" class="nav-link"><i class="nav-icon fas fa-tachometer-alt"></i> <p>Home</p></a></li>'

        for group in menus:
            key = [key for key in group][0]
            icon = '<i class="far fa-circle nav-icon"></i>'

            if group[key]['icon'] != '':
                if re.match(r'\<([a-z]*)\b[^\>]*\>(.*?)\<\/\1\>', group[key]['icon']):
                    icon = group[key]['icon']
                else:
                    icon = '<i class="%s"></i>' % (group[key]['icon'])

            if len(group[key]['children']) > 0:
                r += '<li class="nav-item has-treeview"><a href="#" class="nav-link">%s <span>%s</span><span class="pull-right-container"><i class="fas fa-angle-left right"></i></span></a><ul class="treeview-menu">\n' % (
                    icon, group[key]['label'])

                r += self.render(context, group[key]['children'])

                r += '</ul></li>\n'

            else:
                if (request.path == reverse('admin:index')):
                    r += '<li class="nav-item"><a href="%s" class="nav-link">%s <p>%s</p></a></li>\n' % (
                        group[key]['link'], icon, group[key]['label'])
                else:
                    r += '<li class="nav-item"><a href="%s" class="nav-link">%s <p>%s</p></a></li>\n' % (
                        group[key]['link'], icon, group[key]['label'])

        return r

    def admin_apps(self, context, r):
        request = context['request']
        for app in context['available_apps']:
            app_name = app['name'][:20] + '...' if len(app['name']) >= 20 else app['name']
            if (str(app['app_url']) in request.path):
                r += '<li class="nav-item has-treeview menu-open"><a href="#" class="nav-link active"><i class="nav-icon fas fa-edit"></i> <p>%s</p><p><i class="fas fa-angle-left right"></i></p></a><ul class="nav nav-treeview">\n' % (
                    app_name)
            else:
                r += '<li class="nav-item has-treeview"><a href="#" class="nav-link"><i class="nav-icon fas fa-edit"></i> <p>%s</p><p><i class="fas fa-angle-left right"></i></p></a><ul class="nav nav-treeview">\n' % (
                    app_name)

            for model in app['models']:
                if 'add_url' in model:
                    url = model['add_url']

                if 'change_url' in model:
                    url = model['change_url']

                # if 'delete_url' in model:
                #     url = model['delete_url']

                if 'admin_url' in model:
                    url = model['admin_url']

                icon = '<i class="far fa-circle nav-icon"></i>'
                if model['object_name'].title() in self.models_icon:
                    if self.models_icon[model['object_name'].title()] != '':
                        if re.match(r'\<([a-z]*)\b[^\>]*\>(.*?)\<\/\1\>',
                                    self.models_icon[model['object_name'].title()]):
                            icon = self.models_icon[model['object_name'].title()]
                        else:
                            icon = '<i class="%s"></i>' % (self.models_icon[model['object_name'].title()])
                if (request.path == url):
                    r += '<li class="nav-item"><a href="%s" class="nav-link active">%s %s</a></li>' % (
                    url, icon, model['name'])
                else:
                    r += '<li class="nav-item"><a href="%s" class="nav-link">%s %s</a></li>' % (
                    url, icon, model['name'])

            r += '</ul></li>\n'

        return r

    def set_model_icon(self, model_name, icon):
        self.models_icon[model_name.title()] = icon

    def get_model_icon(self, context):

        icon = '<i class="far fa-circle nav-icon"></i>'
        if context['model']['object_name'].title() in self.models_icon:

            if self.models_icon[context['model']['object_name'].title()] != '':
                if re.match(r'<([a-z]*)\b[^>]*>(.*?)</\1>', self.models_icon[context['model']['object_name'].title()]):
                    icon = self.models_icon[context['model']['object_name']]
                else:
                    icon = '<i class="%s"></i>' % (self.models_icon[context['model']['object_name'].title()])

        return icon


register = template.Library()

Menu = _Menu()


@register.simple_tag(takes_context=True, name='menu')
def menu_tag(context):
    return Menu.admin_apps(context, Menu.render(context))


@register.simple_tag(takes_context=True, name='icon')
def icon_tag(context):
    return Menu.get_model_icon(context)


@register.filter(name='modulo')
def modulo(val, num):
    return int(val) % int(num)

@register.filter(name='grp_name')
def grp_name(mem):
    abc = []
    for i in mem.groups.all():
        abc.append(i.name)
    return abc

@register.filter(name='grp_id')
def grp_id(obj,key):
    return obj[int(key)]['grp_id']
#
# @register.filter(name='key')
# def key(dict,key):
#     print(dict,key)
#     return dict[key]

@register.filter(name='str_int')
def str_int(val):
    return int(val)

@register.filter(name='sub')
def sub(num1,num2):
    return int(num1)-int(num2)

@register.filter(name='str')
def strf(str):
    return str(str)

from _datetime import datetime
@register.filter(name='installmentdate')
def installmentdate(date1):
    date1 = datetime.strptime(date1, '%Y-%m-%d')
    date2 = datetime.now()
    print(date1,date2)
    if date1>=date2:
        return date1.strftime("%Y-%m-%d")
    else:
        return ""

@register.filter(name='replace')
def replace(txt):
    return txt.split(':')[0]

@register.filter(name='replace1')
def replace1(txt):
    return txt.split(':')[1]

import math
@register.filter(name='div')
def sub(num1,num2):
    return int(num1)//int(num2)