bl_info = {
    "name": "EXR Singlechannel Exporter",
    "author": "Lukas Wieg",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Output Properties > Single Channel EXR",
    "description": "Creates compositor nodes to export Channels into seperate files",
    "warning": "",
    "doc_url": "",
    "category": "Render",
}

import bpy

class SingleEXRProperties(bpy.types.PropertyGroup):
    """ Stores all Properties  """
    base_path : bpy.props.StringProperty(name="Output Folder",
                                    description="Export location",
                                    default="//render/",
                                    maxlen=1024,
                                    subtype="FILE_PATH") 
                                    
    codecs = [('ZIP','Zip','',0,0),
             ('PIZ','Piz','',0,1),
             ('DWAA','DWAA (Lossy)','',0,2)]
    codec : bpy.props.EnumProperty(items=codecs,
                                    name="Codec",
                                    default='DWAA')
    depths = [('16', 'Float (Half)', ''),
               ('32', 'Float (Full)', '')]
               
    color_depth : bpy.props.EnumProperty(items=depths,
                                         name="Bit depth",
                                         default='16')

class SingleEXRPanel(bpy.types.Panel):
    """Creates a Panel in the output properties window"""
    bl_label = "Single Channel EXR"
    bl_idname = "OUTPUT_PT_SingleEXR"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    
    def draw(self, context):
        layout = self.layout
        prop_group =  context.scene.sEXR
        obj = context.object
        row = layout.row()
        row.prop(prop_group, "base_path")
        row = layout.row()
        row.prop(prop_group, "codec")
        row = layout.row()
        row.prop(prop_group, "color_depth", expand=True)
        row = layout.row()
        row.operator("s_exr.create_nodes", icon='NODETREE')


class position:    
    def __init__(self, x , y):
        self.x = x
        self.y = y
        
        
class CreateNodes(bpy.types.Operator):
    """Creates compositor nodes to export Channels into seperate files"""
    bl_idname = "s_exr.create_nodes"
    bl_label = "Create Node Setup"
 
   
    def execute(self, context):
        # Constants
        BASE_PATH = context.scene.sEXR.base_path
        NAME_TAG = "sEXR_"
        scene = context.scene        
        
        # Enable compositing nodes
        scene.use_nodes = True
        scene.render.use_compositing = True
        node_tree = scene.node_tree


        # Remove older Nodes
        for node in scene.node_tree.nodes:
            if NAME_TAG in node.name:
                scene.node_tree.nodes.remove(node)

                
        for x, layer in enumerate(scene.view_layers):
            pos = position(1000 + x*700, 1000)
            
            frame = node_tree.nodes.new('NodeFrame')
            frame.use_custom_color = True
            frame.color = (0,1,0)
            frame.label = NAME_TAG + layer.name + " File Outputs"
            frame.name = NAME_TAG + layer.name + " File Outputs"
            frame.location = (pos.x, pos.y)

            render_layer = node_tree.nodes.new("CompositorNodeRLayers")
            render_layer.location = (pos.x, pos.y)
            render_layer.label = NAME_TAG + layer.name
            render_layer.name = NAME_TAG + layer.name            
            render_layer.layer = layer.name
            render_layer.parent = frame

            file_output = node_tree.nodes.new("CompositorNodeOutputFile")
            file_output.location = (pos.x + 400, pos.y)
            file_output.label = NAME_TAG + "Write " + layer.name
            file_output.name = NAME_TAG + "Write " + layer.name
            file_output.base_path = BASE_PATH + layer.name + "/"
            file_output.parent = frame

            # Set global filetype
            file_output.format.file_format = 'OPEN_EXR'
            file_output.format.exr_codec =  scene.sEXR.codec
            file_output.format.color_depth =  scene.sEXR.color_depth

            # Add inputs & connect nodes
            active_outputs = []
            file_output.file_slots.remove(file_output.inputs[0])

            for output in render_layer.outputs:
                if output.enabled:
                    
                    input = file_output.file_slots.new(output.name)
                    file_output.file_slots[input.name].use_node_format = False
                    
                    # Set output format
                    format = file_output.file_slots[input.name].format
                    format.file_format = 'OPEN_EXR'
                    format.color_mode = 'RGB'
                    format.color_depth = scene.sEXR.color_depth # '32'
                    format.exr_codec =  scene.sEXR.codec # 'PIZ'
                    
                    # Cryptomattes need 32 bit to work properly 
                    if 'crypto' in input.name.lower():
                        format.color_mode = 'RGBA'
                        format.color_depth = '32'
                        format.exr_codec = 'PIZ'
                    
                    
                    node_tree.links.new(output, input)
                    active_outputs.append(output)
        return {'FINISHED'}

classes =(CreateNodes,
          SingleEXRPanel,
          SingleEXRProperties)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sEXR = bpy.props.PointerProperty(type=SingleEXRProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.sEXR 


if __name__ == "__main__":
    register()
