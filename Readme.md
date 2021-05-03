# What's the point?

Blender gives you the ability to export each channel as separate file. But this is very tedious. You need to define each output manually in the fileoutput node. To improve this procedure I created this simple Addon. 

# Why even bother? Multilayer EXR are so much easier...

Yeah... Kind of. They are extremely slow over networks and are way to big for the inherent content. For example: If you are using the Cryptomatte out of Blender, you need to set the bitdepth to 32bit float. Thus you double the data of each other channel! By exporting single channels as separate files you can safe up to 20 times of the multilayer exr! Check out the demo files in the "render" folder.

# How to install

Download *export_channels.py* and install it through the addon manager of blender. Et voilà: One single click in the output panel of blender and you got the perfect node tree.



# Todo

- [x] Select compression [ Currently each channel is compressed via DWAA (Exept the Cryptomatte)]
- [ ] Subfolders! Let the user decide if he wants to create millions of subfolders!