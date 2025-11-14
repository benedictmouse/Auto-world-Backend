from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User


class UserCreationForm(forms.ModelForm):
    """Form for creating new users in the admin."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Form for updating users in the admin."""
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password/\">this form</a>."
        ),
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'is_active', 
                  'is_staff', 'is_superuser', 'is_approved')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_approved', 
                    'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_approved', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 
                       'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 
                       'is_staff', 'is_approved', 'is_active'),
        }),
    )
    
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    readonly_fields = ('last_login', 'date_joined')

    def get_readonly_fields(self, request, obj=None):
        """Make date_joined and last_login readonly when editing"""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('date_joined',)
        return self.readonly_fields

    # Custom actions
    actions = ['approve_workers', 'disapprove_workers', 'activate_users', 'deactivate_users']

    @admin.action(description='Approve selected workers')
    def approve_workers(self, request, queryset):
        updated = queryset.filter(is_staff=False).update(is_approved=True)
        self.message_user(request, f'{updated} worker(s) approved successfully.')

    @admin.action(description='Disapprove selected workers')
    def disapprove_workers(self, request, queryset):
        updated = queryset.filter(is_staff=False).update(is_approved=False)
        self.message_user(request, f'{updated} worker(s) disapproved.')

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')