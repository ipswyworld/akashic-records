import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Building2, X, Maximize2, Zap, Search, Box, RefreshCw } from 'lucide-react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { fetchArtifacts } from '../api';
import { getThemeColors } from '../components/CommonUI';

const MemoryPalace = ({ theme }) => {
  const mountRef = useRef(null);
  const [artifacts, setArtifacts] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // --- Phase 3: Temporal Scrubbing State ---
  const [temporalState, setTemporalState] = useState(100); // 100% = Now
  const [historicalGraph, setHistoricalGraph] = useState(null);
  const [activePath, setActivePath] = useState([]); // List of node IDs in the current trace
  // ------------------------------------------

  const colors = getThemeColors(theme);

  useEffect(() => {
    fetchArtifacts().then(data => {
      setArtifacts(data);
      setIsLoading(false);
    }).catch(err => {
      console.error("Artifact Fetch Error:", err);
      setIsLoading(false);
    });
  }, []);

  // --- Phase 3: Temporal Scrubbing Logic ---
  useEffect(() => {
    if (temporalState === 100) {
      setHistoricalGraph(null);
      return;
    }
    
    // Calculate a timestamp based on the percentage
    // For mock purposes, we'll just subtract days
    const daysAgo = Math.floor((100 - temporalState) / 2);
    const date = new Date();
    date.setDate(date.getDate() - daysAgo);
    const ts = date.toISOString();

    fetch(`http://localhost:8001/analytics/graph/historical?timestamp=${ts}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('akasha_token')}` }
    })
      .then(res => res.json())
      .then(setHistoricalGraph)
      .catch(console.error);
  }, [temporalState]);
  // ------------------------------------------

  useEffect(() => {
    if (isLoading || artifacts.length === 0) return;

    // --- THREE.JS SCENE SETUP ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(theme === 'dark' ? 0x0c0a09 : 0xfafaf9);
    
    const camera = new THREE.PerspectiveCamera(75, mountRef.current.clientWidth / mountRef.current.clientHeight, 0.1, 1000);
    camera.position.z = 15;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    mountRef.current.appendChild(renderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(10, 10, 10);
    scene.add(pointLight);

    // --- NEURAL CRYSTALS ---
    const nodes = [];
    const nodeGroup = new THREE.Group();
    
    const typeColors = {
      'web_clip': 0xf59e0b, // Amber
      'audio_transcript': 0x3b82f6, // Blue
      'research_report': 0x8b5cf6, // Purple
      'document': 0x10b981, // Emerald
      'memory': 0xf43f5e // Rose
    };

    artifacts.forEach((art, i) => {
      // Create a crystal geometry (Octahedron)
      const geometry = new THREE.OctahedronGeometry(0.5, 0);
      const material = new THREE.MeshPhongMaterial({
        color: typeColors[art.artifact_type] || 0x78716c,
        emissive: typeColors[art.artifact_type] || 0x78716c,
        emissiveIntensity: 0.2,
        shininess: 100,
        transparent: true,
        opacity: 0.9
      });

      const crystal = new THREE.Mesh(geometry, material);
      
      // Random position in a sphere
      const phi = Math.acos(-1 + (2 * i) / artifacts.length);
      const theta = Math.sqrt(artifacts.length * Math.PI) * phi;
      const radius = 8 + Math.random() * 2;

      crystal.position.set(
        radius * Math.cos(theta) * Math.sin(phi),
        radius * Math.sin(theta) * Math.sin(phi),
        radius * Math.cos(phi)
      );

      crystal.userData = { id: art.id, title: art.title, summary: art.summary, type: art.artifact_type };
      nodeGroup.add(crystal);
      nodes.push(crystal);
    });

    scene.add(nodeGroup);

    // --- BACKGROUND DUST ---
    const starGeometry = new THREE.BufferGeometry();
    const starMaterial = new THREE.PointsMaterial({ color: 0x78716c, size: 0.05 });
    const starVertices = [];
    for (let i = 0; i < 2000; i++) {
      starVertices.push(THREE.MathUtils.randFloatSpread(50), THREE.MathUtils.randFloatSpread(50), THREE.MathUtils.randFloatSpread(50));
    }
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // --- THOUGHT TRACE (Visualizing reasoning paths) ---
    const traceGroup = new THREE.Group();
    if (activePath.length > 1) {
      const lineMaterial = new THREE.LineBasicMaterial({ color: 0xf59e0b, linewidth: 2, transparent: true, opacity: 0.6 });
      const points = [];
      
      activePath.forEach(nodeId => {
        const node = nodes.find(n => n.userData.id === nodeId);
        if (node) points.push(node.position);
      });

      if (points.length > 1) {
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(geometry, lineMaterial);
        traceGroup.add(line);
        
        // Add glow particles along the line
        points.forEach(p => {
          const glowGeo = new THREE.SphereGeometry(0.1, 8, 8);
          const glowMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b });
          const glow = new THREE.Mesh(glowGeo, glowMat);
          glow.position.copy(p);
          traceGroup.add(glow);
        });
      }
    }
    scene.add(traceGroup);
    // ----------------------------------------------------

    // --- RAYCASTING (Clicking) ---
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onClick = (event) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodes);

      if (intersects.length > 0) {
        const data = intersects[0].object.userData;
        setSelectedNode(data);
        
        // Highlight logic
        nodes.forEach(n => n.material.emissiveIntensity = 0.2);
        intersects[0].object.material.emissiveIntensity = 1.0;
      }
    };

    window.addEventListener('click', onClick);

    // --- ANIMATION LOOP ---
    const animate = () => {
      requestAnimationFrame(animate);
      nodeGroup.rotation.y += 0.001;
      stars.rotation.y -= 0.0005;
      nodes.forEach(n => {
        n.rotation.x += 0.01;
        n.rotation.y += 0.01;
      });
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      camera.aspect = mountRef.current.clientWidth / mountRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('click', onClick);
      window.removeEventListener('resize', handleResize);
      if (mountRef.current) mountRef.current.removeChild(renderer.domElement);
    };
  }, [isLoading, artifacts, theme]);

  return (
    <div className="flex-1 flex flex-col relative h-full overflow-hidden bg-stone-950 font-sans">
      {/* Header Overlay */}
      <div className="absolute top-0 left-0 right-0 p-8 z-20 pointer-events-none flex justify-between items-start">
        <div>
          <h2 className="text-white text-3xl font-bold tracking-tight flex items-center gap-3">
            <div className="p-2 bg-amber-500 rounded-xl shadow-lg shadow-amber-500/20 text-slate-900">
              <Box className="w-6 h-6" />
            </div>
            Memory Palace
          </h2>
          <p className="text-stone-500 text-sm mt-2">Neural crystal field of {artifacts.length} artifacts.</p>
        </div>
        
        <div className="flex gap-4 pointer-events-auto">
          <div className="bg-stone-900/80 backdrop-blur-xl border border-stone-800 rounded-2xl px-4 py-2 flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
              <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Neural Mode: Crystal</span>
            </div>
            <div className="h-4 w-px bg-stone-800"></div>
            <div className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-stone-500" />
              <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest italic">Orbit to Explore</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3D Mount Point */}
      <div ref={mountRef} className="flex-1 w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Phase 3: Temporal Scrubbing Slider UI */}
      <div className="absolute bottom-6 left-6 right-6 lg:left-auto lg:right-12 lg:bottom-12 lg:w-72 z-40">
        <div className="bg-stone-900/80 backdrop-blur-xl border border-stone-800 rounded-3xl p-6 shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest flex items-center gap-2">
              <RefreshCw className={`w-3 h-3 ${temporalState < 100 ? 'animate-spin' : ''}`} /> Temporal Scrubbing
            </span>
            <span className="text-[10px] font-mono text-amber-500 font-bold">{temporalState}%</span>
          </div>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={temporalState} 
            onChange={(e) => setTemporalState(parseInt(e.target.value))}
            className="w-full h-1.5 bg-stone-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
          />
          <div className="flex justify-between mt-2">
            <span className="text-[8px] text-stone-600 font-bold">Genesis</span>
            <span className="text-[8px] text-stone-600 font-bold">Now</span>
          </div>
        </div>
      </div>
      {/* -------------------------------------- */}

      {/* Selected Node Details */}
      {selectedNode && (
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-lg z-30 animate-in slide-in-from-bottom-4 duration-500 p-6">
          <div className="bg-stone-900/90 backdrop-blur-3xl border border-stone-800 rounded-[32px] p-8 shadow-2xl relative overflow-hidden">
            <button 
              onClick={() => setSelectedNode(null)}
              className="absolute top-6 right-6 p-2 hover:bg-stone-800 rounded-full text-stone-500 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            
            <div className="mb-6">
              <span className="px-3 py-1 bg-amber-500/10 text-amber-500 rounded-full text-[10px] font-bold uppercase tracking-widest border border-amber-500/20 mb-4 inline-block">
                {selectedNode.type.replace('_', ' ')}
              </span>
              <h3 className="text-xl font-bold text-white mb-2 leading-tight">{selectedNode.title}</h3>
              <div className="flex items-center gap-2 text-stone-500 text-xs italic">
                <Zap className="w-3 h-3" />
                Sovereign Synthesis
              </div>
            </div>

            <p className="text-stone-400 text-sm leading-relaxed mb-8 line-clamp-4">
              {selectedNode.summary || "No summary available for this neural node. Request a synthesis to generate insights."}
            </p>

            <div className="flex gap-3">
              <button className="flex-1 bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold py-3.5 rounded-2xl text-xs transition-all flex items-center justify-center gap-2">
                Open Full Artifact
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
              <button className="px-6 py-3.5 bg-stone-800 hover:bg-stone-700 text-white font-bold rounded-2xl text-xs transition-all border border-stone-700">
                Relate
              </button>
            </div>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="absolute inset-0 z-50 bg-stone-950 flex flex-col items-center justify-center gap-4">
          <div className="w-12 h-12 border-2 border-amber-500/20 border-t-amber-500 rounded-full animate-spin"></div>
          <p className="text-stone-500 font-mono text-[10px] uppercase tracking-[0.2em] animate-pulse">Initializing Palace Geometry...</p>
        </div>
      )}
    </div>
  );
};

export default MemoryPalace;
