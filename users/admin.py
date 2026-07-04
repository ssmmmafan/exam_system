from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django import forms
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from students.models import StudentProfile
from teachers.models import TeacherProfile


class CustomUserCreationForm(forms.ModelForm):
    """自定义用户创建表单"""
    role = forms.ChoiceField(
        choices=[
            ('student', '学生'),
            ('teacher', '教师'),
            ('admin', '管理员'),
        ],
        label='用户角色',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='选择用户角色，创建后将自动创建对应的档案'
    )
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput,
        help_text='至少3位字符'
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('两次密码输入不一致')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        role = self.cleaned_data.get('role', 'student')

        if commit:
            if role == 'student':
                user.is_staff = False
                user.is_superuser = False
            elif role == 'teacher':
                user.is_staff = True
                user.is_superuser = False
            elif role == 'admin':
                user.is_staff = True
                user.is_superuser = True

            user.save()

            if role == 'student':
                StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'student_id': f'S{user.id:06d}',
                        'class_name': '待分配',
                        'major': '待定'
                    }
                )
            elif role == 'teacher':
                TeacherProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'teacher_id': f'T{user.id:06d}',
                        'department': '待分配',
                        'title': 'lecturer'
                    }
                )

        return user


class CustomUserChangeForm(forms.ModelForm):
    """自定义用户修改表单"""
    role_info = forms.CharField(
        label='当前角色',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.is_superuser:
                self.initial['role_info'] = '管理员'
            elif self.instance.is_staff:
                if hasattr(self.instance, 'teacher_profile'):
                    profile = self.instance.teacher_profile
                    self.initial['role_info'] = f'教师 · {profile.teacher_id}'
                else:
                    self.initial['role_info'] = '教师'
            elif hasattr(self.instance, 'student_profile'):
                profile = self.instance.student_profile
                self.initial['role_info'] = f'学生 · {profile.student_id}'
            else:
                self.initial['role_info'] = '普通用户'


class StudentProfileInline(admin.StackedInline):
    """学生档案内联表单"""
    model = StudentProfile
    can_delete = False
    verbose_name = '学生档案'
    verbose_name_plural = '学生档案'
    fieldsets = (
        ('基本信息', {
            'fields': ('student_id', 'class_name', 'major')
        }),
        ('详细信息', {
            'fields': ('enrollment_year', 'phone'),
            'classes': ('collapse',)
        }),
    )

    def get_max_num(self, request, obj=None, **kwargs):
        return 1 if obj and not hasattr(obj, 'student_profile') else 0


class TeacherProfileInline(admin.StackedInline):
    """教师档案内联表单"""
    model = TeacherProfile
    can_delete = False
    verbose_name = '教师档案'
    verbose_name_plural = '教师档案'
    fieldsets = (
        ('基本信息', {
            'fields': ('teacher_id', 'department', 'title')
        }),
        ('联系方式', {
            'fields': ('phone', 'office'),
            'classes': ('collapse',)
        }),
    )

    def get_max_num(self, request, obj=None, **kwargs):
        return 1 if obj and not hasattr(obj, 'teacher_profile') else 0


class CustomUserAdmin(UserAdmin):
    """自定义用户管理"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ('username', 'email', 'get_role_badge', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    # 自定义密码修改链接
    def password_change_link(self, obj):
        url = reverse('admin:auth_user_password_change', args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" style="background: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">🔑 修改密码</a>',
            url
        )

    password_change_link.short_description = '密码操作'
    password_change_link.allow_tags = True

    # 字段集配置
    fieldsets = (
        (None, {'fields': ('username',)}),
        ('密码', {'fields': ('password_change_link',)}),
        ('个人信息', {'fields': ('first_name', 'last_name', 'email')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('role', 'username', 'email', 'password1', 'password2'),
        }),
    )

    # 只读字段
    readonly_fields = ('password_change_link',)

    def get_role_badge(self, obj):
        """显示角色标签"""
        if obj.is_superuser:
            return mark_safe(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 12px;">'
                '管理员</span>'
            )
        if obj.is_staff:
            if hasattr(obj, 'teacher_profile'):
                profile = obj.teacher_profile
                return mark_safe(
                    f'<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 12px;">'
                    f'教师 · {profile.teacher_id}</span>'
                )
            return mark_safe(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 12px;">'
                '教师</span>'
            )
        if hasattr(obj, 'student_profile'):
            profile = obj.student_profile
            return mark_safe(
                f'<span style="background-color: #17a2b8; color: white; padding: 3px 8px; border-radius: 12px;">'
                f'学生 · {profile.student_id}</span>'
            )
        if obj.is_active:
            return mark_safe(
                '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; border-radius: 12px;">'
                '学生</span>'
            )
        return mark_safe(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 12px;">'
            '未激活</span>'
        )

    get_role_badge.short_description = '角色'


# 反注册原来的 UserAdmin
try:
    admin.site.unregister(User)
except:
    pass

# 注册新的 UserAdmin
admin.site.register(User, CustomUserAdmin)

print("✅ 自定义 UserAdmin 已加载")