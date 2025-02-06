import sys
import os
import maya.cmds as cmds
from functools import partial
from importlib import reload

def puiastre_ui():

    if cmds.menu("PuiastreMenu", exists=True):
        cmds.deleteUI("PuiastreMenu")
    cmds.menu("PuiastreMenu", label="Puiastre Productions", tearOff=True, parent="MayaWindow")

    cmds.menuItem(divider=True, dividerLabel="Rigging Tools")

    cmds.menuItem(label="Export curves", command="print('WIP')")
    cmds.menuItem( optionBox=True , command="print('HOLA')")

    cmds.menuItem(label="Auto Rig UI", command="print('WIP')", image="puiastreLogo.ico")


    cmds.setParent("..", menu=True)
