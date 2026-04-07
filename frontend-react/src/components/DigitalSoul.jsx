import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshDistortMaterial, Sphere, Stars, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

const FluidCore = ({ traits, mood, color }) => {
  const meshRef = useRef();
  
  // Mapping traits to distortion
  // Neuroticism -> Speed of liquid movement
  // Agreeableness -> Smoothness (lower distortion factor)
  const speed = (traits?.neuroticism || 0.5) * 4 + 1;
  const distort = (1.1 - (traits?.agreeableness || 0.5)) * 0.6;

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.getElapsedTime() * 0.2;
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.3;
    }
  });

  return (
    <Float speed={speed} rotationIntensity={1} floatIntensity={2}>
      <Sphere ref={meshRef} args={[1, 64, 64]} scale={1.5}>
        <MeshDistortMaterial
          color={color}
          speed={speed}
          distort={distort}
          radius={1}
          emissive={color}
          emissiveIntensity={0.5}
          metalness={0.8}
          roughness={0.2}
        />
      </Sphere>
    </Float>
  );
};

const NeuralMesh = ({ traits, color }) => {
  const pointsRef = useRef();
  const lineRef = useRef();
  
  // Openness -> More particles
  const count = Math.floor(40 + (traits?.openness || 0.5) * 60);
  
  const [particles, velocities] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const vel = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 10;
      vel[i * 3] = (Math.random() - 0.5) * 0.02;
      vel[i * 3 + 1] = (Math.random() - 0.5) * 0.02;
      vel[i * 3 + 2] = (Math.random() - 0.5) * 0.02;
    }
    return [pos, vel];
  }, [count]);

  const lineGeometry = useMemo(() => new THREE.BufferGeometry(), []);

  useFrame(() => {
    const pos = pointsRef.current.geometry.attributes.position.array;
    const linePos = [];
    const maxDist = 3.5;

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      pos[i3] += velocities[i3];
      pos[i3 + 1] += velocities[i3 + 1];
      pos[i3 + 2] += velocities[i3 + 2];

      // Bounce
      if (Math.abs(pos[i3]) > 5) velocities[i3] *= -1;
      if (Math.abs(pos[i3+1]) > 5) velocities[i3+1] *= -1;
      if (Math.abs(pos[i3+2]) > 5) velocities[i3+2] *= -1;

      // Plexus lines
      for (let j = i + 1; j < count; j++) {
        const j3 = j * 3;
        const dist = Math.sqrt(
          Math.pow(pos[i3] - pos[j3], 2) +
          Math.pow(pos[i3+1] - pos[j3+1], 2) +
          Math.pow(pos[i3+2] - pos[j3+2], 2)
        );
        if (dist < maxDist) {
          linePos.push(pos[i3], pos[i3+1], pos[i3+2], pos[j3], pos[j3+1], pos[j3+2]);
        }
      }
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
    lineRef.current.geometry.setAttribute('position', new THREE.Float32BufferAttribute(linePos, 3));
  });

  return (
    <group>
      <points ref={pointsRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particles.length / 3}
            array={particles}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial size={0.08} color={color} transparent opacity={0.6} sizeAttenuation />
      </points>
      <lineSegments ref={lineRef}>
        <bufferGeometry />
        <lineBasicMaterial color={color} transparent opacity={0.2} linewidth={1} />
      </lineSegments>
    </group>
  );
};

const DigitalSoul = ({ traits, mood, size = "100%" }) => {
  const isStressed = mood === 'Stressed' || mood === 'Anxious';
  const color = isStressed ? '#f43f5e' : (mood === 'Productive' ? '#3b82f6' : '#f59e0b');

  return (
    <div style={{ width: size, height: size, minHeight: '300px' }} className="relative rounded-3xl overflow-hidden bg-stone-950/20 backdrop-blur-sm border border-white/5">
      <Canvas alpha="true" className="w-full h-full">
        <PerspectiveCamera makeDefault position={[0, 0, 12]} />
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} color={color} />
        <spotLight position={[-10, 10, 10]} angle={0.15} penumbra={1} intensity={2} color={color} />
        
        <FluidCore traits={traits} mood={mood} color={color} />
        <NeuralMesh traits={traits} color={color} />
        
        <Stars radius={50} depth={50} count={1000} factor={4} saturation={0} fade speed={1} />
      </Canvas>
      
      {/* HUD Overlay for the Soul */}
      <div className="absolute top-4 left-4 pointer-events-none">
        <div className="flex items-center gap-2">
          <div className={`w-1.5 h-1.5 rounded-full animate-pulse`} style={{ backgroundColor: color }}></div>
          <span className="text-[8px] font-mono font-bold text-stone-500 uppercase tracking-[0.2em]">Neural Signal: Active</span>
        </div>
      </div>
    </div>
  );
};

export default DigitalSoul;
