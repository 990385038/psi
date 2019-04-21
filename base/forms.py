# -*- coding: utf-8 -*-
from django import forms


class FormGoods(forms.Form):
    name = forms.CharField(required=True, max_length=100,
                           error_messages={'required': '商品名不能为空'})
    spec = forms.IntegerField(required=True,
                              error_messages={'required': '规格不能为空', 'invalid': "规格需要输入id"})
    goods_class = forms.IntegerField(required=True,
                                     error_messages={'required': '类型不能为空', 'invalid': "分类需要输入id"})
    rec_price = forms.FloatField(required=True,
                                 error_messages={'required': '建议价格不能为空'})
    purchase_price = forms.FloatField(required=True,
                                      error_messages={'required': '采购价不能为空'})
    sale_price = forms.FloatField(required=True,
                                  error_messages={'required': '销售价不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})


class FormEditGoodsBefore(forms.Form):
    id = forms.IntegerField(required=True, error_messages={'required': '商品id不能为空'})


class FormEditGoods(forms.Form):
    id = forms.IntegerField(required=True, error_messages={'required': '商品id不能为空'})
    name = forms.CharField(required=True, max_length=20,
                           error_messages={'required': '商品名不能为空'})
    spec = forms.IntegerField(required=True,
                              error_messages={'required': '规格不能为空'})
    goods_class = forms.IntegerField(required=True,
                                     error_messages={'required': '类型不能为空'})
    rec_price = forms.FloatField(required=True,
                                 error_messages={'required': '建议价格不能为空'})
    purchase_price = forms.FloatField(required=True,
                                      error_messages={'required': '采购价不能为空'})
    sale_price = forms.FloatField(required=True,
                                  error_messages={'required': '销售价不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})


class FormDelGoods(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '删除商品不能为空'})


class FormEditClassBefore(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '选中的分类不能为空'})


class FormEditClass(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '编辑的分类不能为空', 'invalid': '输入要编辑分类的id'})
    name = forms.CharField(required=True,
                           error_messages={'required': '分类名字不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'invalid': '告诉是启用还是停用，不要发12'})


class FormAddClass(forms.Form):
    name = forms.CharField(required=True,
                           error_messages={'required': '分类名字不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})


class FormDelClass(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '删除分类不能为空'})


class FormEditSpecBefore(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '指定的规格不能为空'})


class FormEditSpec(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '编辑的规格不能为空'})
    name = forms.CharField(required=True,
                           error_messages={'required': '规格名不能为空'})
    sub_spec = forms.CharField(required=True,
                               error_messages={'required': '辅助规格不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})


class FormDelSpec(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '删除规格不能为空'})


class FormAddSpec(forms.Form):
    name = forms.CharField(required=True,
                           error_messages={'required': '规格名不能为空'})
    sub_spec = forms.CharField(required=True,
                               error_messages={'required': '辅助规格不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})


class FormAllClient(forms.Form):
    type = forms.IntegerField(required=True,
                              error_messages={'required': '查询供应商/顾客类型不能为空'})


class FormEditClientBefore(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '指定供应商/顾客不能为空'})


class FormEditClient(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '供应商/顾客不能为空'})

    name = forms.CharField(required=True,
                           error_messages={'required': '名字不能为空'})
    tel = forms.CharField(required=True,
                          error_messages={'required': '号码不能为空'})
    contacts = forms.CharField(required=True,
                               error_messages={'required': '联系人不能为空'})
    addr = forms.CharField(required=True,
                           error_messages={'required': '地址不能为空'})
    account = forms.CharField(required=True,
                              error_messages={'required': '账户不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})
    remarks = forms.CharField(required=True,
                              error_messages={'required': '备注不能为空'})


class FormAddClient(forms.Form):
    name = forms.CharField(required=True,
                           error_messages={'required': '名字不能为空'})
    tel = forms.CharField(required=True,
                          error_messages={'required': '号码不能为空'})
    contacts = forms.CharField(required=True,
                               error_messages={'required': '联系人不能为空'})
    addr = forms.CharField(required=True,
                           error_messages={'required': '地址不能为空'})
    account = forms.CharField(required=True,
                              error_messages={'required': '账户不能为空'})
    remarks = forms.CharField(required=True,
                              error_messages={'required': '备注不能为空'})
    type = forms.ChoiceField(required=True,choices=(('供应商',0),('顾客',1)),
                              error_messages={'required': '添加供应商/顾客类型不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})


class FormDelClient(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '删除供应商/顾客不能为空'})


class FormAllWarehouse(forms.Form):
    type = forms.IntegerField(required=True,
                              error_messages={'required': '库的类型不能为空'})


class FormAddWarehouse(forms.Form):
    name = forms.CharField(required=True,
                           error_messages={'required': '名字不能为空'})
    addr = forms.CharField(required=True,
                           error_messages={'required': '地址不能为空'})
    tel = forms.CharField(required=True,
                          error_messages={'required': '号码不能为空'})
    contacts = forms.CharField(required=True,
                               error_messages={'required': '联系人不能为空'})
    volume = forms.CharField(required=True,
                             error_messages={'required': '容量不能为空'})
    type = forms.CharField(required=True,
                           error_messages={'required': '库类型不能为空'})
    remarks = forms.CharField(required=True,
                              error_messages={'required': '库的备注不能为空'})
    storage_state = forms.CharField(required=True,
                                    error_messages={'required': '库存情况不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})


class FormDelWarehouse(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '删除仓库/门店不能为空'})


class FormEditWarehouseBefore(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '选中的仓库/门店不能为空'})


class FormEditWarehouse(forms.Form):
    id = forms.IntegerField(required=True,
                            error_messages={'required': '选中的仓库/门店不能为空'})
    name = forms.CharField(required=True,
                           error_messages={'required': '名字不能为空'})
    addr = forms.CharField(required=True,
                           error_messages={'required': '地址不能为空'})
    tel = forms.CharField(required=True,
                          error_messages={'required': '号码不能为空'})
    contacts = forms.CharField(required=True,
                               error_messages={'required': '联系人不能为空'})
    volume = forms.CharField(required=True,
                             error_messages={'required': '容量不能为空'})
    type = forms.ChoiceField(required=True, choices=(('仓库', 1), ('门店', 2)),
                             error_messages={'required': '库的类型不能为空'})
    storage_state = forms.ChoiceField(required=True, choices=(('已满', 0), ('未满', 1), ('空', 2)),
                                      error_messages={'required': '库存情况不能为空'})
    status = forms.ChoiceField(required=True, choices=(('停用', 0), ('启用', 1), ('删除/失效', 2)),
                               error_messages={'required': '状态不能为空', 'choices': '状态信息不正确'})
