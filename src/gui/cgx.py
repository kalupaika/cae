#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""© Ihor Mirzov, 2019-2021
Distributed under GNU General Public License v3.0

The module represents CGX menu.
It contains functions for CalculiX GraphiX window.

NOTE paint_elsets_old() is not used.
"""

# Standard modules
import os
import sys
import logging

# My modules
sys_path = os.path.abspath(__file__)
sys_path = os.path.dirname(sys_path)
sys_path = os.path.join(sys_path, '..')
sys_path = os.path.normpath(sys_path)
sys_path = os.path.realpath(sys_path)
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)
from path import p
from gui.window import wf
from model import m


def read_fbd_file(file_name):
    if os.path.isfile(file_name):
        wf.connection.post('read ' + file_name)
    else:
        logging.error('No config file ' + file_name)


def paint_elsets_old(elsets):
    """Paint element sets in default CGX colors."""
    colors = 'rgbymntk'
    i = 0
    for i in range(len(elsets)):
        if elsets[i].upper() == 'ALL':
            elsets.pop(i)
            break
    if len(elsets) > 1:
        for elset in elsets:
            wf.connection.post('plus e {} {}'.format(elset, colors[i]))
            i = (i + 1) % len(colors)


def restart_and_read_fbd(file_name):
    """Open GraphiX and execute FBD."""
    wf.kill_slave() # close old CGX
    cmd = p.path_cgx + ' -b ' + file_name
    wf.run_slave(cmd)


"""Menu CGX."""


def paint_elsets():
    """Paint element sets in CGX when INP is opened."""
    if not (p.path_cgx + ' -c ') in wf.sw.cmd:
        msg = 'Please, open INP model to paint elsets.'
        logging.warning(msg)
        return

    wf.connection.post('plot e all')
    wf.connection.post('minus e all')
    elsets = [e.name for e in m.Mesh.elsets.values()]
    i = 0
    for elset in elsets:
        if elset.upper() == 'ALL':
            continue
        wf.connection.post('plus e {} blue{}'.format(elset, i))
        i = (i + 1) % 5


def paint_surfaces():
    """Paint surfaces in CGX when INP is opened."""
    if not (p.path_cgx + ' -c ') in wf.sw.cmd:
        msg = 'Please, open INP model to paint surfaces.'
        logging.warning(msg)
        return

    wf.connection.post('plot e all')
    wf.connection.post('minus e all')
    surfaces = [s.name for s in m.Mesh.surfaces.values()]
    i = 0
    for surf in surfaces:
        if surf.upper() == 'ALL':
            continue
        wf.connection.post('plus f {} pink{}'.format(surf, i))
        i = (i + 1) % 5


def open_inp(inp_file, has_nodes=0):
    """Open INP model in GraphiX."""
    if not os.path.isfile(p.path_cgx):
        logging.error('CGX not found in ' + p.path_cgx)
        raise SystemExit # the best way to exit

    if os.path.isfile(inp_file):
        wf.kill_slave() # close old CGX
        if not has_nodes:
            logging.warning('Empty mesh, CGX will not start!')
            return
        cmd = p.path_cgx + ' -c ' + inp_file
        wf.run_slave(cmd)
        read_fbd_file(os.path.join(p.config, 'cgx_start.fbd'))
        read_fbd_file(os.path.join(p.config, 'cgx_iso.fbd'))
        read_fbd_file(os.path.join(p.config, 'cgx_colors.fbd'))
    else:
        logging.error('File not found:\n' + inp_file)


def open_frd(frd_file):
    """Open FRD results in GraphiX."""
    if not os.path.isfile(p.path_cgx):
        logging.error('CGX not found in ' + p.path_cgx)
        raise SystemExit # the best way to exit

    if os.path.isfile(frd_file):
        cmd = p.path_cgx + ' -o ' + frd_file
        wf.run_slave(cmd)
        read_fbd_file(os.path.join(p.config, 'cgx_start.fbd'))
        read_fbd_file(os.path.join(p.config, 'cgx_iso.fbd'))
    else:
        logging.error('File not found:\n' \
            + frd_file \
            + '\nSubmit analysis first.')


def cmap(colormap):
    """Set custom colormap when FRD is opened."""
    if not (p.path_cgx + ' -o ') in wf.sw.cmd:
        msg = 'Please, open FRD model to set colormap.'
        logging.warning(msg)
        return
    wf.connection.post('cmap ' + colormap)
