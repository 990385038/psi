# -*- coding: utf-8 -*-
from django import forms


class FormOrderMoney(forms.Form):
    need_type = forms.IntegerField(required=True, error_messages={'required': '未指定应发还是应付'})


class FormClientMoney(forms.Form):
    id = forms.IntegerField(required=True, error_messages={'required': '未指定供应商或者客户'})