"use strict";
/* Level data. Geometry in grid cells (W=100, H=72).

   DESIGN: the ice sits in a POCKET fully enclosed by fixed insulator walls
   except for a MOUTH. A heater hugs the mouth, a few air cells away. Because the
   walls block every bypass path, heat can only reach the ice THROUGH the mouth,
   so plugging the mouth is decisive: left open the cube melts; sealed it survives.
   Short heater->ice distances also ensure the heat front arrives within the timer
   (diffusion length ~ sqrt(alpha*t)). Validated headlessly in validate.js. */

function rect(x,y,w,h,temp){ return temp!==undefined ? {x,y,w,h,temp} : {x,y,w,h}; }

const LEVELS = [
  {
    name:"Block the Heat",
    ambient:0,
    timer:55, need:0.25,
    heaters:[ rect(40,30,4,12, 260) ],
    walls:[ rect(48,26,24,4), rect(48,42,24,4), rect(68,26,4,20) ],
    ice: rect(50,32,18,9),
    tools:[ {type:INSUL, w:4, h:12, count:1, name:"Insulator", desc:"Blocks heat flow"} ],
    hint:"The cube's shelter has one open mouth, right at the flame. Drop the insulator into the gap to seal it in."
  },
  {
    name:"Two Fires",
    ambient:-10,
    timer:48, need:0.25,
    heaters:[ rect(42,22,16,4, 260), rect(42,52,16,4, 260) ],
    walls:[ rect(38,28,4,20), rect(58,28,4,20) ],
    ice: rect(42,32,16,12),
    tools:[
      {type:INSUL, w:16, h:4, count:2, name:"Insulator", desc:"Blocks heat flow"},
      {type:COOLER, w:8, h:8, count:1, temp:-28, name:"Cooler", desc:"Active heat sink"}
    ],
    hint:"One flame above, one below. Cap BOTH mouths with the two insulator bars (the cooler is spare margin)."
  },
  {
    name:"Heat Leak",
    ambient:-10,
    timer:54, need:0.50,
    heaters:[ rect(40,16,20,4, 260) ],
    walls:[ rect(36,22,4,24), rect(60,22,4,24), rect(36,42,28,4) ],
    ice: rect(40,26,20,16),
    tools:[
      {type:INSUL, w:12, h:4, count:1, name:"Insulator", desc:"Covers only part of the wide mouth"},
      {type:COOLER, w:8, h:4, count:1, temp:-28, name:"Cooler", desc:"Active heat sink; caps the rest"}
    ],
    hint:"Save half the cube. The insulator covers only 12 of the 20-cell mouth — set the cooler beside it to seal the rest."
  },
  {
    name:"Side Gate",
    ambient:-9,
    timer:58, need:0.35,
    heaters:[ rect(28,32,4,12, 260) ],
    walls:[
      rect(38,22,28,4),
      rect(38,48,28,4),
      rect(62,22,4,30),
      rect(38,22,4,10),
      rect(38,40,4,12)
    ],
    ice: rect(46,32,14,10),
    tools:[
      {type:INSUL, w:4, h:12, count:1, name:"Insulator", desc:"Seal the side gate"},
      {type:COOLER, w:8, h:8, count:1, temp:-28, name:"Cooler", desc:"Pull heat away from the gate"}
    ],
    hint:"The heat has only one side gate into the pocket. Close that gate first; place the cooler near the entrance if heat still leaks through."
  },
  {
    name:"Double Door",
    ambient:-10,
    timer:62, need:0.35,
    heaters:[
      rect(42,16,16,4, 260),
      rect(42,54,16,4, 260)
    ],
    walls:[
      rect(36,24,4,24),
      rect(60,24,4,24),
      rect(36,24,10,4),
      rect(54,24,10,4),
      rect(36,44,10,4),
      rect(54,44,10,4)
    ],
    ice: rect(44,31,14,10),
    tools:[
      {type:INSUL, w:12, h:4, count:2, name:"Insulator", desc:"Cap the upper and lower openings"},
      {type:COOLER, w:8, h:8, count:1, temp:-28, name:"Cooler", desc:"Extra cooling inside the chamber"}
    ],
    hint:"There are two doors: one above and one below. Use both insulator plates to cap them, then use the cooler as backup."
  },
  {
    name:"Thin Bridge",
    ambient:-8,
    timer:60, need:0.40,
    heaters:[ rect(22,34,5,10, 270) ],
    walls:[
      rect(30,25,42,4),
      rect(30,49,42,4),
      rect(70,25,4,11),
      rect(70,42,4,11),
      rect(42,29,4,8),
      rect(42,41,4,8),
      rect(56,29,4,8),
      rect(56,41,4,8)
    ],
    ice: rect(61,36,9,6),
    tools:[
      {type:INSUL, w:4, h:16, count:1, name:"Insulator", desc:"Cut the bridge across"},
      {type:COOLER, w:8, h:6, count:1, temp:-28, name:"Cooler", desc:"Slow the heat wave in the tunnel"}
    ],
    hint:"The heater feeds a narrow corridor. A vertical insulator across the bridge breaks the fastest heat path."
  },
  {
    name:"Crossfire",
    ambient:-12,
    timer:65, need:0.30,
    heaters:[
      rect(45,14,14,4, 255),
      rect(45,54,14,4, 255),
      rect(26,33,4,10, 245)
    ],
    walls:[
      rect(38,23,28,4),
      rect(38,49,28,4),
      rect(34,27,4,22),
      rect(66,27,4,22)
    ],
    ice: rect(44,33,16,10),
    tools:[
      {type:INSUL, w:14, h:4, count:2, name:"Insulator", desc:"Block top and bottom fire"},
      {type:INSUL, w:4, h:10, count:1, name:"Insulator", desc:"Block side fire"},
      {type:COOLER, w:8, h:8, count:1, temp:-28, name:"Cooler", desc:"Reduce heat inside the pocket"}
    ],
    hint:"The pocket is attacked from three sides. Seal the two horizontal mouths first, then close the side leak."
  },

  // ---- player-built levels: less pre-built walls, more agency ----

  {
    name:"Breach",
    ambient:-10,
    timer:50, need:0.30,
    heaters:[ rect(40,18,16,4, 260), rect(26,30,4,12, 260) ],
    walls:[ rect(40,42,16,4) ],                                    // bottom only
    ice:  rect(40,30,16,12),
    tools:[
      {type:INSUL, w:16, h:4,  count:1, name:"Lid",        desc:"Seals the top gap"},
      {type:INSUL, w:4,  h:12, count:1, name:"Left Panel", desc:"Seals the left gap"}
    ],
    hint:"One wall given — the bottom. Top flame and left flame are both live. One tool blocks each."
  },

  {
    name:"Open Season",
    ambient:-15,
    timer:44, need:0.25,
    heaters:[
      rect(40,14,14,4, 260),
      rect(26,28,4,14, 260),
      rect(58,28,4,14, 260)
    ],
    walls:[],                                                       // nothing pre-built
    ice:  rect(40,28,14,14),
    tools:[
      {type:INSUL, w:14, h:4,  count:1, name:"Roof",       desc:"Covers the top"},
      {type:INSUL, w:4,  h:14, count:1, name:"Left Wall",  desc:"Covers the left side"},
      {type:INSUL, w:4,  h:14, count:1, name:"Right Wall", desc:"Covers the right side"}
    ],
    hint:"No walls. Three flames. Build all three barriers yourself."
  },

  {
    name:"Ring of Fire",
    ambient:-20,
    timer:38, need:0.20,
    heaters:[
      rect(40,14,20,4, 260),
      rect(40,50,20,4, 260),
      rect(26,28,4,16, 260),
      rect(64,28,4,16, 260)
    ],
    walls:[],                                                       // nothing pre-built
    ice:  rect(40,28,20,16),
    tools:[
      {type:INSUL,  w:20, h:4,  count:2, name:"Board",       desc:"Top and bottom covers"},
      {type:COOLER, w:4,  h:16, count:2, temp:-28, name:"Side Cooler", desc:"Left and right heat sinks"}
    ],
    hint:"All four sides burning. Boards on top and bottom; coolers on both sides."
  },

  {
    name:"Three Open Sides",
    ambient:-12,
    timer:46, need:0.25,
    heaters:[
      rect(38,16,20,4, 260),
      rect(38,50,20,4, 260),
      rect(22,26,4,20, 260)
    ],
    walls:[ rect(58,26,4,20) ],                                    // right wall only
    ice:  rect(38,26,20,20),
    tools:[
      {type:INSUL,  w:20, h:4,  count:1, name:"Wide Seal",  desc:"Top or bottom cover — your choice"},
      {type:INSUL,  w:4,  h:20, count:1, name:"Side Wall",  desc:"Covers the left side"},
      {type:COOLER, w:20, h:4,  count:1, temp:-28, name:"Cryo Seal", desc:"Active chill for the remaining gap"}
    ],
    hint:"Right wall is given. Cover left with the panel. Then decide — insulator or cooler for top vs bottom? The closer flame hits harder."
  },

  {
    name:"Last Stand",
    ambient:-20,
    timer:36, need:0.15,
    heaters:[
      rect(36,10,28,4, 260),
      rect(36,58,28,4, 260),
      rect(18,26,4,20, 260),
      rect(78,26,4,20, 260)
    ],
    walls:[],                                                       // nothing pre-built
    ice:  rect(36,26,28,20),
    tools:[
      {type:INSUL,  w:28, h:4,  count:1, name:"Top Board",    desc:"Full-width top cover"},
      {type:INSUL,  w:28, h:4,  count:1, name:"Bottom Board", desc:"Full-width bottom cover"},
      {type:INSUL,  w:4,  h:20, count:1, name:"Side Wall",    desc:"Full-height cover for one side"},
      {type:COOLER, w:4,  h:20, count:1, temp:-28, name:"Cryo Wall",   desc:"Active chill for the other side"},
      {type:COOLER, w:8,  h:4,  count:1, temp:-28, name:"Bonus Cooler",desc:"Extra chill — find the weakest spot"}
    ],
    hint:"Four flames, nothing built. Boards top and bottom. Pick a side for the wall; cryo-wall on the other. Place the bonus cooler where heat leaks most."
  }
];
