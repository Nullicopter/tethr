"""
Here we define each front end module. They are in the format:

JS = {
    'module_name': ('path/to/compressed.js', [
        'lib/some/file.js',
        'lib/that/is/part.js',
        'lib/of/the/compressed/module.js'
    ])
}

There is a javascript and a CSS dict. Modules that contain both js and css
should be named the same.

There are multiple consumers of these dicts.

Scriptb uses this for concatenation and compression of the production files.

The templates/require.html module uses them as well:

<%namespace name="r" file="/require.html"/>
${r.require('core', 'test')}

The above would add all css and js includes from both the core and test modules
defined in this file. It will include the proper files depending on whether the
app is in production or dev.
"""
import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STRUCTURE = {
    'JS': {
        'base': os.path.join(PROJECT_PATH, 'public', 'j'),
        'type': 'js'
    },
    
    'CSS': {
        'base': os.path.join(PROJECT_PATH, 'public', 'c'),
        'type': 'css'
    }
}

JS = {
    'core': ('build/core.js', [
        
        'jquery.js',
        'include/jquery.form.js',
        'include/jquery.validate.js',
        'include/jquery.cookie.js',
        'include/jquery.json.js',
        'include/jquery.jeditable.js',
        'include/underscore.js',
        'include/backbone.js',
        
        'quaid/src/core.js',
        'quaid/src/log.js',
        'quaid/src/util.js',
        'quaid/src/widget.js',
        'quaid/src/form.js',
        'quaid/src/validation.js',
        
        'quaid/src/extension/backbone.js',
        'quaid/src/extension/debug.js',
        'quaid/src/extension/notifications.js',
        'quaid/src/extension/editablefield.js',
        
        'lib/base.js'
    ]),
    
    'test': ('build/modules/tests.js',[
        'test/base.js',
        'test/qunit.js',
        'test/test_base.js',
    ]),
    
    'controllers.auth': ('build/controllers/auth.js', ['controllers/auth.js']),
    'controllers.admin': ('build/controllers/admin.js', [
        'controllers/admin/base.js'
    ])
}

CSS = {
    'core': ('build/core.css', [
        'main.css',
        'forms.css',
        'core/notifications.css',
        'widgets/simpleconsole.css',
        'widgets/debugbar.css'
    ]),
    
    'test': ('build/modules/test.css', [
        'test/qunit.css',
    ]),
    
    'ie': ('build/ie.css', ['ie.css']),
    
    'controllers.admin': ('build/controllers/admin.css', [
        'controllers/admin.css'
    ])
}