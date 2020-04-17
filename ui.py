# Blender modules
import bpy
from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList,
                       Menu)
from bpy.props import (IntProperty,
                       BoolProperty,
                       EnumProperty,
                       StringProperty,
                       CollectionProperty)

# local module
import AddModifierTools.operators as AMT_OT


# ANCHOR UIList - listtype
class ADD_MODIFIER_TOOLS_UL_listtype(UIList):
    """ Create a UI List """
    def draw_item(self, context, layout, data, item, active_data, active_propname, index):
        modifier = item
        mod_icon_map = AMT_OT.get_modifier_icon_dict()

        layout.label(text=modifier.name, icon=mod_icon_map[modifier.mod_id])


# ANCHOR Menu - add modifier
class ADD_MODIFIER_TOOLS_MT_add_modifier(Menu):
    """ Create a Add modifier menu """
    bl_idname      = "ADD_MODIFIER_TOOLS_MT_add_modifier"
    bl_label       = "Add modifier"

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        mdict = AMT_OT.get_add_modifiers_layout()
        for cat, mods in mdict.items():
            col = split.column()
            col.label(text=cat)
            for _id, name, icon in mods:
                mod = col.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_menu_action.bl_idname, text=name, icon=icon)
                mod.mod_name = name
                mod.mod_id = _id


# ANCHOR PropertyGroup - modifier collection
class ADD_MODIFIER_TOOLS_modifier_collection(PropertyGroup):
    mod_icon: StringProperty()
    mod_id  : StringProperty()


# ANCHOR Custom UI
def draw(self, context):
    layout = self.layout
    scn = bpy.context.scene
    rows = 2

    row = layout.row(align=True)
    row.prop(scn, "show_hideA")
    row.label(text="Modifier Tools")
    row = layout.row()
    if (scn.show_hideA == True):
        row.template_list("ADD_MODIFIER_TOOLS_UL_listtype", "", scn, "amt_modifiers", scn, "modifier_active_index", rows=rows)
        col = row.column(align=True)
        col.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_list_action.bl_idname, text="", icon="ADD").action = "ADD"
        col.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_list_action.bl_idname, text="", icon="REMOVE").action = "REMOVE"
        col.separator()
        col.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_list_action.bl_idname, text="", icon="TRIA_UP").action = "UP"
        col.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_list_action.bl_idname, text="", icon="TRIA_DOWN").action = "DOWN"

        row = layout.row()
        col = row.column(align=True)
        row = col.row(align=True)
        row.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_multiple_additional.bl_idname, text="Multiple Additional")
        row = col.row(align=True)
        row.prop(scn, "show_hideB")
        row.label(text="Modifier Operator")
        row = col.row(align=True)
        if (scn.show_hideB == True):
            row.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_apply_all.bl_idname, text="Apply All")
            row.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_delete_all.bl_idname, text="Delete All")
            row = col.row(align=True)
            row.operator(AMT_OT.ADD_MODIFIER_TOOLS_OT_expand_collapse.bl_idname, text="Expand/Collapse")
        else:
            pass

        layout.separator()
    else:
        pass


# ANCHOR Classes List
classes = (
    # Menu
    ADD_MODIFIER_TOOLS_MT_add_modifier,
    # UI List
    ADD_MODIFIER_TOOLS_UL_listtype,
    # PropertyGroup
    ADD_MODIFIER_TOOLS_modifier_collection,
)


# ANCHOR Register
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom properties
    bpy.types.Scene.amt_modifiers = CollectionProperty(type=ADD_MODIFIER_TOOLS_modifier_collection)
    bpy.types.Scene.modifier_active_index = IntProperty()
    bpy.types.Scene.show_hideA = BoolProperty(name="" ,default=True)
    bpy.types.Scene.show_hideB = BoolProperty(name="" ,default=False)

    # Add Custom UI to the "Modifiers" menu
    bpy.types.DATA_PT_modifiers.prepend(draw)


# ANCHOR Unregister
def unregister():
    # Remove Custom UI to the "Modifiers" menu
    bpy.types.DATA_PT_modifiers.remove(draw)

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    # Custom properties
    del bpy.types.Scene.amt_modifiers
    del bpy.types.Scene.modifier_active_index
    del bpy.types.Scene.show_hideA
    del bpy.types.Scene.show_hideB


if __name__ == "__main__":
    register()
