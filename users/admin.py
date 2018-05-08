# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from .forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from .models import User
from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.html import format_html, format_html_join
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

from django import forms

from .models import (User, VCard, UserProfile)

class CustomUserAdmin(admin.ModelAdmin):
    '''
        This class render user zone in django admin.
    '''
    list_per_page = 10
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        #(_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active','user_type')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2','user_type'),
        }),
    )
    fieldsets_superadmin = (
        (None, {'fields': ('username', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions','user_type')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('get_full_name','username','user_profile','user_type', 'is_active')
    list_filter = ('is_active','user_type')
    search_fields = ('username',)#, 'first_name', 'last_name', 'email')
    ordering = ('username',)
    icon = "<i class='tiny material-icons'>perm_identity</i>"

    def user_profile(self, obj):
        up = UserProfile.objects.get_or_create(user=obj)[0]
        url = reverse('%s:%s_%s_change' % (
                            self.admin_site.name,
                            up._meta.app_label,
                            up._meta.model_name,
                        ),
                        args=(up.pk,),)
        return format_html('<a href="{}"><i class="material-icons">perm_identity</i></a>'.format(url))

    user_profile.short_description = 'Datos de Contacto'

    def get_queryset(self, request):
        qs = super(CustomUserAdmin, self).get_queryset(request)
        if request.user.is_administrator:
            return qs
        else:
            return qs.filter(user_type__gt = request.user.user_type)


    def save_model(self, request, obj, form, change):
        '''
        TODO: controlar privilegios del request.user
        '''
        obj.is_staff = True
        obj.save()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
                return self.fieldsets_superadmin
        return super(CustomUserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}

        if obj is None:
            defaults['form'] = self.add_form
        else:
            defaults['form'] = self.form
        defaults['form'].user = request.user
        defaults.update(kwargs)
        return super(CustomUserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            url(
                r'^(.+)/password/$',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ] + super(CustomUserAdmin, self).get_urls()

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(CustomUserAdmin, self).lookup_allowed(lookup, value)

    '''
    @sensitive_post_parameters_m
    @csrf_protect_m
    @transaction.atomic
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(CustomUserAdmin, self).add_view(request, form_url, extra_context)
    '''

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(id))
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(self.model._meta.verbose_name),
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )

    '''
    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST['_continue'] = 1
        return super(CustomUserAdmin, self).response_add(request, obj, post_url_continue)
    '''




from django.utils.html import format_html, format_html_join

from material import (Layout, Fieldset, Row, Column, Span,  Field,  # NOQA
                   Span2, Span3, Span4, Span5, Span6, Span7,
                   Span8, Span9, Span10, Span11, Span12,
                   LayoutMixin)


from django.template import loader, Context


class InlineVcardUser(admin.TabularInline):
    model = VCard
    exclude = ('store',)
    verbose_name = "VCard (Dato de contacto)"
    verbose_name_plural = "VCard (Datos de contacto)"
    extra = 1

class UserProfileAdmin(admin.ModelAdmin):
    hidden_level = User.ADMIN
    exclude = ('user','email','photo_social')

    inlines = [InlineVcardUser]

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(User, CustomUserAdmin)
