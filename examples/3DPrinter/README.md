# Interaction with a 3D printer

This example demonstrates how to use the scope
to record signals at different points in space.
The points are on a grid.
A 3D printer moves the measurement probe along the grid.

## Overview

* `grid.py`:
This file creates the grid.
Control the spacing in x, y, z direction (variables `dx`, `dy`, `dz`).
You can also choose the maximal and minimal coordinates in x, y, z direction
and define forbidden points (e.g., where the measurement probe would collide with
and object).
Before each measurement run, the grid is plotted and in case of any mistake 
you can still safely abort the measurement run.
* `controlprinter.py`:
This file controls the printer. 
First, the grid is created as defined in `grid.py` and plotted.
Then, the grid is communicated to the main function that moves
the printer head and triggers the recording with the scope.
The main idea is:
1. Move the printer until it does not report changing positions.
2. Then wait for 2 seconds until the screen of the scope is freezed.
   The waveforms are then transferred to the computer and saved in a 
   YAML file.
3. Move to the next position in the grid.
* `moveup.py`:
In case of any error that makes the printer stop at a certain position,
you can run this script to move the printer head up such that you can
remove the measurement sample.
* `getheight.py`:
Move the needle down step-by-step to get an estimate of the fill level in the well.

*All files have to be copied to one directory and executed there!*


## Important settings and parameters

* COM port: `ser.port = "COM3"`
  This is the identifier of the USB port.
* The ID of your scope. This example was developed and tested for a Rigol MSO5000. 
  If you want to use a different scope, make sure it is interface through PyVISAScope
  and change line 69 of `controlprinter.py`.
* Waiting time before the screen is freezed: `sleepingtime`. 
