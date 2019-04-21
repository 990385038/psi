# -*- coding:utf-8 -*-
from django import forms


class comfirm_login_form(forms.Form):
    code = forms.CharField(
        label='企业微信返回码',
        min_length=5,
        max_length=128,
        error_messages={
            'required': u'code不能为空', }
    )
    state = forms.CharField(
        label='csrd_token',
        min_length=5,
        max_length=32,
        error_messages={
            'required': u'state不能为空', }
    )
