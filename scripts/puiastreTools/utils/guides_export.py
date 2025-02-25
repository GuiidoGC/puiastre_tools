import maya.cmds as cmds
import maya.OpenMaya as om
import os
import json

class GuidesExport():

        def guides_export(self, guides, name):
                self.guides_folder = cmds.ls(guides)
                self.guides_name = name
                if self.guides_folder:
                        self.guides_descendents = cmds.listRelatives(self.guides_folder[0], allDescendents=True, type="joint")
                        if not self.guides_descendents:
                                om.MGlobal.displayError("No guides found in the scene.")
                                return

                        left_guides = []
                        right_guides = []
                        for guide in self.guides_descendents:
                                if guide.split("_")[0] == "L":
                                        left_guides.append(guide)
                                if guide.split("_")[0] == "R":
                                        right_guides.append(guide)
                        for left_guide in left_guides:
                                splited_guide = left_guide.split("_")[1]
                                for right_guide in right_guides:
                                        if splited_guide in right_guide:
                                                left_world_position = [round(coord, 3) for coord in cmds.xform(left_guide, q=True, ws=True, t=True)]
                                                right_world_position = [round(coord, 3) for coord in cmds.xform(right_guide, q=True, ws=True, t=True)]

                                                right_world_position[0] = right_world_position[0] * -1


                                                if left_world_position != right_world_position:
                                                        om.MGlobal.displayWarning(f"Guides are not symmetrical. {right_guide} is not in the same position as {left_guide}.")
                                                        return
                                                      

                        
                        if len(left_guides) != len(right_guides):
                                om.MGlobal.displayWarning("Guides are not symmetrical.")
                                return
                        
                        self.guides_positions = []
                        self.guides_parents = []
                        self.guides_joint_orient = []
                        for position in self.guides_descendents: #Get the position of each guide
                                self.guides_positions.append(cmds.xform(position, t=True, ws=True, query=True))

                        for parent in self.guides_descendents: #Get the parent of each guide
                                self.guides_parents.append(cmds.listRelatives(parent, parent=True)[0])
                        for joint_orient in self.guides_descendents: #Get the joint orient of each guide
                                self.guides_joint_orient.append(cmds.getAttr(f"{joint_orient}.jointOrient"))


                elif len(self.guides_folder) > 1:
                        om.MGlobal.displayError(f"More than one {guides} found in the scene.")
                        return
                else:
                        om.MGlobal.displayError("No guides found in the scene.")
                        return

                self.export_json()

        def export_json(self):

                complete_path = os.path.realpath(__file__)
                script_path = complete_path.replace("\\", "/")
                relative_path = script_path.split("/scripts/puiastreTools/utils/guides_export.py")[0]
                relative_path = relative_path.replace("/", "\\")
                final_path = os.path.join(relative_path, "guides")
                self.guides_data = {self.guides_name: {}}

                for i, guide in enumerate(self.guides_descendents):
                        self.guides_data[self.guides_name][guide] = {
                                "position": self.guides_positions[i],
                                "parent": self.guides_parents[i],
                                "joint_orient": self.guides_joint_orient[i]
                        }

                if not os.path.exists(final_path):
                        os.makedirs(final_path)

                with open(os.path.join(final_path, f'{self.guides_name}.json'), "w") as outfile:
                        json.dump(self.guides_data, outfile, indent=4)

                om.MGlobal.displayInfo(f"Guides data exported to {os.path.join(final_path, f'{self.guides_name}.json')}")


        def guide_import(self, name):

                complete_path = os.path.realpath(__file__)
                script_path = complete_path.replace("\\", "/")
                relative_path = script_path.split("/scripts/puiastreTools/utils/guides_export.py")[0]
                relative_path = relative_path.replace("/", "\\")
                final_path = os.path.join(relative_path, "guides")

                with open(os.path.join(final_path, f'{name}.json'), "r") as infile:
                        self.guides_data = json.load(infile)

                guides_node = cmds.createNode("transform", name="C_guides_GRP")
                
                for joint, data in reversed(list(self.guides_data[name].items())):
                        cmds.select(clear=True)
                        self.imported_joint = cmds.joint(name=joint, position=data["position"])
                        if data["parent"]:
                                cmds.parent(joint, data["parent"])
                                cmds.setAttr(f"{self.imported_joint}.jointOrient", data["joint_orient"][0][0], data["joint_orient"][0][1], data["joint_orient"][0][2])
                        

                                
                cmds.select(clear=True)
                


""" EXECUTE THE CODE IN MAYA SCRIPT EDITOR FOR EXPORTING

from puiastreTools.utils import guides_export
from importlib import reload
reload(guides_export)
guides_export.GuidesExport().guides_export("C_guides_GRP", "azhurean_guides")

"""

""" EXECUTE THE CODE IN MAYA SCRIPT EDITOR FOR IMPORTING

from puiastreTools.utils import guide_import
from importlib import reload
reload(guides_import)
guides_import.GuidesExport().guide_import("azhurean_guides")

"""
