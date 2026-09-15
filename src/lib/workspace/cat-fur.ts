import * as THREE from 'three';

/** Diffuse matte coat, without added fur geometry or glossy highlights. */
export function makeCatCoatMatte(model: THREE.Group) {
  model.traverse(object=>{
    const mesh=object as THREE.Mesh;if(!mesh.isMesh)return;
    for(const material of Array.isArray(mesh.material)?mesh.material:[mesh.material]){
      const coat=material as THREE.MeshPhysicalMaterial;
      if(!/calico/i.test(coat.name))continue;
      coat.roughness=1;coat.metalness=0;coat.envMapIntensity=0;
      if(coat.isMeshPhysicalMaterial){coat.specularIntensity=0;coat.sheen=0;coat.clearcoat=0;}
      coat.onBeforeCompile=shader=>{
        shader.fragmentShader=shader.fragmentShader.replace('#include <lights_physical_fragment>',`#include <lights_physical_fragment>
          material.specularColor=vec3(0.0);
          material.specularF90=0.0;
        `);
      };
      coat.customProgramCacheKey=()=> 'cat-matte-coat-v1';coat.needsUpdate=true;
    }
  });
}
