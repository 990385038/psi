# -*- coding: utf-8 -*-
import json

from django import forms
from jsonschema import validate


# 盘点时的查询商品
class FormGoods(forms.Form):
    warehouse = forms.IntegerField()


# 盘点
class FormCheck(forms.Form):
    json_goods_str = forms.CharField()  # 用jsonschema校验

    def clean(self):
        cleaned_data = self.cleaned_data
        json_goods = json.loads(cleaned_data['json_goods_str'])
        json_schema = {
            "type": "object",
            "required": ["goods", "warehouse", "check_time"],
            "properties": {
                "goods": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["goods", "batch", 'num'],
                        "properties": {
                            "goods": {"type": "integer"},
                            "batch": {"type": "string"},
                            "num": {"type": "integer"},
                        },
                    }
                },
                "warehouse": {"type": "integer"},
                "check_time": {"type": "string"},
            }
        }
        try:
            validate(json_goods, json_schema)
        except Exception as e:
            raise forms.ValidationError(e)
        return cleaned_data


# 调拨
class FormChange(forms.Form):
    json_goods_str = forms.CharField()  # 用jsonschema校验

    def clean(self):
        cleaned_data = self.cleaned_data
        json_goods = json.loads(cleaned_data['json_goods_str'])
        json_schema = {
            "type": "object",
            "required": ["goods", "warehouse_out", "warehouse_in", "change_time"],
            "properties": {
                "goods": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["goods", "batch", 'num'],
                        "properties": {
                            "goods": {"type": "integer"},
                            "batch": {"type": "string"},
                            "num": {"type": "integer"},
                        },
                    }
                },
                "warehouse_out": {"type": "integer"},
                "warehouse_in": {"type": "integer"},
                "change_time": {"type": "string"},
            }
        }
        try:
            validate(json_goods, json_schema)
        except Exception as e:
            raise forms.ValidationError(e)
        return cleaned_data


# 加工
class FormWork(forms.Form):
    json_goods_str = forms.CharField()  # 用jsonschema校验

    def clean(self):
        cleaned_data = self.cleaned_data
        json_goods = json.loads(cleaned_data['json_goods_str'])
        json_schema = {
            "type": "object",
            "required": ["goods_out", "goods_in", "warehouse_out", "warehouse_in", "work_time"],
            "properties": {
                "goods_out": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["goods", "batch", 'num'],  # 此处批次号从库存查到的商品选入
                        "properties": {
                            "goods": {"type": "integer"},
                            "batch": {"type": "string"},
                            # "num": {"type": "integer"},
                            "num": {"type": "string"},  # 前端要发字符串
                        },
                    }
                },
                "goods_in": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["goods", "batch", 'num'],  # 此处批次号应从创建加工单填入
                        "properties": {
                            "goods": {"type": "integer"},
                            "batch": {"type": "string"},
                            "num": {"type": "integer"},
                        },
                    }
                },  # "warehouse_out": {"type": "integer"},
                "warehouse_out": {"type": "string"},  # 雄辉说加工时出发仓库只能发中文名，也唯一
                "warehouse_in": {"type": "integer"},
                "work_time": {"type": "string"},
            }
        }
        try:
            validate(json_goods, json_schema)
        except Exception as e:
            raise forms.ValidationError(e)
        return cleaned_data


# 校验仓库
class WareHouse(forms.Form):
    warehouse = forms.IntegerField()


# 详细某张单，调拨，盘点，加工共用
class OrderDetail(forms.Form):
    id = forms.IntegerField()
