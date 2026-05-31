"use strict";
/* Canvas setup + drawing: heat field, ice blob, tool/heater overlays, ghost. */

const cv = document.getElementById("cv");
cv.width = W*SCALE; cv.height = H*SCALE;
const ctx = cv.getContext("2d");

// offscreen 1px-per-cell buffers, upscaled to canvas
const fieldCanvas = document.createElement("canvas");
fieldCanvas.width=W; fieldCanvas.height=H;
const fctx = fieldCanvas.getContext("2d");
const fieldImg = fctx.createImageData(W,H);

const iceCanvas = document.createElement("canvas");
iceCanvas.width=W; iceCanvas.height=H;
const ictx = iceCanvas.getContext("2d");
const iceImg = ictx.createImageData(W,H);

function tempColor(t){
  // map -30..190 C -> cold blue .. teal .. yellow .. red
  const u = Math.max(0,Math.min(1,(t-(-30))/(190-(-30))));
  let r,g,b;
  if(u<0.5){ const k=u/0.5;       r=40+k*40;  g=90+k*150;  b=255-k*100; }
  else     { const k=(u-0.5)/0.5; r=80+k*175; g=240-k*150; b=155-k*120; }
  return [r|0,g|0,b|0];
}

function render(drag, hover){
  // 1) heat field
  const d=fieldImg.data;
  for(let i=0;i<W*H;i++){
    const [r,g,b]=tempColor(T[i]);
    const o=i*4; d[o]=r; d[o+1]=g; d[o+2]=b; d[o+3]=255;
  }
  fctx.putImageData(fieldImg,0,0);
  ctx.imageSmoothingEnabled=true;
  ctx.drawImage(fieldCanvas,0,0,cv.width,cv.height);

  // 2) ice fill (smoothed upscale)
  const id=iceImg.data;
  for(let i=0;i<W*H;i++){
    const f = mat[i]===ICE ? latent[i]/L_CELL : 0;
    const o=i*4;
    if(f>0.15){ id[o]=200; id[o+1]=235; id[o+2]=255; id[o+3]=Math.min(255,f*230+25); }
    else { id[o+3]=0; }
  }
  ictx.putImageData(iceImg,0,0);
  ctx.drawImage(iceCanvas,0,0,cv.width,cv.height);

  // 3) crisp ice outline (marching squares)
  const segs=contourSegments();
  ctx.lineWidth=2; ctx.strokeStyle="rgba(230,248,255,.9)"; ctx.beginPath();
  for(const s of segs){ ctx.moveTo(s[0]*SCALE,s[1]*SCALE); ctx.lineTo(s[2]*SCALE,s[3]*SCALE); }
  ctx.stroke();

  // 4) tool regions
  drawMaterialBorders();

  // 5) heaters
  LEVELS[levelIndex].heaters.forEach(drawHeater);

  // 6) drag ghost
  if(drag && hover) drawGhost(drag,hover);
}

function drawMaterialBorders(){
  ctx.imageSmoothingEnabled=false;
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){
    const m=mat[idx(x,y)];
    if(m===INSUL || m===COOLER){
      ctx.fillStyle = m===INSUL ? "rgba(154,123,79,.85)" : "rgba(63,210,255,.42)";
      ctx.fillRect(x*SCALE,y*SCALE,SCALE,SCALE);
    }
  }
}
function drawHeater(r){
  const x=r.x*SCALE, y=r.y*SCALE, w=r.w*SCALE, h=r.h*SCALE;
  const g=ctx.createLinearGradient(x,y,x+w,y+h);
  g.addColorStop(0,"#ff8a3c"); g.addColorStop(1,"#ff3b2f");
  ctx.fillStyle=g; ctx.fillRect(x,y,w,h);
  ctx.fillStyle="rgba(255,220,120,.9)";
  ctx.font=`${Math.min(w,h)*0.7}px serif`; ctx.textAlign="center"; ctx.textBaseline="middle";
  ctx.fillText("🔥",x+w/2,y+h/2);
}
function drawGhost(drag,hover){
  const ok = canPlace(hover.x,hover.y,drag.w,drag.h);
  ctx.fillStyle   = ok ? "rgba(120,220,160,.45)" : "rgba(255,90,90,.4)";
  ctx.strokeStyle = ok ? "rgba(160,255,200,.95)" : "rgba(255,140,140,.95)";
  ctx.lineWidth=2;
  ctx.fillRect  (hover.x*SCALE,hover.y*SCALE,drag.w*SCALE,drag.h*SCALE);
  ctx.strokeRect(hover.x*SCALE,hover.y*SCALE,drag.w*SCALE,drag.h*SCALE);
}
