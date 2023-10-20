bl_info = {
    "name": "Turtle MAL",
    "author": "Vincenzo Piombo",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "category": "Development",
    "location": "Text Editor > Toolbar",
    "description": "Enables the creation of curves and meshes using Lisp scripts, following a turtle-based approach reminiscent of the Logo programming style.\nBased on https://github.com/kanaka/mal",
    "warning": "",
    "wiki_url": "",
}

from . import mal
from . import turtle_mal

def register():
    turtle_mal.register()

def unregister():
    turtle_mal.unregister()
