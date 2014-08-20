# -*- coding: utf-8 -*-
import datetime
import dateutil.parser
import dateutil.tz
import markdown as Markdown
import os

from flask import Blueprint
from jinja2 import contextfunction, Template, Markup
from tarbell.hooks import register_hook

NAME = "Grunt build template"

blueprint = Blueprint('base', __name__)


@contextfunction
def read_file(context, path, absolute=False):
    """
    Read the file at `path`. If `absolute` is True, use absolute path,
    otherwise path is assumed to be relative to Tarbell template root dir.
    """
    if not absolute:
        path = os.path.join(os.path.dirname(__file__), '..', path)

    try:
        return open(path, 'r').read()
    except IOError:
        return None


@contextfunction
def render_file(context, path, absolute=False):
    """
    Render a file with the current context
    """
    file_contents = read_file(context, path, absolute)
    template = Template(file_contents)
    return template.render(**context)


@blueprint.app_context_processor
def context_processor():
    """
    Add helper functions to context for all projects.
    """
    return {
        'read_file': read_file,
        'render_file': render_file,
    }


@blueprint.app_template_filter()
def process_text(text, scrub=True):
    try:
        return Markup(text)
    except TypeError:
        return ""


@blueprint.app_template_filter()
def format_date(value, format='%b. %d, %Y', convert_tz=None):
    """
    Format a date.
    """
    if isinstance(value, float) or isinstance(value, int):
        seconds = (value - 25569) * 86400.0
        parsed = datetime.datetime.utcfromtimestamp(seconds)
    else:
        parsed = dateutil.parser.parse(value)
    if convert_tz:
        local_zone = dateutil.tz.gettz(convert_tz)
        parsed = parsed.astimezone(tz=local_zone)

    return parsed.strftime(format)


@blueprint.app_template_filter()
def markdown(value):
    """Run text through markdown process"""
    if isinstance(value, basestring):
        value = value.decode("utf-8")
        return Markup(Markdown.markdown(value))
    return None
