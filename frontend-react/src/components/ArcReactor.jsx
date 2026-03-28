import React, { useRef, useEffect } from 'react';

const ArcReactor = ({ isListening, isThinking, isActionActive, theme }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let rotation = 0;
    let actionRingRadius = 40;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      rotation += isThinking ? 0.05 : 0.01;

      // 1. Core Glow
      const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 40);
      gradient.addColorStop(0, isActionActive ? '#10b981' : (isListening ? '#f59e0b' : '#3b82f6'));
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, 40, 0, Math.PI * 2);
      ctx.fill();

      // 2. Rotating Rings
      const drawRing = (radius, segments, width, speedMult, color) => {
        ctx.strokeStyle = color;
        ctx.lineWidth = width;
        ctx.setLineDash([Math.PI * 2 * radius / segments / 2, Math.PI * 2 * radius / segments / 2]);
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, rotation * speedMult, rotation * speedMult + Math.PI * 2);
        ctx.stroke();
      };

      const ringColor = isActionActive ? 'rgba(16, 185, 129, 0.5)' : (isListening ? 'rgba(245, 158, 11, 0.5)' : 'rgba(59, 130, 246, 0.5)');
      drawRing(25, 8, 3, 1, ringColor);
      drawRing(32, 12, 2, -1.5, ringColor);
      drawRing(40, 16, 1, 0.5, ringColor);

      // 3. Pulse Effect
      if (isListening || isThinking) {
        ctx.strokeStyle = ringColor;
        ctx.lineWidth = 1;
        ctx.setLineDash([]);
        const pulseRadius = 40 + (Math.sin(Date.now() / 200) * 10);
        ctx.beginPath();
        ctx.arc(centerX, centerY, pulseRadius, 0, Math.PI * 2);
        ctx.stroke();
      }

      // 4. Action Confirmation Ring (Emerald Ripple)
      if (isActionActive) {
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 2;
        ctx.setLineDash([]);
        actionRingRadius += 1;
        if (actionRingRadius > 60) actionRingRadius = 40;
        ctx.beginPath();
        ctx.arc(centerX, centerY, actionRingRadius, 0, Math.PI * 2);
        ctx.globalAlpha = (60 - actionRingRadius) / 20;
        ctx.stroke();
        ctx.globalAlpha = 1.0;
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [isListening, isThinking, theme]);

  return (
    <div className="relative group cursor-pointer active:scale-95 transition-transform">
      <canvas 
        ref={canvasRef} 
        width={100} 
        height={100} 
        className="w-16 h-16 sm:w-20 sm:h-20 drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]"
      />
      {isListening && (
        <div className="absolute inset-0 rounded-full bg-amber-500/10 animate-ping pointer-events-none"></div>
      )}
    </div>
  );
};

export default ArcReactor;
