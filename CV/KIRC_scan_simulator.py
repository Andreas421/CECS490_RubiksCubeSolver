#!/usr/bin/env python3
"""K.I.R.C. overhead-camera scanning simulator (no hardware required).

Usage:
    python KIRC_scan_simulator.py
    python KIRC_scan_simulator.py --seed 2027 --output KIRC_scan_visualizer.html

The simulator:
  * Maintains the 54 facelets of a legal scrambled 3x3 cube.
  * Simulates an overhead camera that sees ONLY the U face.
  * Moves any of the F/R/B/L faces in quarter turns (alone or opposite pairs).
  * Records each camera reading against the sticker's ORIGINAL cube position.
  * Compares 40-turn original, 34-turn restored, and 25-turn solve-ready plans.
  * Asserts every noncenter sticker is scanned and the cube is restored.

To replace the simulation with hardware, replace the calls to apply_group()
with serial STEP/DIR commands + ACK, and replace capture()'s synthetic colors
with the 9 top-face colors classified by the OpenCV pipeline. Keep tracker.

Python 3.9+; standard library only.
"""

from __future__ import annotations
import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

FACE_ORDER = "URFDLB"   # Kociemba face order
SIDE_FACES = "FRBL"
COLORS = {
    "U": "#F6F7F9",  # white
    "R": "#D94B48",  # red
    "F": "#28A064",  # green
    "D": "#F3CC47",  # yellow
    "L": "#F09A36",  # orange
    "B": "#3F73DB",  # blue
}
COLOR_NAMES = {"U":"White", "R":"Red", "F":"Green", "D":"Yellow", "L":"Orange", "B":"Blue"}
Vec = Tuple[int, int, int]
# Each face's outward normal, right direction, and DOWN direction (viewed
# from outside that face); guarantees standard URFDLB facelet orientation.
FRAME: Dict[str, Tuple[Vec, Vec, Vec]] = {
    "U": ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
    "R": ((1, 0, 0), (0, 0, -1), (0, -1, 0)),
    "F": ((0, 0, 1), (1, 0, 0), (0, -1, 0)),
    "D": ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
    "L": ((-1, 0, 0), (0, 0, 1), (0, -1, 0)),
    "B": ((0, 0, -1), (-1, 0, 0), (0, -1, 0)),
}


def plus(a: Vec, b: Vec) -> Vec:
    return tuple(x+y for x, y in zip(a, b))  # type: ignore[return-value]


def cross(a: Vec, b: Vec) -> Vec:
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def dot(a: Vec, b: Vec) -> int:
    return sum(x*y for x, y in zip(a, b))


def rot(v: Vec, normal: Vec, clockwise: bool) -> Vec:
    """Rotate 90 degrees about a signed normal using integer geometry."""
    p = cross(v, normal) if clockwise else cross(normal, v)
    return plus(p, tuple(x*dot(normal, v) for x in normal))


def generate_moves():
    slots = {}
    for face in FACE_ORDER:
        normal, right, down = FRAME[face]
        for row in range(3):
            for col in range(3):
                offset = plus(tuple((col-1)*x for x in right),
                              tuple((row-1)*x for x in down))
                slots[(plus(normal, offset), normal)] = f"{face}{3*row+col}"
    assert len(slots) == 54
    positions = list(slots.keys())
    names = list(slots.values())
    index = {name: n for n, name in enumerate(names)}
    permutation = {}
    for face in FACE_ORDER:
        axis = FRAME[face][0]
        for suffix, clockwise in [("", True), ("'", False)]:
            new_locations = []
            for position, sticker_normal in positions:
                if dot(position, axis) == 1:
                    destination = (rot(position, axis, clockwise),
                                   rot(sticker_normal, axis, clockwise))
                else:
                    destination = (position, sticker_normal)
                new_locations.append(index[slots[destination]])
            permutation[face+suffix] = new_locations
    return names, index, permutation


NAMES, INDEX, PERMS = generate_moves()
CENTERS = {INDEX[f+"4"] for f in FACE_ORDER}
NON_CENTERS = set(range(54)) - CENTERS
U_SLOTS = [INDEX[f"U{i}"] for i in range(9)]
SOLVED = [name[0] for name in NAMES]


def inverse(move: str) -> str:
    assert move in PERMS
    return move[:-1] if move.endswith("'") else move+"'"


def rotate(stickers: List, move: str) -> List:
    """Return sticker state after one move, both physical colors and IDs."""
    nxt = list(stickers)
    for source, target in enumerate(PERMS[move]):
        nxt[target] = stickers[source]
    return nxt


def apply_group(stickers: List, moves: Tuple[str, ...]) -> List:
    """Opposite turns F+B and R+L commute; these can run simultaneously."""
    if len(moves) > 1:
        assert len(moves) == 2 and frozenset(m[0] for m in moves) in (
            frozenset("FB"), frozenset("RL"))
    for move in moves:
        stickers = rotate(stickers, move)
    return stickers


def invert_group(group: Tuple[str, ...]) -> Tuple[str, ...]:
    return tuple(inverse(move) for move in reversed(group))


def make_scramble(seed: int, length: int = 22):
    rng = random.Random(seed)
    state = list(SOLVED)
    last_face = None
    scramble = []
    for _ in range(length):
        face = rng.choice([f for f in FACE_ORDER if f != last_face])
        move = face + rng.choice(["", "'"])
        state = rotate(state, move)
        scramble.append(move)
        last_face = face
    return state, scramble


@dataclass(frozen=True)
class Action:
    moves: Tuple[str, ...]
    photo: bool
    phase: str
    explanation: str


def optimized_plan() -> List[Action]:
    """34 quarter-turns, 20 motor stages, 12 total photos."""
    out = [Action((), True, "START", "Overhead camera captures the U face.")]
    for pair in (("F", "B"), ("R", "L")):
        for step in range(1,5):
            out.append(Action(pair, step != 4, "FULL ROTATIONS",
                f"Turn {pair[0]} and {pair[1]} together; {step*90}° total."))

    forward = [
        (("L'",), False),
        (("F",), True),
        (("R", "L'"), True),
        (("B", "F'"), True),
        (("R'", "L"), True),
        (("B'",), True),
    ]
    for turns, photo in forward:
        out.append(Action(turns, photo, "CLEANUP SCAN",
            "Expose remaining F/R/B/L middle-edge stickers."))
    for turns, _ in reversed(forward):
        out.append(Action(invert_group(turns), False, "RESTORE CUBE",
            "Undo the cleanup turns in reverse order."))
    return out


def fastest_plan() -> List[Action]:
    """25-turn plan: do not undo cleanup; solve the cube in its final state."""
    return [a for a in optimized_plan() if a.phase != "RESTORE CUBE"]


def baseline_plan() -> List[Action]:
    """Earlier 40-turn, 21-photo schedule: one motor at a time."""
    out = [Action((),True,"START","Capture U face.")]
    for face in SIDE_FACES:
        for k in range(1,5):
            out.append(Action((face,),k != 4,"FULL ROTATIONS",
                    f"Rotate {face} to {k*90}°; photo if not restored."))
    setup = [
        ("F", ("R", "L'")), ("B", ("L", "R'")),
        ("L", ("F", "B'")), ("R", ("B", "F'")),
    ]
    for first, pair in setup:
        out.append(Action((first,),False,"CLEANUP SCAN","Rotate setup face."))
        for move in pair:
            out.append(Action((move,),True,"CLEANUP SCAN","Capture new side-middle sticker."))
            out.append(Action((inverse(move),),False,"RESTORE SETUP","Undo observation turn."))
        out.append(Action((inverse(first),),False,"RESTORE SETUP","Undo setup face."))
    return out


def simulate(initial_cube: List[str], plan: List[Action], restore_expected: bool = True):
    """One exact state tracker for both physical colors and original sticker IDs."""
    physical = list(initial_cube)
    original_location = list(range(54))  # original ID currently in each slot
    seen: Dict[int, str] = {}
    # Known centers are supplied by calibration, not inferred from hidden stickers.
    # U center is visible, but we preload all six for a uniform scanner interface.
    known_centers = {INDEX[face+"4"]:face for face in FACE_ORDER}
    frames = []
    num_photos = 0
    motor_turns = 0
    for step,action in enumerate(plan):
        physical = apply_group(physical,action.moves)
        original_location = apply_group(original_location,action.moves)
        motor_turns += len(action.moves)
        new_ids=[]
        if action.photo:
            num_photos+=1
            # Real version: camera sees ONLY these 9 top slots; OpenCV returns
            # nine colors, not the complete 54-sticker model below.
            for slot in U_SLOTS:
                original_id = original_location[slot]
                measured_color = physical[slot]
                if original_id not in CENTERS:
                    if original_id in seen:
                        assert seen[original_id] == measured_color, "Conflicting camera reading"
                    else:
                        seen[original_id] = measured_color
                        new_ids.append(original_id)
        # Color order and position matter, not just 9-of-each-color counts.
        frames.append({
            "step":step, "moves":list(action.moves), "photo":action.photo,
            "phase":action.phase, "explanation":action.explanation,
            "cube":list(physical), "top":[physical[i] for i in U_SLOTS],
            "seen":[seen.get(i) for i in range(54)],
            "coverage":len(seen), "new":[NAMES[i] for i in new_ids],
            "photos":num_photos,"motor_turns":motor_turns,
        })
    if restore_expected:
        assert original_location == list(range(54)), "Facelet tracker didn't return home"
        assert physical == initial_cube, "Cube was not restored to original scramble"
    assert set(seen) == NON_CENTERS, (
        "Unscanned original stickers: " + str([NAMES[i] for i in NON_CENTERS-set(seen)]))
    recovered = [seen.get(i,known_centers.get(i)) for i in range(54)]
    assert recovered == initial_cube, "Reconstructed original state is incorrect"
    assert all(recovered.count(face) == 9 for face in FACE_ORDER)
    # If scanning ends in a different configuration, apply the tracked
    # permutation to the recovered ORIGINAL stickers and solve this state.
    current_for_solver = [recovered[old_id] for old_id in original_location]
    assert current_for_solver == physical, "Final physical cube state was not reconstructed"
    return {
        "frames":frames, "motor_turns":motor_turns,
        "motor_stages":len(plan)-1, "photos":num_photos,
        "coverage":len(seen),
        "original_cube":"".join(initial_cube),
        "recovered_cube":"".join(recovered),
        "restored":physical == initial_cube,
        "state_to_solve":"".join(current_for_solver),
    }


HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>K.I.R.C. — Overhead Camera Scanning Simulator</title>
<style>
:root{--bg:#0e131d;--card:#1a2433;--raised:#243143;--text:#f1f4f8;--sub:#acb9c9;--line:#334254;--accent:#75d7b7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,Segoe UI,Arial,sans-serif}
main{max-width:1300px;margin:auto;padding:30px 20px 50px}header{display:flex;gap:16px;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;margin-bottom:24px}
h1{font-size:clamp(23px,3vw,34px);letter-spacing:-.8px;margin:6px 0}p{line-height:1.55;color:var(--sub)}.eyebrow{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:var(--accent);font-weight:800}
.panel{background:var(--card);border:1px solid var(--line);border-radius:15px;padding:20px}.stack{display:grid;gap:17px}
.twocol{display:grid;grid-template-columns:minmax(280px,1fr) minmax(300px,1.4fr);gap:17px;margin-top:18px}
@media(max-width:780px){.twocol{grid-template-columns:1fr}}
.control{display:flex;align-items:center;gap:9px;flex-wrap:wrap}button,select{border:1px solid #46586c;border-radius:9px;padding:10px 13px;background:#27364a;color:white;font:inherit;cursor:pointer}
button:hover,select:hover{background:#344a62}button.primary{background:#28846d;border-color:#3bb695;font-weight:700}button.primary:hover{background:#33977d}
button:disabled{opacity:.35;cursor:default}input[type=range]{accent-color:var(--accent);width:100%;margin-top:18px}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:11px;margin:17px 0}
.kpi{padding:14px 13px;border:1px solid var(--line);border-radius:11px;background:#16202c}.kpi b{display:block;font-size:clamp(21px,3vw,30px);line-height:1.15}.kpi span{font-size:11px;color:var(--sub)}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}.tile{aspect-ratio:1;border-radius:6px;border:1px solid #536072;display:flex;align-items:center;justify-content:center;box-shadow:inset 0 -3px #0002;min-width:0}
.tile.unseen{background:#2b3647!important;color:#a4aebb!important;box-shadow:none;font-size:19px;font-weight:700}.tile.new{outline:3px solid var(--accent);outline-offset:-2px}
.camera{max-width:258px;margin:auto}.sectiontitle{font-size:14px;letter-spacing:.5px;margin:0 0 14px;color:#d8e2ef;font-weight:750}
.net{display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(3,auto);gap:8px;max-width:540px;margin:auto;align-items:center}
.face{min-width:0}.facelabel{font-size:11px;text-align:center;color:var(--sub);font-weight:750;margin:0 0 4px}.face .grid3{gap:3px}.face .tile{border-radius:3px}
.muted{color:var(--sub);font-size:13px}.move{font-size:25px;font-weight:800;color:var(--accent);letter-spacing:1px}.ph{display:inline-block;padding:5px 8px;background:#304e44;border-radius:6px;color:#b1f2dd;font-size:12px;font-weight:750}
.ph.off{background:#344050;color:#a9b6c9}.stage{color:#a8b8cc;text-transform:uppercase;letter-spacing:1px;font-size:11px;font-weight:750}
.progress{height:10px;background:#354457;border-radius:10px;overflow:hidden;margin-top:12px}.fill{height:100%;width:0;background:var(--accent);transition:width .15s}
.log{max-height:218px;overflow:auto;border-radius:9px;border:1px solid var(--line)}.logrow{display:flex;gap:10px;padding:9px 12px;border-bottom:1px solid #344353;color:#bdcbda;font-size:12px;cursor:pointer}
.logrow.active{background:#2b4b4a;color:#fff}.logrow:last-child{border-bottom:0}.logrow .n{width:25px;color:#8d9eb0;flex-shrink:0}
footer{margin-top:20px;color:var(--sub);font-size:13px}.tag{display:inline-block;padding:3px 8px;border-radius:5px;background:#374458;color:#fff;font-size:12px}
@media(max-width:550px){main{padding:18px 10px}.panel{padding:15px}.kpis{grid-template-columns:repeat(2,1fr)}.net{gap:4px}}
</style></head><body><main>
<header><div><div class="eyebrow">K.I.R.C. / Hardware-Free Prototype</div><h1>One-camera cube scanning simulation</h1>
<p style="max-width:725px;margin-bottom:0">The only real camera view is the 3×3 <b>top face</b>. Rotate the other faces, record exposed sticker colors, and reconstruct the original scramble.</p></div>
<div class="control"><label for="plan" class="muted">Scan strategy</label><select id="plan"><option value="fastest">Solve-ready · 25 turns</option><option value="optimized">Restored · 34 turns</option><option value="baseline">Original · 40 turns</option></select></div></header>
<div class="panel"><div class="control"><button id="prev">◀ Previous</button><button id="play" class="primary">▶ Play</button><button id="next">Next ▶</button><button id="reset">↺ Reset</button><span id="stepCounter" class="muted"></span></div>
<input id="seek" type="range" min="0" max="20" value="0"><div class="kpis">
<div class="kpi"><b id="coverage">8 / 48</b><span>Original stickers scanned</span></div>
<div class="kpi"><b id="turns">0</b><span>Motor quarter-turns</span></div>
<div class="kpi"><b id="shots">1</b><span>Photos captured</span></div>
<div class="kpi"><b id="stages">0</b><span>Motor stages completed</span></div></div>
<div class="progress"><div class="fill" id="bar"></div></div></div>
<div class="twocol">
<div class="stack"><section class="panel"><h2 class="sectiontitle">OVERHEAD CAMERA — WHAT THE HARDWARE ACTUALLY SEES</h2>
<div class="camera" id="topCamera"></div><div style="margin-top:16px"><div class="stage" id="phase"></div><div class="move" id="moves"></div>
<div style="margin-top:8px"><span class="ph" id="photoFlag">PHOTO</span></div><p id="explanation"></p><p id="newStickers"></p></div></section>
<section class="panel"><h2 class="sectiontitle">HOW TO READ THIS</h2><p class="muted">A move like <b>F+B</b> means two opposite faces rotate simultaneously by 90°. A prime (<b>'</b>) means counterclockwise as viewed from outside that face. A photo is taken only at selected stages.</p><p class="muted">The recovered state is indexed by the <em>sticker's position before scanning began</em>, not its temporary position in the overhead image.</p></section></div>
<div class="stack"><section class="panel"><h2 class="sectiontitle">ORIGINAL SCRAMBLE — RECONSTRUCTED AS PHOTOS ARRIVE</h2><div class="net" id="coverageNet"></div><p class="muted">Question marks are stickers the camera has <b>not</b> photographed yet. The six center colors are assumed pre-calibrated.</p></section>
<section class="panel"><h2 class="sectiontitle">TRUE CUBE STATE — SIMULATION DEBUG ONLY</h2><div class="net" id="truthNet"></div><p class="muted">The physical system cannot see all of this at once. This complete cube net is shown here to demonstrate the face movements and verify restoration.</p></section>
</div></div>
<div class="twocol"><section class="panel"><h2 class="sectiontitle">SCANNING TIMELINE — CLICK ANY STAGE</h2><div class="log" id="timeline"></div></section><section class="panel"><h2 class="sectiontitle">VERIFICATION & IMPORTANT ASSUMPTIONS</h2>
<p id="summary" class="muted"></p><p class="muted">The overhead motor is <b>removed throughout scanning</b>. Other center stickers are hidden, so the cube needs a known center-color mapping / keyed insertion orientation. Camera readings here are perfect simulated colors; real OpenCV detection will need confidence checks and rescans.</p><p class="muted">Simultaneous opposite turns are geometrically valid, but must be confirmed mechanically. If your mechanism cannot safely turn both at once, run them sequentially.</p></section></div>
<footer>Offline interactive visualization generated by <code>KIRC_scan_simulator.py</code>. Arrow keys = step back / forward; space = play / pause. Seed: <span id="seed"></span>.</footer>
</main>
<script>
const DATA=__SIM_DATA__;
const colors={"U":"#F6F7F9","R":"#D94B48","F":"#28A064","D":"#F3CC47","L":"#F09A36","B":"#3F73DB"};
const ids={};const faces='URFDLB';for(let i=0;i<faces.length;i++)for(let j=0;j<9;j++)ids[faces[i]+j]=i*9+j;
const layout={U:[1,0],L:[0,1],F:[1,1],R:[2,1],B:[3,1],D:[1,2]};
let kind='optimized', current=0, timer=null;
function elem(tag,cls,text){const d=document.createElement(tag);if(cls)d.className=cls;if(text!==undefined)d.textContent=text;return d;}
function getFrame(){return DATA[kind].frames[current]}
function tile(color,hidden=false,highlight=false){let d=elem('div','tile'+(hidden?' unseen':'')+(highlight?' new':''),hidden?'?':'');if(!hidden){d.style.background=colors[color]||'#222';}return d}
function makeFace(face, values, captured=[],newNames=[]){let wrap=elem('div','face');let t=elem('div','facelabel',face);wrap.appendChild(t);let g=elem('div','grid3');
 for(let j=0;j<9;j++){let id=ids[face+j],value=values[id];let isCenter=(j===4);g.appendChild(tile(value,value===null, newNames.includes(face+j)));}wrap.appendChild(g);return wrap;}
function drawNet(target,values,newNames=[]){const root=document.getElementById(target);root.replaceChildren();
 for(let row=0;row<3;row++)for(let col=0;col<4;col++){const entry=Object.entries(layout).find(([f,c])=>c[0]===col&&c[1]===row);
 if(entry)root.appendChild(makeFace(entry[0],values,[],newNames));else root.appendChild(elem('div'));}}
function update(){const sim=DATA[kind],frame=getFrame();const length=sim.frames.length;document.getElementById('seek').max=length-1;document.getElementById('seek').value=current;
 document.getElementById('stepCounter').textContent=`Stage ${current} of ${length-1}`;
 document.getElementById('coverage').textContent=frame.coverage+' / 48';document.getElementById('turns').textContent=frame.motor_turns;
 document.getElementById('shots').textContent=frame.photos;document.getElementById('stages').textContent=current;
 document.getElementById('bar').style.width=(100*frame.coverage/48)+'%';document.getElementById('phase').textContent=frame.phase;
 document.getElementById('moves').textContent=frame.moves.length?frame.moves.join(' + '):'Initial camera capture';
 const ph=document.getElementById('photoFlag');ph.textContent=frame.photo?'● CAPTURE PHOTO':'NO PHOTO';ph.className=frame.photo?'ph':'ph off';
 document.getElementById('explanation').textContent=frame.explanation;
 document.getElementById('newStickers').textContent=frame.new.length?'New originals: '+frame.new.join(', '):'No new original stickers captured.';
 let camera=elem('div','grid3');for(let i=0;i<9;i++)camera.appendChild(tile(frame.top[i],false,false));document.getElementById('topCamera').replaceChildren(camera);
 const learned=frame.seen.slice();for(const face of faces)learned[ids[face+'4']]=face;
 drawNet('coverageNet',learned,frame.new);
 drawNet('truthNet',frame.cube,[]);
 const rows=document.getElementById('timeline').children;for(let i=0;i<rows.length;i++)rows[i].classList.toggle('active',i===current);
 if(rows[current] && Math.abs(rows[current].offsetTop-document.getElementById('timeline').scrollTop)>180)rows[current].scrollIntoView({block:'nearest'});
 document.getElementById('summary').innerHTML=`<b>${sim.motor_turns} quarter-turns, ${sim.motor_stages} motor stages, ${sim.photos} photos.</b> All 48 non-center stickers are observed; ${sim.restored?"the original scramble is restored":"the final cube state is calculated for immediate solving"}. Reconstruction exactly matches the simulated true state. This is a valid sequence, not a mathematically proven global optimum.`;
 document.getElementById('play').textContent=timer?'Ⅱ Pause':'▶ Play';document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===length-1;
}
function selectPlan(name){pause();kind=name;current=0;let log=document.getElementById('timeline');log.replaceChildren();DATA[kind].frames.forEach((f,i)=>{
 let r=elem('div','logrow');r.appendChild(elem('div','n',String(i).padStart(2,'0')));let m=elem('div','',`${f.moves.length?f.moves.join('+'):'INITIAL'}${f.photo?'  📷':''}  ·  ${f.phase}  ·  ${f.coverage}/48`);r.appendChild(m);r.onclick=()=>{pause();current=i;update()};log.appendChild(r);});update();}
function pause(){if(timer)clearInterval(timer);timer=null;document.getElementById('play').textContent='▶ Play'}
function toggle(){if(timer){pause();update();return;}if(current>=DATA[kind].frames.length-1)current=0;timer=setInterval(()=>{if(current>=DATA[kind].frames.length-1){pause();update();return;}current++;update()},850);update()}
function change(n){pause();current=Math.max(0,Math.min(DATA[kind].frames.length-1,n));update()}
document.getElementById('play').onclick=toggle;document.getElementById('prev').onclick=()=>change(current-1);document.getElementById('next').onclick=()=>change(current+1);document.getElementById('reset').onclick=()=>change(0);
document.getElementById('seek').oninput=e=>change(+e.target.value);document.getElementById('plan').onchange=e=>selectPlan(e.target.value);
document.addEventListener('keydown',e=>{if(['INPUT','SELECT'].includes(document.activeElement?.tagName))return;if(e.key==='ArrowRight')change(current+1);if(e.key==='ArrowLeft')change(current-1);if(e.key===' '){e.preventDefault();toggle()}});
document.getElementById('seed').textContent=DATA.seed;selectPlan(kind);
</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=2027, help="Random scramble seed")
    parser.add_argument("--output", default="KIRC_scan_visualizer.html", help="Offline HTML output path")
    args = parser.parse_args()
    original, scramble = make_scramble(args.seed)
    results = {
        "seed":args.seed,"scramble":scramble,
        "baseline":simulate(original,baseline_plan()),
        "optimized":simulate(original,optimized_plan()),
        "fastest":simulate(original,fastest_plan(),restore_expected=False),
    }
    assert results['baseline']['recovered_cube'] == results['optimized']['recovered_cube'] == results['fastest']['recovered_cube']
    html = HTML.replace('__SIM_DATA__',json.dumps(results,separators=(',',':')).replace('</','<\\/'))
    outpath = Path(args.output)
    outpath.parent.mkdir(parents=True,exist_ok=True)
    outpath.write_text(html,encoding='utf-8')
    print(f"Saved interactive visualizer: {outpath.resolve()}")
    print(f"Scramble (for repeatability): {' '.join(scramble)}")
    for plan in ('baseline','optimized','fastest'):
        r=results[plan]
        print(f"{plan:10} {r['motor_turns']:2} quarter-turns | {r['motor_stages']:2} motor stages | "
              f"{r['photos']:2} camera photos | {r['coverage']}/48 scanned | restored={r['restored']}")
    print('Original URFDLB state:',results['optimized']['recovered_cube'])
    print('Scan-and-solve URFDLB state:',results['fastest']['state_to_solve'])
    print('PASS: every original sticker recovered; final states verified against physical cube simulation.')


if __name__=='__main__':
    main()
