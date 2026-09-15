"""World-scaled, face-projected UVs for shared seamless surface-detail maps."""
def ensure_detail_uv(obj):
    if obj.type!='MESH' or not any(m and m.get('matteDetail') for m in obj.data.materials):
        return
    mesh=obj.data
    if mesh.uv_layers.get('SurfaceDetail'):
        return
    if not mesh.uv_layers:
        mesh.uv_layers.new(name='SourceUV')
    detail=mesh.uv_layers.new(name='SurfaceDetail')
    normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
    for face in mesh.polygons:
        normal=normal_matrix@face.normal
        axis=max(range(3),key=lambda i:abs(normal[i]))
        axes=[i for i in range(3) if i!=axis]
        material=mesh.materials[face.material_index] if len(mesh.materials)>face.material_index else None
        density=material.get('detailDensity',10) if material else 10
        for loop_index in face.loop_indices:
            p=obj.matrix_world@mesh.vertices[mesh.loops[loop_index].vertex_index].co
            detail.data[loop_index].uv=(p[axes[0]]*density,p[axes[1]]*density)
    mesh.uv_layers.active_index=0
