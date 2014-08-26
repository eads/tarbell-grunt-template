# -*- coding: utf-8 -*-
import datetime
import dateutil.parser
import dateutil.tz
import markdown as Markdown
import os
import sh
import shutil

from clint.textui import puts, colored
from flask import Blueprint
from jinja2 import contextfunction, Template, Markup
from tarbell.hooks import register_hook
from tarbell.cli import _mkdir

NAME = "Grunt build template"

EXCLUDES = ["Gruntfile.js", "package.json", "node_modules/*", "less/*"]

blueprint = Blueprint('base', __name__)


@register_hook('server_start')
def grunt_watch(site):
    """Start grunt watch"""
    grunt = sh.grunt.bake('watch', _cwd=site.path, _bg=True)
    proc = grunt()
    site.grunt_pid = proc.pid
    puts("Starting Grunt watch (pid: {0})".format(colored.yellow(proc.pid)))


@register_hook('server_stop')
def grunt_stop(site):
    """Stop grunt watch"""
    puts("Stopping Grunt watch")
    sh.kill(site.grunt_pid)


def setup_grunt(site, git):
    """Set up grunt"""
    os.chdir(site.path)
    puts("Installing node packages")
    print(sh.npm("install", _cwd=site.path))
    puts("Running grunt")
    print(sh.grunt(_cwd=site.path))


@register_hook('newproject')
def newproject_grunt(site, git):
    """Copy grunt files to new project and run setup"""
    blueprint_path = os.path.join(site.path, '_blueprint')

    puts("Copying Gruntfile.js to new project")
    shutil.copyfile(os.path.join(blueprint_path, 'Gruntfile.js'),
                    os.path.join(site.path, 'Gruntfile.js'))

    puts("Copying package.json to new project")
    shutil.copyfile(os.path.join(blueprint_path, 'package.json'),
                    os.path.join(site.path, 'package.json'))

    puts(git.add("Gruntfile.js"))
    puts(git.add("package.json"))
    puts(git.commit(m='Add Gruntfile.js and package.json'))

    _mkdir(os.path.join(site.path, 'src'))

    puts("Copying default assets")
    _mkdir(os.path.join(site.path, 'src/less'))
    shutil.copyfile(os.path.join(blueprint_path, 'src/less/main.less'),
                    os.path.join(site.path, 'src/less/main.less'))

    _mkdir(os.path.join(site.path, 'src/js'))
    shutil.copyfile(os.path.join(blueprint_path, 'src/js/app.js'),
                    os.path.join(site.path, 'src/js/app.js'))

    puts(git.add("src/js/app.js"))
    puts(git.add("src/less/main.less"))
    puts(git.commit(m='Add default javascript and LESS assets'))

    setup_grunt(site, git)


@register_hook('install')
def install_grunt(site, git):
    """Run grunt setup on project install"""
    setup_grunt(site, git)


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
