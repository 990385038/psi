# -*- coding: utf-8 -*-
import json

from django import forms
from jsonschema import validate


class FormGoods(forms.Form):
    name = forms.CharField(required=True, max_length=100,
                           error_messages={'required': '商品名不能为空'})
    spec = forms.IntegerField(required=True,
                              error_messages={'required': '规格不能为空'})  # 规格的id
    type = forms.CharField(max_length=100)
    supplier = forms.IntegerField(required=True,
                                  error_messages={'required': '供应商不能为空'})  # 供应商/顾客的id
    rec_price = forms.FloatField()
    purchase_price = forms.FloatField()
    trade_price = forms.FloatField()
    retail_price = forms.FloatField()
    batch = forms.CharField()
    status = forms.IntegerField()


class FormEditGoods(forms.Form):
    id = forms.IntegerField(required=True, error_messages={'required': '商品id不能为空'})
    name = forms.CharField(required=True, max_length=20,
                           error_messages={'required': '商品名不能为空'})
    spec = forms.IntegerField(required=True,
                              error_messages={'required': '规格不能为空'})  # 规格的id
    type = forms.CharField(max_length=255)
    supplier = forms.IntegerField(required=True,
                                  error_messages={'required': '供应商不能为空'})  # 供应商/顾客的id
    rec_price = forms.FloatField()
    purchase_price = forms.FloatField()
    trade_price = forms.FloatField()
    retail_price = forms.FloatField()
    status = forms.IntegerField()


class FormDelGoods(forms.Form):
    id = forms.IntegerField()


class FormAddOrder(forms.Form):  # 新增订单校验json
    json_data_str = forms.CharField(max_length=1024)

    def clean(self):  # 重写clean，可以覆盖jaon_data_str，这里没覆盖
        cleaned_data = self.cleaned_data
        json_data = json.loads(cleaned_data["json_data_str"])
        json_schema = {
            "type": "object",
            "required": ["type", "client", "warehouse", "send_way", "count_type", "real_price",
                         "need_price", "orders"],
            "properties": {
                "type": {"type": "string"},
                "client": {"type": "integer"},
                "warehouse": {"type": "integer"},
                # "cabinets": {"type": "string"},
                "send_way": {"type": "string"},
                "count_type": {"type": "string"},
                "real_price": {"type": "number"},
                "need_price": {"type": "number"},
                "orders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["num", "need_price", "new_need_price", "batch", "goods"],
                        "properties": {
                            "num": {"type": "integer"},
                            "need_price": {"type": "number"},
                            "new_need_price": {"type": "number"},
                            "batch": {"type": "string"},
                            "goods": {"type": "integer"},
                        }
                    }
                },
            }
        }
        try:
            validate(json_data, json_schema)
        except Exception as e:
            raise forms.ValidationError(e)
        return cleaned_data


class FormUniteOrder(forms.Form):
    id = forms.IntegerField()


class FormEditOrder(forms.Form):  # 简单编辑订单校验
    id = forms.IntegerField()
    client = forms.IntegerField()
    warehouse = forms.IntegerField()
    cabinets = forms.CharField()
    send_way = forms.CharField()
    count_type = forms.CharField()
    real_price = forms.FloatField()  # 如果校验打错，会出现标准form报错
    need_price = forms.FloatField()


# 校验仓库
class WareHouse(forms.Form):
    warehouse = forms.IntegerField()


# 支付订单
class FormBillOrder(forms.Form):
    id = forms.IntegerField()
    money = forms.FloatField()


# 强行结案订单
class FormFinishOrder(forms.Form):
    id = forms.IntegerField()


# 审核通过订单
class ReviewedOrder(forms.Form):
    id = forms.IntegerField(required=True, error_messages={'required': '未指定订单'})
    is_pass = forms.IntegerField(required=True, error_messages={'required': '未指定审核状态'})
