# Radial Synth

This is the homepage for the Olin Spring 2018 Software Design Interactive Programming project as done by Jane Sieving and Lydia Hodges.

## Overview

We created a program that allows a user to 'draw' on a grid with different shapes and colors, and then play sound based on what they have 'drawn'.

## Results

We successfully created a screen that the user can interact with using their mouse. On the left hand side, taking up the majority of the screen, is a grid where the user can click to place different shapes of varying color and hue. On the right hand side, there are buttons that can be clicked on for different affects:
- Color buttons (red, green, blue, yellow): changes the mark that will be placed on the grid to the corresponding color
- Hue buttons (black and white): changes the intensity/brightness of the color of the mark that will be placed on the grid
- Clear button (X): clears all marks on the grid
- Play/Stop button (green triangle/red square): Changes cursor function so that clicking on grid plays sound, clicking while in play-mode will stop playing sound and allow user to place markers on grid again
- Shape buttons (circle and square): changes the mark that will be placed on the grid to the corresponding shape

![alt text](https://github.com/draconian9908/RadialSynth/blob/master/RadialSynth_Start.jpg)

*The initial screen, clean of marks, with the grid and buttons.*

![alt text](https://github.com/draconian9908/RadialSynth/blob/master/RadialSynth_Marked.png)

*The screen with marks, no sound currently playing*

We have also successfully integrated sound playback. After placing marks in the grid, the user clicks on the Play Button to change the cursor function, then clicks anywhere in the grid they want. The program looks at the grid spaces around where the user clicked in rings of increasing size, and plays a corresponding sound for each mark that lies on the current ring. Color determines instrument, hue determines note/pitch, and shape determines whether the note is short or sustained.

![alt text](https://github.com/draconian9908/RadialSynth/blob/master/RadialSynth_SoundRing.png)

*The screen with marks, currently playing sound. Light gray 'ring' is the ring currently playing sound.*

## Implementation
