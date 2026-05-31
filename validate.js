const fs=require('fs');
const src=['js/config.js','js/levels.js','js/sim.js']
  .map(f=>fs.readFileSync(f,'utf8').replace(/"use strict";/g,'')).join('\n');
function trial(li,tools){
  const code=src+`
   placed=${JSON.stringify(tools)};
   buildLevel(${li});
   const need=LEVELS[${li}].need,frames=Math.ceil(LEVELS[${li}].timer*60);
   let m=-1; for(let f=0;f<frames;f++){ step(); if(iceRemaining()<=0.001){m=f;break;} }
   const r=+iceRemaining().toFixed(3);
   return {r,m,need,win:r>=need};
  `;
  return new Function(code)();
}
const r=(x,y,w,h,t)=>({type:t,x,y,w,h});
const out={};
out.L1_empty = trial(0,[]);
out.L1_solved= trial(0,[r(28,12,5,48,2)]);
out.L2_empty = trial(1,[]);
out.L2_solved= trial(1,[r(36,22,28,5,2), r(36,45,28,5,2)]);
out.L3_empty = trial(2,[]);
out.L3_insulOnly = trial(2,[r(44,32,4,10,2)]);
out.L3_solved= trial(2,[r(40,28,8,8,3), r(44,34,4,10,2), r(50,30,8,8,3)]);
const txt=JSON.stringify(out,null,2);
fs.writeFileSync('VALIDATION.json',txt);
console.log(txt);
