"""Contact-led feline jump poses, baked on the original deformation skeleton.

Rows in cat-motion.json are time, compression, pitch, fore reach/lift, hind
reach/lift. Foot targets remain planted during preparation and cushioning.
"""
import math
from mathutils import Matrix, Vector


def jump_frames(rig, standing, motion, fps=60):
    def parameters(time):
        keys=motion['poses']
        for a,b in zip(keys,keys[1:]):
            if time<=b[0]:
                t=max(0,min(1,(time-a[0])/(b[0]-a[0])))
                t=t*t*(3-2*t)
                return [x+(y-x)*t for x,y in zip(a[1:],b[1:])]
        return keys[-1][1:]

    def segment(name,a,b):
        old=standing[name]
        axis=old.to_3x3()@Vector((0,1,0))
        rotation=axis.rotation_difference((b-a).normalized())@old.to_quaternion()
        # The IK solution below retains bone lengths. Only the short ankle adapts.
        return Matrix.LocRotScale(a,rotation,Vector((1,(b-a).length/rig.pose.bones[name].length,1)))

    frames=[]
    for f in range(round(motion['seconds']*fps)+1):
        time=f/fps
        crouch,pitch,fore_reach,fore_lift,hind_reach,hind_lift=parameters(time)
        pitch=math.radians(pitch)
        pivot=Vector((0,.5,.3))
        tilt=Matrix.Translation(pivot)@Matrix.Rotation(-pitch,4,'X')@Matrix.Translation(-pivot)
        shift=Matrix.Translation((0,.12*crouch,-1.25*crouch))
        torso=shift@tilt
        frame={name:torso@m for name,m in standing.items()}
        # Keep the gaze comparatively level as the back rotates.
        head=frame['Head'].translation
        head_delta=Matrix.Translation(head)@Matrix.Rotation(pitch*.55,4,'X')@Matrix.Translation(-head)
        for p in [rig.pose.bones['Head']]+list(rig.pose.bones['Head'].children_recursive):
            frame[p.name]=head_delta@frame[p.name]
        # Tail trails the push and counterbalances the landing, rather than
        # remaining a rigid vertical pole above the back.
        tail_base=frame['Tail'].translation
        tail_sweep=math.radians(45)*math.sin(math.pi*min(1,time/motion['seconds']))
        tail_delta=Matrix.Translation(tail_base)@Matrix.Rotation(-tail_sweep,4,'X')@Matrix.Translation(-tail_base)
        for p in [rig.pose.bones['Tail']]+list(rig.pose.bones['Tail'].children_recursive):
            frame[p.name]=tail_delta@frame[p.name]
        for side in ['L','R']:
            for front in [True,False]:
                upper=('Thigh_front_' if front else 'Thigh_Back_')+side
                lower=('Calf_Front_' if front else 'Calf_back_')+side
                ankle=('Foot_front_L2' if side=='L' else 'Foot_front_L2.002') if front else 'Foot_Back_'+side
                paw='Foot_front_'+side if front else ('Foot_Back_L2' if side=='L' else 'Foot_Back_L2.002')
                lift=fore_lift if front else hind_lift
                reach=fore_reach if front else hind_reach
                target=standing[paw].translation+Vector((0,-reach,lift))
                hip=frame[upper].translation
                # Preserve the original ankle-to-paw vector for stable, flat contact.
                wrist=target+(standing[ankle].translation-standing[paw].translation)
                a=rig.pose.bones[upper].length
                b=rig.pose.bones[lower].length
                direction=wrist-hip
                distance=max(.05,min(direction.length,a+b-.005))
                axis=direction.normalized()
                pole=torso.to_3x3()@Vector((0,1 if front else -1,0))
                bend=(pole-axis*pole.dot(axis)).normalized()
                along=(a*a-b*b+distance*distance)/(2*distance)
                height=math.sqrt(max(.001,a*a-along*along))
                knee=hip+axis*along+bend*height
                # Clamp excessive targets rather than stretching thighs and shins.
                wrist=hip+axis*distance
                frame[upper]=segment(upper,hip,knee)
                frame[lower]=segment(lower,knee,wrist)
                frame[ankle]=segment(ankle,wrist,target)
                delta=Matrix.Translation(target-standing[paw].translation)
                for p in [rig.pose.bones[paw]]+list(rig.pose.bones[paw].children_recursive):
                    frame[p.name]=delta@standing[p.name]
        frames.append(frame)
    return frames
