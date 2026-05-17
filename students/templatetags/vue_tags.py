from django import template
import json

register = template.Library()


@register.simple_tag
def vue_data(**kwargs):
    """将 Django 变量传递给 Vue"""
    data = {}
    for key, value in kwargs.items():
        if hasattr(value, 'values'):
            try:
                data[key] = list(value.values())
            except:
                data[key] = str(value)
        elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
            try:
                data[key] = list(value)
            except:
                data[key] = str(value)
        else:
            data[key] = value
    
    return f'<script id="vue-data" type="application/json">{json.dumps(data)}</script>'


@register.simple_tag
def vue_init(app_name='app'):
    """生成 Vue 初始化脚本"""
    return f'''
<script>
document.addEventListener('DOMContentLoaded', function() {{
    VueUtils.initFromDjango('{app_name}');
}});
</script>
'''


@register.filter
def to_json(obj):
    """将对象转换为 JSON 字符串"""
    return json.dumps(obj)