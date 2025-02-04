﻿# Copyright (c) 2017 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import copy
import pprint
import maya.cmds as cmds
import maya.mel as mel
from pxr import Kind, Sdf, Usd, UsdGeom
import sgtk
from tank_vendor import six

HookBaseClass = sgtk.get_hook_baseclass()


class MayaSessionPreScriptPublishPlugin(HookBaseClass):
    """
    Plugin for publishing an open maya session.

    This hook relies on functionality found in the base file publisher hook in
    the publish2 app and should inherit from it in the configuration. The hook
    setting for this plugin should look something like this::

        hook: "{self}/publish_file.py:{engine}/tk-multi-publish2/basic/publish_session.py"

    """

    # NOTE: The plugin icon and name are defined by the base file plugin.

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """
        <p>This plugin publishes session geometry for the current session. Any
        session geometry will be exported to the path defined by this plugin's
        configured "Publish Template" setting. The plugin will fail to validate
        if the "AbcExport" plugin is not enabled or cannot be found.</p>
        """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to receive
        through the settings parameter in the accept, validate, publish and
        finalize methods.

        A dictionary on the following form::

            {
                "Settings Name": {
                    "type": "settings_type",
                    "default": "default_value",
                    "description": "One line description of the setting"
            }

        The type string should be one of the data types that toolkit accepts as
        part of its environment configuration.
        """
        # inherit the settings from the base publish plugin
        base_settings = super(MayaSessionPreScriptPublishPlugin, self).settings or {}

        # settings specific to this class
        maya_publish_settings = {
            "Publish Template": {
                "type": "template",
                "default": None,
                "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            }
        }

        # update the base settings
        base_settings.update(maya_publish_settings)


        file_type = {
            "File Types": {
                "type": "list",
                "default": [
                    ["Pre Script", "script"],
                ],
                "description": (
                    "List of file types to include. Each entry in the list "
                    "is a list in which the first entry is the Shotgun "
                    "published file type and subsequent entries are file "
                    "extensions that should be associated."
                )
            },
        }

        base_settings.update(file_type)
        
        return base_settings

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """
        return ["maya.session.component.pre_script"]

    def accept(self, settings, item):
        """
        Method called by the publisher to determine if an item is of any
        interest to this plugin. Only items matching the filters defined via the
        item_filters property will be presented to this method.

        A publish task will be generated for each item accepted here. Returns a
        dictionary with the following booleans:

            - accepted: Indicates if the plugin is interested in this value at
                all. Required.
            - enabled: If True, the plugin will be enabled in the UI, otherwise
                it will be disabled. Optional, True by default.
            - visible: If True, the plugin will be visible in the UI, otherwise
                it will be hidden. Optional, True by default.
            - checked: If True, the plugin will be checked in the UI, otherwise
                it will be unchecked. Optional, True by default.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process

        :returns: dictionary with boolean keys accepted, required and enabled
        """

        accepted = True
        publisher = self.parent
        template_name = settings["Publish Template"].value

        # ensure a work file template is available on the parent item
        work_template = item.parent.properties.get("work_template")
        if not work_template:
            self.logger.debug(
                "A work template is required for the session item in order to "
                "publish session geometry. Not accepting session geom item."
            )
            accepted = False

        # ensure the publish template is defined and valid and that we also have
        publish_template = publisher.get_template_by_name(template_name)
        if not publish_template:
            self.logger.debug(
                "The valid publish template could not be determined for the "
                "session geometry item. Not accepting the item."
            )
            accepted = False

        # we've validated the publish template. add it to the item properties
        # for use in subsequent methods
        item.properties["publish_template"] = publish_template


        # because a publish template is configured, disable context change. This
        # is a temporary measure until the publisher handles context switching
        # natively.
        item.context_change_allowed = False
        return {
            "accepted": accepted,
            "checked": True
        }

    def validate(self, settings, item):
        """
        Validates the given item to check that it is ok to publish. Returns a
        boolean to indicate validity.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        :returns: True if item is valid, False otherwise.
        """
        #return True 
        #return super(MayaSessionPreScriptPublishPlugin, self).validate(
        #    settings, item)


        path = _session_path()
        
        

        # ---- ensure the session has been saved

        if not path:
            # the session still requires saving. provide a save button.
            # validation fails.
            error_msg = "The Maya session has not been saved."
            self.logger.error(
                error_msg,
                extra=_get_save_as_action()
            )
            raise Exception(error_msg)

        # get the normalized path

        #path = sgtk.util.ShotgunPath.normalize(path)

        path = '' 

        check_component = cmds.ls(item.context.entity['name'])

        if not check_component or not len(check_component) == 1:
            error_msg = "Componen is not."
            self.logger.error(
                error_msg,
            )
            raise Exception(error_msg)


        # get the configured work file template
#        work_template = item.parent.properties.get("work_template")
#        publish_template = item.properties.get("publish_template")

        work_template = ''
        publish_template = ''

        # get the current scene path and extract fields from it using the work
        # template:
#        work_fields = work_template.get_fields(path)

        # ensure the fields work for the publish template
#        missing_keys = publish_template.missing_keys(work_fields)
#        if missing_keys:
#            error_msg = "Work file '%s' missing keys required for the " \
#                        "publish template: %s" % (path, missing_keys)
#            self.logger.error(error_msg)
#            raise Exception(error_msg)

        # create the publish path by applying the fields. store it in the item's
        # properties. This is the path we'll create and then publish in the base
        # publish plugin. Also set the publish_path to be explicit.
        #item.properties["path"] = publish_template.apply_fields(work_fields)
        #item.properties["publish_path"] = item.properties["path"]
        item.properties["path"] = ''
        item.properties["publish_path"] = ''


        # use the work file's version number when publishing
#        if "version" in work_fields:
#            item.properties["publish_version"] = 1
            #item.properties["publish_version"] = work_fields["version"]

        # run the base class validation
        return True
        return super(MayaSessionPreScriptPublishPlugin, self).validate(
            settings, item)

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        if item.context.step['name'] == 'model' :
            path = _session_path()

            import re
            ver = 'v' + re.search('(?<=_v)\d{2,3}' , path ).group() if re.search('(?<=_v)\d{2,3}' , path ) else ''
            
            sh_list = cmds.ls(type='mesh')
            for sh in sh_list:
                if not cmds.objExists('%s.version'%sh):
                    cmds.addAttr(sh, ln='version', dt='string')
                    
                cmds.setAttr('%s.version'%sh, ver, type='string')

        print( '+' * 50 )
        print( '[ Shape Version ] ' , ver )
        print( '--- item ----' )
        print( item )
        print( item.context.step['name'] ) 
        print( '+' * 50 )

        return True

    def finalize( self , settings, item ):
        return True

#    def _get_relatives_path(self,publish_path,asset_usd_path):
#        common_prefix = os.path.commonprefix([os.path.dirname(publish_path),asset_usd_path])
#        return os.path.relpath(asset_usd_path, common_prefix)
    
#    def _return_order_node_list(self,node_list):
#        
#        return_list = []
#
#        parents = list(set([cmds.listRelatives(x,p=1,f=1)[0] for x in node_list if cmds.listRelatives(x,p=1)])) 
#        for parent in parents:
#            nodes = cmds.listRelatives(parent,c=1,f=1)
#            nodes.reverse()
#            return_list.extend(nodes)
#            #return_list.extend(cmds.listRelatives(parent,c=1,f=1))
#        
#        return return_list
        
    
#    def _get_sub_component_path(self,sub_component,item):
#        path = os.path.splitext(item.properties["path"])[0]
#        path = os.path.join(path,sub_component.replace("|","_")+'.usd')
#        
#        return path

#    def _set_xform(self,node,prim):
#
#        translate = cmds.xform(node,q=1,t=1)
#        rotate = cmds.xform(node,q=1,ro=1)
#        scale = cmds.xform(node,q=1,s=1)
#
#        xformAPI = UsdGeom.XformCommonAPI(prim)
#        xformAPI.SetTranslate(translate)
#        xformAPI.SetRotate(rotate)
#        xformAPI.SetScale(scale)
       

#    def _append_mesh_attr_usd(self):
#        import sys
#        from collections import OrderedDict
#        import json
#        try:
#            meshes = cmds.ls(typ="mesh")
#            for mesh in meshes:
#
#
#                mesh_attributes = OrderedDict()
#                if cmds.listAttr(mesh,ud=1):
#                    for meshTag in cmds.listAttr(mesh, ud=True):
#                        if meshTag in  ["Meshtype","USD_UserExportedAttributesJson"] :
#                            continue
#                        elif meshTag in ["MtlTag","Doubleside","Subdivision","Displace"]:
#                            mesh_attributes[meshTag] = cmds.getAttr("%s.%s" % (mesh, meshTag), asString=True)
#            
#                    if mesh_attributes:
#                        if cmds.attributeQuery("USD_UserExportedAttributesJson", node = mesh, exists=True):
#                            cmds.setAttr(mesh + ".USD_UserExportedAttributesJson", l=False)
#                        else:
#                            cmds.addAttr(mesh,ln="USD_UserExportedAttributesJson",dt="string")
#                        usd_attr = json.dumps(mesh_attributes, ensure_ascii=False, indent=4)
#                        cmds.setAttr(mesh + ".USD_UserExportedAttributesJson", usd_attr, type="string")
#                        cmds.setAttr(mesh + ".USD_UserExportedAttributesJson", l=True)
#        except Exception as e:
#            _, _ , tb = sys.exc_info() 
#            print ('file name = ', __file__ )
#            print ('error line No = {}'.format(tb.tb_lineno))
#            print (e)
#            raise Exception("Failed to atnt mesh tag  <br> Detail :%s"%e)





#def _find_scene_animation_range():
#    """
#    Find the animation range from the current scene.
#    """
#    # look for any animation in the scene:
#    animation_curves = cmds.ls(typ="animCurve")
#
#    # if there aren't any animation curves then just return
#    # a single frame:
#    if not animation_curves:
#        return 1, 1
#
#    # something in the scene is animated so return the
#    # current timeline.  This could be extended if needed
#    # to calculate the frame range of the animated curves.
#    start = int(cmds.playbackOptions(q=True, min=True))
#    end = int(cmds.playbackOptions(q=True, max=True))
#
#    return start, end


def _session_path():
    """
    Return the path to the current session
    :return:
    """
    path = cmds.file(query=True, sn=True)

    if path is not None:
        path = six.ensure_str(path)

    return path


def _get_save_as_action():
    """
    Simple helper for returning a log action dict for saving the session
    """

    engine = sgtk.platform.current_engine()

    # default save callback
    callback = cmds.SaveScene

    # if workfiles2 is configured, use that for file save
    if "tk-multi-workfiles2" in engine.apps:
        app = engine.apps["tk-multi-workfiles2"]
        if hasattr(app, "show_file_save_dlg"):
            callback = app.show_file_save_dlg

    return {
        "action_button": {
            "label": "Save As...",
            "tooltip": "Save the current session",
            "callback": callback
        }
    }
