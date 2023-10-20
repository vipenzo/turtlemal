import bpy
import math
import mathutils

###### Blender stuff

def run_lisp():
    text = bpy.context.space_data.text.as_string()
    print(f"executing: '{text}'")
    print(REP(f"(do {text})"))
    
def draw_func(self, context):
    layout = self.layout
    row = layout.row()
    row.operator("turtle_mal.execute_lisp", icon='EVENT_T')

class MTO_mal_turtle_operator(bpy.types.Operator):
    bl_idname = "turtle_mal.execute_lisp"
    bl_label = "Turtle Lisp execute"
    
    def execute(self, context):
        run_lisp()
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(MTO_mal_turtle_operator)
    bpy.types.TEXT_HT_header.append(draw_func)

def unregister():
    bpy.utils.unregister_class(MTO_mal_turtle_operator)
    bpy.types.TEXT_HT_header.remove(draw_func)

##### MAL Stuff
from .mal.stepA_mal import Env,core,types,sys,mal_readline,reader,printer,traceback,PRINT,EVAL,READ

# repl
repl_env = Env()
def REP(str):
    return PRINT(EVAL(READ(str), repl_env))

# core.py: defined using python
for k, v in core.ns.items(): repl_env.set(types._symbol(k), v)
repl_env.set(types._symbol('eval'), lambda ast: EVAL(ast, repl_env))
repl_env.set(types._symbol('*ARGV*'), types._list(*sys.argv[2:]))
repl_env.set(types._symbol('PI'), math.pi)

repl_env.set(types._symbol('is_close'), lambda n1,n2:(math.fabs(n1-n2) < 1e-9))
repl_env.set(types._symbol('abs'), math.fabs)
repl_env.set(types._symbol('sin'), math.sin)
repl_env.set(types._symbol('cos'), math.cos)
repl_env.set(types._symbol('tan'), math.tan)
repl_env.set(types._symbol('asin'), math.asin)
repl_env.set(types._symbol('acos'), math.acos)
repl_env.set(types._symbol('atan'), math.atan)
repl_env.set(types._symbol('sqrt'), math.sqrt)
repl_env.set(types._symbol('python_atan2'), math.atan2)
repl_env.set(types._symbol('atan2'), lambda x,y:(math.sqrt(x**2 + y**2), math.atan2(y/x)))
repl_env.set(types._symbol('to_degrees'), math.degrees)
repl_env.set(types._symbol('to_radians'), math.radians)

REP("(def! *host-language* \"python\")")
REP("(def! load-file (fn* [f] (eval (read-string (str \"(do \" (slurp f) \"\nnil)\") ))))")



import os
current_file_path = os.path.realpath(__file__)
addon_directory = os.path.dirname(current_file_path)
print(f"addon_directory={addon_directory}")
REP(f"(def! blender-addon-path \"{addon_directory}\")")
core_mal_path = os.path.join(addon_directory, "mal", "core.mal")
#
# core.mal: defined using the language itself
REP(f"(load-file \"{core_mal_path}\")")



#####  Blender specific extension

class Turtle:
    def __init__(self, plane = mathutils.Vector((0,0,1)), position = mathutils.Vector((0,0,0)), direction = mathutils.Vector((1,0,0))):
        # Imposta la direzione iniziale fornita o usa il vettore lungo l'asse X come predefinito
        self.plane = plane
        self.position = position
        self.direction = direction
        self.direction.normalize()
        #logger.log("init. direction="+str(self.direction))
    def context(self):
        return self.plane, self.position, self.direction
    def rotate_3d(self, x,y,z):
        #logger.log(f"prima della rotate 3d x={x} y={y} z={z}")
        matrix = mathutils.Euler((math.radians(x),math.radians(y),math.radians(z)),'XYZ').to_matrix()
        self.direction = self.direction @ matrix
        self.plane = self.plane @ matrix
        self.plane.normalize()
        #logger.log("dopo rotated3d")
    def move_3d(self,length):
        #self.log()
        self.position = self.position + self.plane * length
        #self.log()
    def forward(self, length):
        #logger.log(f"Turtle.forward length={length}")
        self.position=self.position+self.direction * length
        #self.log()
        return self.position
    def rotate(self, angle):
        #logger.log(f"Turtle.rotate angle={angle}")
        #logger.log("rotate:")
        #logger.log(angle)
        rotation_matrix = mathutils.Matrix.Rotation(math.radians(angle), 3, self.plane)
        self.direction = self.direction @ rotation_matrix
        self.direction.normalize()
        #self.log()


class Curve:
    def __init__(self, name, turtle, start_strenght, cyclic):
        print(f"Curve.__init__. parametro turtle={turtle}")
        self.name = name if name is not None else "TurtleCurve"
        self.cyclic = cyclic
        self.turtle = turtle if turtle is not None else Turtle()
        print(f"Curve.__init__. self.turtle={self.turtle}")
        self.start_position = self.turtle.position
        self.start_direction = self.turtle.direction
        self.curve_data = bpy.data.curves.new(name=self.name, type='CURVE')
        self.curve_data.dimensions = '3D'
        self.curve_data.resolution_u = 20
        self.dirty = False
        self.bezier_spline = self.curve_data.splines.new('BEZIER')
        self.last_point_index = 0
        self.strenght = start_strenght
        self.set_point_data(self.start_position, self.start_direction, start_strenght)
    def set_point_data(self, position, direction, strenght):
        p = self.bezier_spline.bezier_points[self.last_point_index]
        p.co = position
        p.handle_left_type = 'ALIGNED'
        p.handle_left = position - direction * strenght
        p.handle_right = position + direction * strenght
        self.strenght = strenght
    def add_point(self, end_position, end_direction, end_strenght):
        print(f"Curve.add_point. end_position={end_position}")
        self.last_point_index = self.last_point_index + 1
        self.bezier_spline.bezier_points.add(1)  
        self.set_point_data(end_position, end_direction, end_strenght)
        self.dirty = True
    def tangent_bezier(self, length, next_angle, strenght):
        # Aggiungi uno spline Bezier
        #logger.log("bezier")
        end_position = self.turtle.forward(length)
        self.turtle.rotate(next_angle)
        end_direction = self.turtle.direction
        self.add_point(end_position, end_direction, strenght)
    def move(self,length):
        print(f"Curve.move length={length}")
        end_position = self.turtle.forward(length)   ## TODO: forse qui bisogna creare un'altro bezier segment
        self.set_point_data(end_position, self.turtle.direction, self.strenght)
    def forward(self, length):
        print(f"Curve.forward length={length}")
        self.tangent_bezier(length, 0, 0)
    def rotate(self, angle):
        print(f"Curve.rotate angle={angle}")
        self.turtle.rotate(angle)       
    def rotate_3d(self, x,y,z):
        self.turtle.rotate3d(x,y,z)
    def close(self):
        if self.dirty:
            curve_object = bpy.data.objects.new(self.name, self.curve_data)
            bpy.context.collection.objects.link(curve_object)
            return curve_object


def create_turtle(from_turtle=None):
    if from_turtle is None:
        return Turtle()
    else:
        plane, position, direction = from_turtle.context()
        return Turtle(plane, position, direction)

def create_curve(turtle, start_strenght, cyclic, name):
    print(f"create_curve. turtle={turtle}, start_strenght={start_strenght}, cyclic={cyclic}, name={name} ")
    return Curve(name, turtle, start_strenght, cyclic)
   # EVAL([path_function [curve]],lisp_env)
    
def build_curve_object(curve):    
    return curve.close()   # returns the created object

def extrude_curve_object(guide_curve, profile_curve, taper_curve=None):
    #logger.log(f"extrude_curve. guide_curve={guide_curve} profile_curve={profile_curve}")
    guide_curve.data.bevel_mode = 'OBJECT'
    guide_curve.data.bevel_object = profile_curve
    guide_curve.data.use_fill_caps = True
    if taper_curve:
        guide_curve.data.taper_object = taper_curve
    
repl_env.set(types._symbol('create_turtle'), create_turtle)
repl_env.set(types._symbol('create_curve'), create_curve)
repl_env.set(types._symbol('extrude_curve_object'), extrude_curve_object)
repl_env.set(types._symbol('build_curve_object'), build_curve_object)
repl_env.set(types._symbol('forward'), lambda turtle,distance: turtle.forward(distance))
repl_env.set(types._symbol('rotate'), lambda turtle,angle: turtle.rotate(angle))
repl_env.set(types._symbol('move'), lambda turtle,distance: turtle.move(distance))

REP("""(def! get_or (fn [dict k defvalue] 
            (let [v (get dict k)]
                (if v v defvalue))))""")
REP("""(def! create_curve_object (fn [path_function options] 
    (let [curve (create_curve   
            (get_or options :turtle nil) 
            (get_or options :start_strenght 0) 
            (get_or options :cyclic false) 
            (get_or options :name nil)
            )]
        (path_function curve)
        (build_curve_object curve))))""")
