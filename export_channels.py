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
#scene = bpy.context.scene
#node_tree = scene.node_tree

class SingleEXRPanel(bpy.types.Panel):
    """Creates a Panel in the output properties window"""
    bl_label = "Single Channel EXR"
    bl_idname = "OUTPUT_PT_SingleEXR"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    
    def draw(self, context):
        layout = self.layout

        obj = context.object
        row = layout.row()
        row.prop(context.scene, "sEXR_base_path")
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
        BASE_PATH = context.scene.sEXR_base_path
        NAME_TAG = "sEXR_"
        scene = context.scene        

        # Enable compositing nodes
        scene.use_nodes = True
        scene.render.use_compositing = True


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
                    format.color_depth = '16' # '32'
                    format.exr_codec = 'DWAA' # 'PIZ'
                    
                    # Cryptomattes need 32 bit to work properly 
                    if 'crypto' in input.name.lower():
                        format.color_mode = 'RGBA'
                        format.color_depth = '32'
                        format.exr_codec = 'PIZ'
                    
                    
                    node_tree.links.new(output, input)
                    active_outputs.append(output)
        return {'FINISHED'}

classes =(CreateNodes,
            SingleEXRPanel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sEXR_base_path = bpy.props.StringProperty(name="Output Folder",
                                    description="Export location",
                                    default="//render/",
                                    maxlen=1024,
                                    subtype="FILE_PATH") 

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()