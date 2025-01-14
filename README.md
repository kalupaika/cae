© Ihor Mirzov, 2019-2021  
Distributed under GNU General Public License v3.0

[![Github All Releases](https://img.shields.io/github/downloads/calculix/cae/total.svg)](https://github.com/calculix/cae/releases)

<br/><br/>



---

[Downloads](https://github.com/calculix/cae/releases) |
[Features](#features) |
[Screenshots](#screenshots) |
[How to use](#how-to-use) |
[Your help](#your-help) |
[For developers](#for-developers) |
[What's new](#whats-new) |
[TODO](#todo)

---

<br/><br/>



# CalculiX Adanced Environment (CAE)

CAE is a software package mainly consisting of CalculiX [GraphiX](http://calculix.de/), [CrunchiX](http://dhondt.de/) and keyword editor. The last one - is a very simple, free and open source GUI/pre-processor for CalculiX. Program is based on the keywords hierarchy, is designed to guide you through the keywords creation process and is aimed to help you reach the correct input file with no mistakes. Keyword editor is written in Python3 and utilizes PyQt5.

It is implied that you have already created geometry and generated mesh in some other software like [FreeCAD](https://www.freecadweb.org/) or [Salome-platform](https://www.salome-platform.org/).

<br/><br/>



# Features

- CAE comes with the latest CGX and CCX compiled for both Linux and Windows. Analysis [runs on all cores](https://github.com/calculix/cae/issues/22) automatically.

- INP format for all needs: program parses .inp-file and generates model on the fly, so separate format for the model is not needed. Final model is saved also with .inp format ready to be calculated with CCX. Robust INP importer algorithm is tested on over 20 000 INP files, including Abaqus models ([see log](src/importer.log)).


- Official [HTML documentation](doc) is natively integrated into the keyword edit dialogs (Help button).

- Calculix keywords hierarchy with all attributes is maintaned in [editable XML file](config/kom.xml).

- [Solid mesh parser](src/model/parsers/mesh.py) supports includes in the input file. Tested on the all official CalculiX examples. See [mesh.log](src/model/parsers/mesh.log).

- Application's global settings could be set up in the File->Settings menu. Settings are maintained in editable Python file - it is automatically overwritten during the workflow.

- [Optimal job management](src/model/job.py):

    - if you use subroutines, CalculiX sources could be automatically recompiled from GUI;
    - run analysis directly from GUI;
    - open results in GraphiX or convert to VTU format and open them in [Paraview](https://www.paraview.org).

- CAE uses converters:

    - [ccx2paraview](https://github.com/calculix/ccx2paraview) - CalculiX to Paraview converter (frd to vtk/vtu)
    - [unv2ccx](https://github.com/calculix/unv2ccx) - Salome universal to CalculiX converter (unv to inp)

- Cute modern design with [nice icons](img).


<br/><br/>



# Screenshots

Keyword editor and CGX windows with imported mesh and painted surfaces:
![img1](img/img_surfaces.png "Painted surfaces")

"New keyword" dialog with corresponding chapter from HTML manual:
![img2](img/img_dialog.png "Keyword dialog")

Keyword editor and CGX windows with calculated model:
![img3](img/img_social.png "Calculation results")

New CGX colormaps - viridis, inferno, turbo:
![img4](img/img_cmaps.png "New CGX colormaps")

Calculation result exported to Paraview:
![img5](img/img_paraview.png "Results in Paraview")

<br/><br/>



# How to use

Get [Python3](https://www.python.org/downloads/) (>3.8) and install it.

[Download latest release](https://github.com/calculix/cae/releases) (source code) and unpack it.

Open terminal in a directory where you've unpacked CAE. Allow all files to be executed (Linux only):

    sudo chmod -R 777 ./*

Install dependencies with command:

    pip3 install -r requirements.txt

It's OK if Xlib installation will fail in Windows.

That's all, enjoy!

Run the software with command (or double click those files):

    in Linux:       ./cae.sh
    in Windows:     cae.bat

You can edit default startup model name in File->Settings or leave it empty or even pass it as an argument to open on startup:

    in Linux:       ./cae.sh -inp yourmodel.inp
                    ./cae.sh -inp yourmodel.unv
    in Windows:     cae.bat -inp yourmodel.inp
                    cae.bat -inp yourmodel.unv

Another way to run CAE - is directly from 'src' directory:

    python3 ./src/cae.py
    python3 ./src/cae.py -inp yourmodel.inp
    python3 ./src/cae.py -inp yourmodel.unv

The intended workflow is:

- create geometry and mesh in [FreeCAD](https://www.freecadweb.org/) or [Salome-platform](https://www.salome-platform.org/),
- save mesh as UNV or export it to INP with [Salome to CalculiX mesh exporter](https://github.com/psicofil/SalomeToCalculix),
- import INP or UNV mesh into CAE and continue creating model,
- if needed, edit Fortran subroutines and rebuild CCX (menu Job),
- submit job from CAE,
- view job result in GraphiX or export it to post-process in Paraview.

In Windows to work with subroutines and to recompile CalculiX sources from CAE you'll need [cygwin](https://www.cygwin.com/). Install it to 'C:\\cygwin64' with:
- gcc-g++ 7.3.0-3
- gcc-fortran 7.3.0-3
- make 4.2.1-2
- perl 5.26.3-2

**Attention!** Do not move CCX or CGX from 'bin' directory!

<br/><br/>



# Your help

Please, you may:

- Star this project.
- Simply use this software and ask questions.
- Share your models and screenshots.
- Do something from the [TODO-list](#TODO).
- Report problems by [posting issues](https://github.com/calculix/cae/issues). Please, attach ./examples/default.log (or other logs) to the problem report.

<br/><br/>



# For developers

You may also need libraries:

    qttools5-dev-tools
    pycallgraph

<br/><br/>



# What's new

What's new in future v0.9.0:

- CalculiX 2.17.1. Linux version of CGX has 'cmap' command and [custom colormaps](https://github.com/calculix/cgx/releases/tag/v2.17.cmap): classic, viridis, inferno and turbo. Switch colormaps from menu CGX.
- Significantly improved INP importer algorithm. Now parser supports keyword line continuation. Tested on over 20 000 INP files, including Abaqus models.
- New checker module. Checks are called on the application start. OS name, Python version, CAE version and default web browser are logged. Requirements are installed automatically via pip. Statrup checks could be switched off from the settings.
- Refactored logging system. Now it is a new dedicated module.
- Significantly improved window connectivity (master/slave).
- Improved robustness - now almost every module has a test. Test system uses 'unittest' standard library.
- Simplified code to omit redundant arguments passing between objects. Class instances are created directly in modules and imported to any other module.
- Using external python packages *ccx2paraview* and *unv2ccx* as required dependacies.
- Added buttons to select paths in Settings dialog.
- cae.bat and sae.sh - run source code

<br/><br/>



# TODO

Examples and training materials:
- Prool's INP-templates and snippets.
- Interface for [Martin Kraska examples](https://github.com/mkraska/CalculiX-Examples).
- Menu Help: wiki, YouTube videos for beginners. 

Python API:
- Invent some kind of Python API. Possibly use [pycalculix](https://github.com/spacether/pycalculix), [pyccx](https://github.com/drlukeparry/pyccx) and [pycgx](https://github.com/zagl/pycgx). Here are [pycgx examples](https://github.com/zagl/ccx-user).
- Pay attention to [pyvista](https://www.pyvista.org/) and [Python tetgen interface](https://tetgen.pyvista.org/).
- Python code (*PYTHON keyword) in the INP_code for step repetition and other kind of model generation.
- Martin Kraska: support the param.py parametrization mechanism.

FreeCAD:
- Embeded CAE into FreeCAD.
- Connector for FreeCAD: listen to port and obtain meshed geometry.

CGX:
- Master window / toolset with list of CGX commands.
- Highlight loads and boundary conditions.

Parsers:
- Reparse mesh/model after tree.actionDeleteImplementation.
- Parsers for loads and boundary conditions.

Importer:
- treeView: import certain keyword with descendants (tree branch) from INP-file.
- Interface for materials import: right click on *Material -> Import.
- [Meshio converter](https://github.com/nschloe/meshio).
- Import mesh from FRD, [VTK](https://lorensen.github.io/VTKExamples/site/Python/IO/ReadLegacyUnstructuredGrid/), [VTU](https://lorensen.github.io/VTKExamples/site/Python/IO/ReadUnstructuredGrid/), [Gmsh](http://gmsh.info/).
- Open .fbd/.fbl and forward to CGX. Then import generated model.

Other:
- Take binaries for Windows from https://www.meil.pw.edu.pl/add/ADD/Teaching/Software/Calculix
