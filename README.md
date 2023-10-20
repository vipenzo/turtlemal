# TurtleMal

An addon for [Blender](https://www.blender.org/) that introduces the capability to script using a Clojure-inspired Lisp language. It's perfect for Lisp and Clojure enthusiasts looking to extend and automate Blender in a functional paradigm.

## Features

- **Functional Language**: Write scripts for Blender with a pure functional touch, taking inspiration from Clojure.
- **Familiar Syntax**: If you're acquainted with Lisp or Clojure, you'll find yourself right at home. If you're new, it's an exciting opportunity to delve into functional programming!
- **Deep Integration**: This addon is crafted for a smooth experience within Blender, enabling you to tap into and manipulate Blender's objects and functions directly through your Lisp scripts.
- **3D Plane Turtle Graphics**: Drawing inspiration from the turtle geometry of the Logo programming language, this addon introduces a unique way of defining curves and shapes. While the "turtle" still draws on a 2D plane, users have the flexibility to move and rotate this plane within the 3D space of Blender. This provides a dynamic blend of 2D sketching and 3D positioning, allowing for intricate patterns and designs to be created with ease.

## Installation

1. Download the addon from this repository.
2. Launch Blender and head over to Preferences > Addons.
3. Click on "Install" and pick the downloaded zip file.
4. Find and activate the addon from the list.

## Usage Instructions
1. Navigate to the "Scripting" panel within Blender.
2. You'll notice a new button at the top left labeled "Turtle Lisp Execute".
3. Write or paste your Lisp code into Blender's text editor.
4. Click the "Turtle Lisp Execute" button to interpret and execute the Lisp code.


## Examples

### Regular polygons curves
```lisp
(defn regular_polygon_path [nsides side_len]
  (let [external_angle  (/ 360 nsides)
        internal_angle (- 180 external_angle)
        half_internal_angle (/ internal_angle 2)
        radius (/ (/ side_len 2) (cos (to_radians half_internal_angle)))]
    (fn [turtle]
      (println (sdump_ external_angle internal_angle half_internal_angle radius))
      (move turtle (negate radius))
      (rotate turtle (negate half_internal_angle))
      (dotimes [x nsides]
        (forward turtle side_len)
        (rotate turtle external_angle)))))

(defn square [side_len]
  (create_curve_object (regular_polygon_path 4 side_len) {:name "square"}))

(defn hexagon [side_len]
  (create_curve_object (regular_polygon_path 6 side_len) {:name "hexagon"}))


;(square 8)
;(hexagon 8)

(dotimes [x 12]
  (if (> x 2)
    (create_curve_object (regular_polygon_path x (* 2 x)) {:name (str "polygon " x " sides")}) x))