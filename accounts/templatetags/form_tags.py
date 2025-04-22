from django import template
from django.forms.widgets import Input, Select, Textarea, CheckboxInput, RadioSelect, CheckboxSelectMultiple

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Thêm class CSS vào trường form
    Sử dụng: {{ form.field|add_class:"form-control" }}
    """
    if field.field.widget.__class__ in [CheckboxInput]:
        return field.as_widget(attrs={"class": css_class})
    elif field.field.widget.__class__ in [RadioSelect, CheckboxSelectMultiple]:
        # Xử lý đặc biệt cho radio và checkbox multiple
        return field
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='field_type')
def field_type(field):
    """
    Trả về loại widget của trường
    Sử dụng: {% if form.field|field_type == 'CheckboxInput' %}
    """
    return field.field.widget.__class__.__name__

@register.filter(name='placeholder')
def placeholder(field, text):
    """
    Thêm placeholder cho trường
    Sử dụng: {{ form.field|placeholder:"Nhập dữ liệu" }}
    """
    return field.as_widget(attrs={"placeholder": text}) 