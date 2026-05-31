"use strict";
/* Grid state + physics: conduction (heat eq, harmonic-mean k), convection
   approx, latent-heat melting. Ice erodes from the hot-facing side. */

// ---------- shared grid state ----------
let T, Tn, mat, latent;     // flat grids, idx = y*W + x
let levelIndex = 0;
let initialIce = 1;
let placed = [];            // placed tools: {type,x,y,w,h,slot}

const idx = (x,y) => y*W + x;
const inBounds = (x,y) => x>=0 && y>=0 && x<W && y<H;

function stamp(r,m,temp){
  for(let y=r.y;y<r.y+r.h;y++) for(let x=r.x;x<r.x+r.w;x++)
    if(inBounds(x,y)){ const i=idx(x,y); mat[i]=m; if(temp!==undefined) T[i]=temp; }
}
function applyTool(p){
  const temp = p.type===COOLER ? COOLER_T : AMBIENT;
  for(let y=p.y;y<p.y+p.h;y++) for(let x=p.x;x<p.x+p.w;x++)
    if(inBounds(x,y)){ const i=idx(x,y); if(mat[i]===AIR){ mat[i]=p.type; T[i]=temp; } }
}

// ---------- build / reset ----------
function buildLevel(li){
  const L = LEVELS[li];
  T = new Float32Array(W*H);
  Tn = new Float32Array(W*H);
  mat = new Uint8Array(W*H);
  latent = new Float32Array(W*H);
  T.fill(AMBIENT); mat.fill(AIR);

  (L.walls||[]).forEach(r=>stamp(r,INSUL,AMBIENT));   // fixed insulator
  L.heaters.forEach(r=>stamp(r,HEATER,HEATER_T));     // burners

  let cells=0;
  for(let y=L.ice.y;y<L.ice.y+L.ice.h;y++)
    for(let x=L.ice.x;x<L.ice.x+L.ice.w;x++)
      if(inBounds(x,y)){ const i=idx(x,y); mat[i]=ICE; T[i]=MELT_T; latent[i]=L_CELL; cells++; }
  initialIce = cells*L_CELL;

  placed.forEach(p=>applyTool(p));                    // re-apply player tools
}

// ---------- physics ----------
const hk = (a,b) => 2*a*b/(a+b+1e-9);                 // harmonic mean -> series conduction

function step(){
  for(let s=0;s<SUBSTEPS;s++) substep();
}
function substep(){
  for(let y=0;y<H;y++){
    for(let x=0;x<W;x++){
      const i=idx(x,y), mi=mat[i];
      if(mi===HEATER){ Tn[i]=HEATER_T; continue; }
      if(mi===COOLER){ Tn[i]=COOLER_T; continue; }
      const ti=T[i], ki=MAT_K[mi], ci=MAT_C[mi];
      // net conductive flux from 4 neighbors, harmonic-mean face conductivity
      let flux=0;
      if(x>0)   { const j=i-1; flux+=hk(ki,MAT_K[mat[j]])*(T[j]-ti); }
      if(x<W-1) { const j=i+1; flux+=hk(ki,MAT_K[mat[j]])*(T[j]-ti); }
      if(y>0)   { const j=i-W; flux+=hk(ki,MAT_K[mat[j]])*(T[j]-ti); }
      if(y<H-1) { const j=i+W; flux+=hk(ki,MAT_K[mat[j]])*(T[j]-ti); }
      const dE = DT*flux;            // energy into cell this substep
      let tnew = ti + dE/ci;

      if(mi===ICE){
        // latent-heat gate: at melting point energy melts instead of heating.
        // dE>0 drains latent (melts); dE<0 refreezes (cooler nearby).
        latent[i] -= dE;
        if(latent[i] > L_CELL) latent[i] = L_CELL;
        if(latent[i] <= 0){
          const leftover = -latent[i];              // energy past full melt
          mat[i]=AIR; latent[i]=0;
          Tn[i] = MELT_T + leftover/MAT_C[AIR];      // becomes warming air
        } else {
          Tn[i] = MELT_T;                            // stays at 0C while phase-changing
        }
        continue;
      }
      if(mi===AIR) tnew += CONVECT*(AMBIENT - tnew)*DT; // convection/radiation approx
      Tn[i]=tnew;
    }
  }
  const t=T; T=Tn; Tn=t;   // swap buffers (mat/latent mutated in place)
}

function iceRemaining(){
  let s=0; for(let i=0;i<W*H;i++) if(mat[i]===ICE) s+=latent[i];
  return initialIce>0 ? s/initialIce : 0;
}

// ---------- placement rule ----------
function canPlace(x,y,w,h){
  if(x<0||y<0||x+w>W||y+h>H) return false;
  for(let yy=y;yy<y+h;yy++) for(let xx=x;xx<x+w;xx++)
    if(mat[idx(xx,yy)]!==AIR) return false;   // only onto empty air
  return true;
}
