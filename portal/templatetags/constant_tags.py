from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_branch_name():
    return settings.BRANCH_NAME


@register.simple_tag
def get_branch_id():
    return settings.BRANCH_ID


@register.simple_tag
def get_actr_prefix():
    return settings.ACTR_NO_PREFIX

