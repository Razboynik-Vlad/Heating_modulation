"use strict";
/* Marching squares on the ice-fraction field -> smooth deforming outline. */

const ISO = 0.5;

function iceFrac(x,y){
  if(!inBounds(x,y)) return 0;
  const i=idx(x,y);
  return mat[i]===ICE ? latent[i]/L_CELL : 0;
}
const interp = (a,b) => (ISO-a)/(b-a);   // fraction along a crossing edge

function contourSegments(){
  const segs=[];
  for(let y=0;y<H-1;y++){
    for(let x=0;x<W-1;x++){
      const f00=iceFrac(x,y), f10=iceFrac(x+1,y), f11=iceFrac(x+1,y+1), f01=iceFrac(x,y+1);
      let c=0;
      if(f00>ISO)c|=1; if(f10>ISO)c|=2; if(f11>ISO)c|=4; if(f01>ISO)c|=8;
      if(c===0||c===15) continue;
      const T_=()=>[x+interp(f00,f10), y];
      const R_=()=>[x+1, y+interp(f10,f11)];
      const B_=()=>[x+interp(f01,f11), y+1];
      const L_=()=>[x, y+interp(f00,f01)];
      const push=(a,b)=>segs.push([a[0],a[1],b[0],b[1]]);
      switch(c){
        case 1:  push(L_(),T_()); break;
        case 2:  push(T_(),R_()); break;
        case 3:  push(L_(),R_()); break;
        case 4:  push(R_(),B_()); break;
        case 5:  push(L_(),T_()); push(R_(),B_()); break;
        case 6:  push(T_(),B_()); break;
        case 7:  push(L_(),B_()); break;
        case 8:  push(B_(),L_()); break;
        case 9:  push(T_(),B_()); break;
        case 10: push(T_(),R_()); push(B_(),L_()); break;
        case 11: push(R_(),B_()); break;
        case 12: push(L_(),R_()); break;
        case 13: push(T_(),R_()); break;
        case 14: push(L_(),T_()); break;
      }
    }
  }
  return segs;
}
