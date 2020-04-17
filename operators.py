# Blender modules
import bpy
from bpy.types import Operator
from bpy.props import (IntProperty,
                       BoolProperty,
                       EnumProperty,
                       StringProperty,
                       CollectionProperty)


# ANCHOR Function - Get selected objects
def get_selected_objects():
    """ Get selected objects name to list """
    obj_list = []
    sel_obj = bpy.context.selected_objects
    for i in sel_obj:
        obj_list.append(i.name)
    return obj_list


# ANCHOR Function - Add modifier for object
def add_modifer_for_object(obj="", mod=""):
    """ Add modifier for object """
    if obj:
        obj_data = bpy.data.objects[obj]
        if mod:
            obj_data.modifiers.new("", mod)


# ANCHOR Function - Check mode for object
def check_mode_for_object(obj=""):
    """ Check mode for object """
    if obj:
        obj_data = bpy.data.objects[obj]
        mode = obj_data.mode
        if mode == "EDIT":
            return False
        elif mode == "OBJECT":
            return True


# ANCHOR Function - Apply modifier for object
def apply_modifiers_for_object(obj=""):
    """ Apply modifiers for object """
    if obj:
        obj_data = bpy.data.objects[obj]

        # Copying context for the operator's override
        override = bpy.context.copy()
        override["object"] = obj_data

        mod_list = obj_data.modifiers
        if len(mod_list) > 0:
            for mod in mod_list:
                override["modifier"] = mod
                bpy.ops.object.modifier_apply(override,
                                              apply_as="DATA",
                                              modifier=override["modifier"].name)


# ANCHOR Function - Delete modifier for object
def delete_modifiers_for_object(obj=""):
    """ Delete modifier for object """
    if obj:
        obj_data = bpy.data.objects[obj]
        mod_list = obj_data.modifiers
        if len(mod_list) > 0:
            for mod in mod_list:
                obj_data.modifiers.remove(mod)


# ANCHOR Function - Set expand collapse modifiers
def set_expand_collapse_modifiers(obj=""):
    """ Set expand collapse modifiers """
    if obj:
        obj_data = bpy.data.objects[obj]
        vs = 0
        for mod in obj_data.modifiers:
            if (mod.show_expanded):
                vs += 1
            else:
                vs -= 1
        is_colse = False
        if (0 < vs):
            is_colse = True
        for mod in obj_data.modifiers:
            mod.show_expanded = not is_colse


# ANCHOR Function - Get modifier icon
def get_modifier_icon_dict():
    """ Get modifier icon dict """
    return {m.identifier : m.icon for m in bpy.types.Modifier.bl_rna.properties["type"].enum_items}


# ANCHOR Function - Get modifier layout
# https://blenderartists.org/t/how-to-rebuild-the-add-modifier-menu-layout/1204906/2 By iceythe
def get_add_modifiers_layout():
    """ Get add modifier layout dict """
    # Categories start on these modifiers
    mods = ("DATA_TRANSFER", "ARRAY", "ARMATURE", "CLOTH")

    # Rna enum items are listed in same order as menu
    op = bpy.ops.object.modifier_add
    rna_enum = op.get_rna_type().properties["type"].enum_items
    mod_dict = {"Modify": [], "Generate": [], "Deform": [], "Simulate": []}

    for item, cat in zip(mods, mod_dict):
        for mod in rna_enum[rna_enum.find(item):]:
            mod_id = mod.identifier
            # Delimit at next item in mods
            if mod_id != item and mod_id in mods[mods.index(item):]:
                break
            mod_dict[cat].append((mod_id, mod.name, mod.icon))

    # There's an invalid entry called Surface at the end of "Simulate"
    # category. It's a duplicate of Simple Deform so we remove it.
    if mod_dict["Simulate"] and mod_dict["Simulate"][-1][0] == "SURFACE":
        del mod_dict["Simulate"][-1]
    return mod_dict


# ANCHOR Operator - apply all modifiers
class ADD_MODIFIER_TOOLS_OT_apply_all(Operator):
    """ Apply All Modifiers Operator """
    bl_idname  = "add_modifier_tools.apply_all_modifiers"
    bl_label   = "Apply All Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        if (len(context.selected_objects) > 0):
            sel_objs = get_selected_objects()
            for obj in sel_objs:
                obj_mode = check_mode_for_object(obj)
                if not obj_mode:
                    self.report({"INFO"}, F"Modifiers cannot be applied in edit mode the {obj}.")
                    return {"CANCELLED"}
                else:
                    try:
                        apply_modifiers_for_object(obj)
                    except:
                        self.report({"INFO"}, "Failed to apply all modifiers.")

        for area in context.screen.areas:
            area.tag_redraw()

        return {"FINISHED"}


# ANCHOR Operator - delete all modifiers
class ADD_MODIFIER_TOOLS_OT_delete_all(Operator):
    """ Delete All Modifiers Operator """
    bl_idname  = "add_modifier_tools.delete_all_modifiers"
    bl_label   = "Delete All Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if (len(context.selected_objects) > 0):
            sel_objs = get_selected_objects()
            for obj in sel_objs:
                try:
                    delete_modifiers_for_object(obj)
                except:
                    self.report({"INFO"}, "Failed to delete all modifiers.")

        for area in context.screen.areas:
            area.tag_redraw()

        return {"FINISHED"}


# ANCHOR Operator - expand/collapse modifiers
class ADD_MODIFIER_TOOLS_OT_expand_collapse(Operator):
    """ Expand/Collapse Modifiers Operator """
    bl_idname  = "add_modifier_tools.expand_collapse_modifiers"
    bl_label   = "Expand/Collapse Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if (len(context.selected_objects) > 0):
            sel_objs = get_selected_objects()
            for obj in sel_objs:
                set_expand_collapse_modifiers(obj)
        else:
            self.report({"INFO"}, "No modifiers to Expand/Collapse")
            return {"CANCELLED"}
        
        for area in context.screen.areas:
            area.tag_redraw()

        return {"FINISHED"}


# ANCHOR Operator - multiple additional
class ADD_MODIFIER_TOOLS_OT_multiple_additional(Operator):
    """ Multiple Additional Modifiers Operator """
    bl_idname      = "add_modifier_tools.multiple_additional_modifiers"
    bl_label       = "Multiple Additional Modifiers"
    bl_options     = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        mod_list = []
        scn = context.scene
        mod = scn.amt_modifiers
        for i in mod.items():
            mod_list.append(i[1].mod_id)

        if (len(context.selected_objects) > 0):
            sel_objs = get_selected_objects()
            for mod in mod_list:
                for i in sel_objs:
                    add_modifer_for_object(i, mod)
        else:
            self.report({"INFO"}, "No selected to objects")
            return {"CANCELLED"}

        for area in context.screen.areas:
            area.tag_redraw()

        return {"FINISHED"}


# ANCHOR Operator - list action
class ADD_MODIFIER_TOOLS_OT_list_action(Operator):
    """ UI List actions Operator """
    bl_idname      = "add_modifier_tools.list_action"
    bl_label       = "List Actions"
    bl_options     = {'REGISTER'}

    action: EnumProperty(
        items=(
            ("UP"    , "Up"    , ""),
            ("DOWN"  , "Down"  , ""),
            ("REMOVE", "Remove", ""),
            ("ADD"   , "Add"   , "")
        )
    )

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.modifier_active_index

        try:
            mod = scn.amt_modifiers[idx]
        except IndexError:
            pass
        else:
            if self.action == "DOWN" and idx < len(scn.amt_modifiers) - 1:
                mod_next = scn.amt_modifiers[idx+1].name
                scn.amt_modifiers.move(idx, idx+1)
                scn.modifier_active_index += 1
            elif self.action == "UP" and idx >= 1:
                mod_prev = scn.amt_modifiers[idx-1].name
                scn.amt_modifiers.move(idx, idx-1)
                scn.modifier_active_index -= 1
            elif self.action == "REMOVE":
                scn.amt_modifiers.remove(idx)
                scn.modifier_active_index -= 1

        if self.action == "ADD":
            bpy.ops.wm.call_menu(name="ADD_MODIFIER_TOOLS_MT_add_modifier")

        return {"FINISHED"}


# ANCHOR Operator - menu action
class ADD_MODIFIER_TOOLS_OT_menu_action(Operator):
    """ Menu actions Operator """
    bl_idname      = "add_modifier_tools.menu_action"
    bl_label       = "Menu Actions"
    bl_options     = {"REGISTER"}

    mod_name: StringProperty()
    mod_id:   StringProperty()

    def execute(self, context):
        scn = context.scene
        item = scn.amt_modifiers.add()
        item.name = self.mod_name
        item.mod_id = self.mod_id
        scn.modifier_active_index = len(scn.amt_modifiers)-1

        for area in context.screen.areas:
            area.tag_redraw()

        return {"FINISHED"}


# ANCHOR Classes List
classes = (
    ADD_MODIFIER_TOOLS_OT_apply_all,
    ADD_MODIFIER_TOOLS_OT_delete_all,
    ADD_MODIFIER_TOOLS_OT_expand_collapse,
    ADD_MODIFIER_TOOLS_OT_multiple_additional,
    ADD_MODIFIER_TOOLS_OT_list_action,
    ADD_MODIFIER_TOOLS_OT_menu_action,
)


# ANCHOR Register
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


# ANCHOR Unregister
def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)


if __name__ == "__main__":
    register()
