import maya.cmds as cmds
import puiastreTools.tools.curve_tool as curve_tool
from puiastreTools.utils import guides_manager
from puiastreTools.utils import data_export
from importlib import reload
reload(guides_manager)

class jawModule():

    def __init__(self):

        self.data_exporter = data_export.DataExport()

        self.modules_grp = self.data_exporter.get_data("basic_structure", "modules_GRP")
        self.skel_grp = self.data_exporter.get_data("basic_structure", "skel_GRP")
        self.masterWalk_ctl = self.data_exporter.get_data("basic_structure", "masterWalk_CTL")
        self.head_ctl = self.data_exporter.get_data("C_neckModule", "head_ctl")

    def local(self, ctl, grp, jnt_skinning):

        """
        This function sets the local space for a controller and its group.
        It connects the controller's worldMatrix to the group's offsetParentMatrix.
        """
        mult_matrix = cmds.createNode("multMatrix", n=ctl.replace("CTL", "MMX"), ss=True)
        cmds.connectAttr(f"{ctl}.worldMatrix[0]", f"{mult_matrix}.matrixIn[0]")
        cmds.connectAttr(f"{grp}.worldInverseMatrix[0]", f"{mult_matrix}.matrixIn[1]")
        trn_local = cmds.createNode("transform", n=ctl.replace("_CTL", "Local_TRN"), ss=True)
        cmds.matchTransform(trn_local, grp, pos=True, rot=True, scl=True)
        cmds.parent(trn_local, self.module_trn)
        cmds.connectAttr(f"{mult_matrix}.matrixSum", f"{trn_local}.offsetParentMatrix")
        cmds.connectAttr(f"{trn_local}.worldMatrix[0]", f"{jnt_skinning}.offsetParentMatrix")
    
    def lock_attrs(self, ctl):

        for attr in ["sx", "sy", "sz", "v"]:
            cmds.setAttr(f"{ctl}.{attr}", lock=True, keyable=False, channelBox=False)

    def make(self):

        side = "C"


        self.module_trn = cmds.createNode("transform", n=f"{side}_jawModule_GRP", p=self.modules_grp)
        self.skinning_trn = cmds.createNode("transform", n=f"{side}_jawSkinningJoints_GRP", p=self.skel_grp)


        jaw_jnts = guides_manager.guide_import(joint_name=f"{side}_jaw_JNT", all_descendents=True)
        cmds.parent(jaw_jnts, self.module_trn)

        jaw_jnt = jaw_jnts[0]
        jaw_jnt_end = jaw_jnts[-1]
        ctl = curve_tool.controller_creator

        jaw_skinning_jnt = cmds.createNode("joint", n=f"{side}_jawSkinning_JNT", p=self.skinning_trn)
        upper_jaw_skinning_jnt = cmds.createNode("joint", n=f"{side}_upperJawSkinning_JNT", p=self.skinning_trn)
        chin_skinning_jnt = cmds.createNode("joint", n=f"{side}_chinSkinning_JNT", p=self.skinning_trn)

        jaw_curve_ctl, jaw_curve_grp = ctl(side+"_jaw", ["GRP"])
        self.lock_attrs(jaw_curve_ctl)
        cmds.matchTransform(jaw_curve_grp[0], jaw_jnt, pos=True)
        self.local(jaw_curve_ctl, jaw_curve_grp[0], jaw_skinning_jnt)
        cmds.addAttr(jaw_curve_ctl, ln="EXTRA_ATTRIBUTES", at="enum", en="___:", k=True)
        cmds.setAttr(f"{jaw_curve_ctl}.EXTRA_ATTRIBUTES", lock=True)
        cmds.addAttr(jaw_curve_ctl, ln="Collision", min=0, max=1, dv=1, k=True, at="float")

        upper_jaw_curve_ctl, upper_jaw_curve_grp = ctl(f"{side}_upperJaw", ["GRP", "OFF"])
        self.lock_attrs(upper_jaw_curve_ctl)
        cmds.matchTransform(upper_jaw_curve_grp, jaw_jnt, pos=True)
        self.local(upper_jaw_curve_ctl, upper_jaw_curve_grp[0], upper_jaw_skinning_jnt)

        chin_curve_ctl, chin_curve_grp = ctl(f"{side}_chin", ["GRP"])
        self.lock_attrs(chin_curve_ctl)
        cmds.matchTransform(chin_curve_grp[0], jaw_jnt_end, pos=True)
        self.local(chin_curve_ctl, chin_curve_grp[0], chin_skinning_jnt)
        cmds.parent(chin_curve_grp[0], jaw_curve_ctl)

        #Collsion set-up
        upper_jaw_mmx = cmds.createNode("multMatrix", n=f"{side}upperJaw_MMX", ss=True)
        cmds.connectAttr(f"{upper_jaw_curve_ctl}.matrix", f"{upper_jaw_mmx}.matrixIn[0]")
        cmds.connectAttr(f"{upper_jaw_curve_grp[-1]}.matrix", f"{upper_jaw_mmx}.matrixIn[1]")
        upper_jaw_dcm = cmds.createNode("decomposeMatrix", n=f"{side}upperJaw_DCM", ss=True)
        cmds.connectAttr(f"{upper_jaw_mmx}.matrixSum", f"{upper_jaw_dcm}.inputMatrix")

        jaw_mmx = cmds.createNode("multMatrix", n=f"{side}jaw_MMX", ss=True)
        cmds.connectAttr(f"{jaw_curve_ctl}.matrix", f"{jaw_mmx}.matrixIn[0]")
        cmds.connectAttr(f"{jaw_curve_grp[-1]}.matrix", f"{jaw_mmx}.matrixIn[1]")
        jaw_dcm = cmds.createNode("decomposeMatrix", n=f"{side}jaw_DCM", ss=True)
        cmds.connectAttr(f"{jaw_mmx}.matrixSum", f"{jaw_dcm}.inputMatrix")

        

        union_pma = cmds.createNode("plusMinusAverage", n=f"{side}union_PMA", ss=True)
        cmds.setAttr(f"{union_pma}.operation", 2)
        cmds.connectAttr(f"{jaw_dcm}.outputRotateX", f"{union_pma}.input1D[0]")
        cmds.connectAttr(f"{upper_jaw_dcm}.outputRotateX", f"{union_pma}.input1D[1]")
        clamp = cmds.createNode("clamp", n=f"{side}jaw_CLP", ss=True)
        cmds.setAttr(f"{clamp}.minR", -360)
        cmds.connectAttr(f"{union_pma}.output1D", f"{clamp}.inputR")
        cmds.connectAttr(f"{upper_jaw_dcm}.outputRotateX", f"{clamp}.maxR")
        floatC = cmds.createNode("floatConstant", n=f"{side}jaw_FLT", ss=True)
        cmds.setAttr(f"{floatC}.inFloat", 0)
        blend_attrs= cmds.createNode("blendTwoAttr", n=f"{side}jaw_BTA", ss=True)
        cmds.connectAttr(f"{floatC}.outFloat", f"{blend_attrs}.input[0]")
        cmds.connectAttr(f"{clamp}.outputR", f"{blend_attrs}.input[1]")
        cmds.connectAttr(f"{jaw_curve_ctl}.Collision", f"{blend_attrs}.attributesBlender")
        cmds.connectAttr(f"{blend_attrs}.output", f"{upper_jaw_curve_grp[-1]}.rotateX")

        if "C_head_CTL" in cmds.ls():
            cmds.parent(jaw_curve_grp[0], "C_head_CTL")
            cmds.parent(upper_jaw_curve_grp[0], "C_head_CTL")
        elif "C_masterWalk_CTL" in cmds.ls():
            cmds.parent(jaw_curve_grp[0], "C_masterWalk_CTL")
            cmds.parent(upper_jaw_curve_grp[0], "C_masterWalk_CTL")


