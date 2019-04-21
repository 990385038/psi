# -*- coding: utf-8 -*-
from django import forms


class FormClientIncome(forms.Form):
    client = forms.IntegerField()
    money = forms.FloatField()


class FromClientIncomeTotal(forms.Form):
    client = forms.IntegerField()


class FormClientIncomeHistory(forms.Form):
    client = forms.IntegerField()
