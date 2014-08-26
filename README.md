Tarbell + Grunt blueprint
=========================

A proof-of-concept [Tarbell blueprint](http://tarbell.tribapps.com) that includes 
a simple integration with Grunt to build and optimize project assets.

## Install ##

Install node and npm with `brew install node` on OS X or `apt-get install nodejs npm` on Ubuntu.

Install grunt globally:

    npm install -g grunt
    npm install -g grunt-cli
    
Install the Tarbell blueprint with:

    tarbell install-template https://github.com/eads/tarbell-grunt-template
    
Create a new project using the blueprint by running `tarbell newproject` and selecting
the grunt blueprint when prompted. When you run `tarbell serve`, the Grunt watch system
will be invoked and rebuild your assets when you edit them.

## Basic usage ##

To compile css to `css/main.css`, edit `src/less/main.less`. 

All `.js` files in `src/js/` will compile to `js/tarbell-app.min.js`. An empty `src/js/app.js` 
file is provided as a starting point.

The `_base.html` base template file already includes references to the compiled assets:

```
{% block css %}
<link rel="stylesheet" type="text/css" href="css/main.css" />
{% endblock %
```

```
{% block scripts %}
<script src="js/tarbell-app.js"></script>
{% endblock %
```

## Advanced usage ##

Edit `Gruntfile.js` and 'package.json` and override the `_base.html` blocks or template to fit your needs.
