import React, { useState, useRef } from 'react';
import { NodeViewWrapper } from '@tiptap/react';
import type { NodeViewProps } from '@tiptap/react';
import { Trash2, Crop as CropIcon, Check, X } from 'lucide-react';

export const ImageNodeView: React.FC<NodeViewProps> = ({ node, updateAttributes, deleteNode, selected }) => {
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLSpanElement>(null);
  
  const { src, width, align } = node.attrs;

  const [isCroppingMode, setIsCroppingMode] = useState(false);
  const [cropBox, setCropBox] = useState({ t: 0, r: 0, b: 0, l: 0 }); // values in percentage 0-100

  // SCALING (Narożniki)
  const handleScaleDrag = (e: React.MouseEvent, corner: 'nw' | 'ne' | 'sw' | 'se') => {
    if (isCroppingMode) return;
    e.preventDefault();
    e.stopPropagation();
    
    if (!imgRef.current || !containerRef.current?.parentElement) return;
    
    const startX = e.clientX;
    const startWidth = imgRef.current.offsetWidth;
    const parentWidth = containerRef.current.parentElement.offsetWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = moveEvent.clientX - startX;
      // Jeśli ciągniemy za prawy róg (ne, se), delta dodaje szerokości; jeśli za lewy (nw, sw) delta odejmuje od prawej, ale graficznie powiększa "w lewo"
      const factor = corner.includes('e') ? 1 : -1;
      const newWidthPx = Math.max(50, startWidth + deltaX * factor);
      const percentage = Math.min(100, Math.round((newWidthPx / parentWidth) * 100));
      updateAttributes({ width: `${percentage}%` });
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  // CROPPING (Uchwyty krawędzi w trybie crop Mode)
  const handleCropDrag = (e: React.MouseEvent, edge: 't' | 'b' | 'l' | 'r') => {
    e.preventDefault();
    e.stopPropagation();

    if (!imgRef.current) return;

    const startX = e.clientX;
    const startY = e.clientY;
    const imgW = imgRef.current.offsetWidth;
    const imgH = imgRef.current.offsetHeight;
    
    const startCrop = { ...cropBox };

    const onMouseMove = (moveEvent: MouseEvent) => {
      const dx = moveEvent.clientX - startX;
      const dy = moveEvent.clientY - startY;

      // Calculate the percentage movement
      const dpx = (dx / imgW) * 100;
      const dpy = (dy / imgH) * 100;

      setCropBox(prev => {
        const next = { ...prev };
        if (edge === 'l') next.l = Math.max(0, Math.min(100 - next.r - 2, startCrop.l + dpx)); // 2% minimum gap
        if (edge === 'r') next.r = Math.max(0, Math.min(100 - next.l - 2, startCrop.r - dpx)); 
        if (edge === 't') next.t = Math.max(0, Math.min(100 - next.b - 2, startCrop.t + dpy));
        if (edge === 'b') next.b = Math.max(0, Math.min(100 - next.t - 2, startCrop.b - dpy));
        return next;
      });
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  // Zastosuj finalne cięcie (po kliknięciu zielonego "ptaszka")
  const applyCrop = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!imgRef.current) return;

    const { t, r, b, l } = cropBox;
    if (t === 0 && r === 0 && b === 0 && l === 0) {
      setIsCroppingMode(false);
      return;
    }

    const image = imgRef.current;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const scaleX = image.naturalWidth / image.width;
    const scaleY = image.naturalHeight / image.height;

    // Przeliczenie procentów na oryginalne piksele obrazka (px krawędzi)
    const sourceX = (l / 100) * image.width * scaleX;
    const sourceY = (t / 100) * image.height * scaleY;
    const sourceW = ((100 - l - r) / 100) * image.width * scaleX;
    const sourceH = ((100 - t - b) / 100) * image.height * scaleY;

    if (sourceW <= 0 || sourceH <= 0) {
      setIsCroppingMode(false);
      setCropBox({ t: 0, r: 0, b: 0, l: 0 });
      return;
    }

    canvas.width = sourceW;
    canvas.height = sourceH;
    ctx.imageSmoothingQuality = 'high';

    ctx.drawImage(
      image,
      sourceX, sourceY, sourceW, sourceH,
      0, 0, sourceW, sourceH
    );

    const base64Image = canvas.toDataURL('image/jpeg', 0.95);
    
    // Dopasowanie nowej szerokości wizualnej proporcjonalnie do "ściętych" pikseli
    const ratioRemaining = (100 - l - r) / 100;
    const currentWidthPercent = parseFloat(node.attrs.width || '100');
    const newWidthPercent = Math.max(5, Math.round(currentWidthPercent * ratioRemaining));

    setIsCroppingMode(false);
    setCropBox({ t: 0, r: 0, b: 0, l: 0 });

    updateAttributes({ 
      src: base64Image, 
      width: `${newWidthPercent}%`
    });
  };

  const cancelCrop = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsCroppingMode(false);
    setCropBox({ t: 0, r: 0, b: 0, l: 0 });
  };

  return (
    <NodeViewWrapper 
      as="span" 
      ref={containerRef}
      className={`relative inline-block align-top mb-1 transition-none leading-none ${selected && !isCroppingMode ? 'ring-2 ring-blue-500' : ''}`} 
      style={{ width: width === '100%' ? '100%' : width }}
      data-align={align}
    >
      {/* Pasek narzędzi na obrazku */}
      {selected && !isCroppingMode && (
        <div className="absolute top-2 right-2 flex gap-1 z-20 bg-white/95 backdrop-blur-sm p-1 rounded-lg shadow-sm border border-gray-200">
          <button 
            onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); setIsCroppingMode(true); }}
            className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
            title="Przytnij zdjęcie"
          >
            <CropIcon size={14} />
          </button>
          <div className="w-[1px] bg-gray-200 my-1"></div>
          <button 
            onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); deleteNode(); }}
            className="p-1.5 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
            title="Usuń zdjęcie"
          >
            <Trash2 size={14} />
          </button>
        </div>
      )}

      <img 
        ref={imgRef} 
        src={src} 
        className={`max-w-full block select-none rounded-sm transition-opacity duration-200 ${isCroppingMode ? 'opacity-30' : 'opacity-100'}`} 
        alt="" 
      />

      {/* Render explicit crop UI over the dimmed image */}
      {isCroppingMode && (
        <div className="absolute inset-0 pointer-events-none z-30" style={{ clipPath: 'none' }}>
           
           {/* Wyraźny nieucięty obrazek wewnątrz obszaru cropowania */}
           <img 
             src={src} 
             className="absolute inset-0 w-full h-full object-fill select-none pointer-events-none" 
             style={{
               clipPath: `inset(${cropBox.t}% ${cropBox.r}% ${cropBox.b}% ${cropBox.l}%)`
             }}
             alt="" 
           />

           {/* Box showing cropped area boundary z handles */}
           <div 
             className="absolute border-2 border-blue-500 shadow-[0_0_0_9999px_rgba(0,0,0,0.4)] pointer-events-none"
             style={{
               top: `${cropBox.t}%`,
               right: `${cropBox.r}%`,
               bottom: `${cropBox.b}%`,
               left: `${cropBox.l}%`
             }}
           >
              {/* Handles for Crop (edges) */}
              <div className="absolute top-0 left-1/2 -ms-4 w-8 h-3 -mt-1.5 cursor-ns-resize pointer-events-auto bg-blue-500 rounded-full opacity-0 hover:opacity-100 transition-opacity" onMouseDown={(e) => handleCropDrag(e, 't')} />
              <div className="absolute bottom-0 left-1/2 -ms-4 w-8 h-3 -mb-1.5 cursor-ns-resize pointer-events-auto bg-blue-500 rounded-full opacity-0 hover:opacity-100 transition-opacity" onMouseDown={(e) => handleCropDrag(e, 'b')} />
              <div className="absolute left-0 top-1/2 -mt-4 w-3 h-8 -ml-1.5 cursor-ew-resize pointer-events-auto bg-blue-500 rounded-full opacity-0 hover:opacity-100 transition-opacity" onMouseDown={(e) => handleCropDrag(e, 'l')} />
              <div className="absolute right-0 top-1/2 -mt-4 w-3 h-8 -mr-1.5 cursor-ew-resize pointer-events-auto bg-blue-500 rounded-full opacity-0 hover:opacity-100 transition-opacity" onMouseDown={(e) => handleCropDrag(e, 'r')} />
           </div>

           {/* Approve / Cancel actions directly under crop box */}
           <div 
             className="absolute flex gap-1 pointer-events-auto backdrop-blur-sm bg-white/90 p-1 rounded-lg border border-gray-200 shadow-lg"
             style={{
               bottom: `calc(${cropBox.b}% - 2.5rem)`,
               left: `calc(${cropBox.l}% + (100% - ${cropBox.l}% - ${cropBox.r}%) / 2)`,
               transform: 'translateX(-50%)'
             }}
           >
              <button 
                onMouseDown={applyCrop}
                className="flex items-center gap-1 px-2 py-1 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700"
              >
                <Check size={14} /> Przytnij
              </button>
              <button 
                onMouseDown={cancelCrop}
                className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium hover:bg-gray-200"
              >
                <X size={14} /> Anuluj
              </button>
           </div>
        </div>
      )}

      {/* Render Scaling UI */}
      {selected && !isCroppingMode && (
        <div className="absolute inset-0 pointer-events-none" style={{ clipPath: 'none' }}>
           {/* ----- CORNER SCALES ----- */}
           <div className="absolute -top-1.5 -left-1.5 w-3 h-3 bg-white border-2 border-blue-500 cursor-nwse-resize pointer-events-auto rounded-sm" onMouseDown={(e) => handleScaleDrag(e, 'nw')} title="Skaluj" />
           <div className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-white border-2 border-blue-500 cursor-nesw-resize pointer-events-auto rounded-sm" onMouseDown={(e) => handleScaleDrag(e, 'ne')} title="Skaluj" />
           <div className="absolute -bottom-1.5 -left-1.5 w-3 h-3 bg-white border-2 border-blue-500 cursor-nesw-resize pointer-events-auto rounded-sm" onMouseDown={(e) => handleScaleDrag(e, 'sw')} title="Skaluj" />
           <div className="absolute -bottom-1.5 -right-1.5 w-3 h-3 bg-white border-2 border-blue-500 cursor-nwse-resize pointer-events-auto rounded-sm" onMouseDown={(e) => handleScaleDrag(e, 'se')} title="Skaluj" />
        </div>
      )}
    </NodeViewWrapper>
  );
};
