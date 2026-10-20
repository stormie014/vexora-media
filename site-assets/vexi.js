// Vexora mascot: a cartoon phone with blue eyes, eyelashes and a small smile.
// mascotSVG({expr, pose, ghost, w}) returns an <svg> string.
// expr: happy | sideeye | shocked | excited | smug | sad | wink
// pose: wave | hips | point | none | hold (holds a sign above)
(function (g) {
  const C = {
    teal: '#0D7C80', tealDark: '#0A5F62', pink: '#C8365F', bg: '#F4F7F7',
    ink: '#14252A', blue: '#2E86FF', blueDeep: '#1554C0', white: '#FFFFFF'
  };

  function eye(cx, cy, expr, side) {
    // side: -1 left eye, 1 right eye
    let out = '';
    let rx = 31, ry = 35, irisR = 21, px = 0, py = 3;
    if (expr === 'shocked') { rx = 36; ry = 40; irisR = 15; py = 0; }
    if (expr === 'sideeye') { px = 9; py = 4; }
    if (expr === 'smug') { px = -7; py = 2; }
    if (expr === 'sad') { py = 6; }
    // closed / happy-squint eyes
    if (expr === 'excited' || (expr === 'wink' && side === 1)) {
      out += `<path d="M${cx - 24} ${cy + 6} Q${cx} ${cy - 22} ${cx + 24} ${cy + 6}" fill="none" stroke="${C.ink}" stroke-width="7" stroke-linecap="round"/>`;
    } else {
      out += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${C.white}" stroke="${C.ink}" stroke-width="5"/>`;
      out += `<circle cx="${cx + px}" cy="${cy + py}" r="${irisR}" fill="${C.blue}"/>`;
      out += `<circle cx="${cx + px}" cy="${cy + py}" r="${irisR * 0.55}" fill="${C.blueDeep}"/>`;
      out += `<circle cx="${cx + px}" cy="${cy + py}" r="${irisR * 0.32}" fill="${C.ink}"/>`;
      out += `<circle cx="${cx + px - irisR * 0.35}" cy="${cy + py - irisR * 0.4}" r="${irisR * 0.24}" fill="${C.white}"/>`;
      out += `<circle cx="${cx + px + irisR * 0.3}" cy="${cy + py + irisR * 0.35}" r="${irisR * 0.1}" fill="${C.white}"/>`;
      // heavy lids
      if (expr === 'sideeye' || expr === 'smug') {
        out += `<path d="M${cx - rx - 2} ${cy - 2} L${cx + rx + 2} ${cy - 2} L${cx + rx + 2} ${cy - ry - 6} L${cx - rx - 2} ${cy - ry - 6} Z" fill="${C.bg}"/>`;
        out += `<line x1="${cx - rx}" y1="${cy - 2}" x2="${cx + rx}" y2="${cy - 2}" stroke="${C.ink}" stroke-width="6" stroke-linecap="round"/>`;
      }
      if (expr === 'sad') {
        out += `<path d="M${cx - rx} ${cy - ry + 4} L${cx + rx} ${cy - ry + 4} L${cx + side * rx} ${cy - ry - 14} Z" fill="${C.bg}"/>`;
      }
    }
    // eyelashes (outer top corner), three curls
    const lashBaseX = cx + side * (rx * 0.55);
    const lashBaseY = cy - ry * 0.82 + ((expr === 'sideeye' || expr === 'smug') ? ry * 0.75 : 0);
    if (!(expr === 'excited' || (expr === 'wink' && side === 1))) {
      for (let i = 0; i < 3; i++) {
        const a = side * (0.55 + i * 0.38);
        const x1 = lashBaseX + side * i * 6, y1 = lashBaseY + i * 7;
        const x2 = x1 + Math.sin(a) * 22, y2 = y1 - Math.cos(a) * 22;
        out += `<path d="M${x1} ${y1} Q${(x1 + x2) / 2 + side * 6} ${(y1 + y2) / 2 - 6} ${x2} ${y2}" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>`;
      }
    } else {
      out += `<path d="M${cx + side * 22} ${cy - 2} q${side * 10} -10 ${side * 18} -12" fill="none" stroke="${C.ink}" stroke-width="5" stroke-linecap="round"/>`;
    }
    return out;
  }

  function mouth(expr) {
    const cx = 160, cy = 272;
    switch (expr) {
      case 'shocked': return `<ellipse cx="${cx}" cy="${cy + 6}" rx="14" ry="19" fill="${C.ink}"/><ellipse cx="${cx}" cy="${cy + 15}" rx="8" ry="6" fill="${C.pink}"/>`;
      case 'excited': return `<path d="M${cx - 30} ${cy - 6} Q${cx} ${cy + 44} ${cx + 30} ${cy - 6} Z" fill="${C.ink}"/><path d="M${cx - 16} ${cy + 16} Q${cx} ${cy + 8} ${cx + 16} ${cy + 16} Q${cx} ${cy + 30} ${cx - 16} ${cy + 16} Z" fill="${C.pink}"/>`;
      case 'sideeye': return `<path d="M${cx - 14} ${cy + 4} L${cx + 16} ${cy + 1}" stroke="${C.ink}" stroke-width="6" stroke-linecap="round"/>`;
      case 'smug': return `<path d="M${cx - 18} ${cy + 2} Q${cx + 4} ${cy + 12} ${cx + 22} ${cy - 8}" fill="none" stroke="${C.ink}" stroke-width="6" stroke-linecap="round"/>`;
      case 'sad': return `<path d="M${cx - 16} ${cy + 12} Q${cx} ${cy - 2} ${cx + 16} ${cy + 12}" fill="none" stroke="${C.ink}" stroke-width="6" stroke-linecap="round"/>`;
      default: return `<path d="M${cx - 18} ${cy} Q${cx} ${cy + 16} ${cx + 18} ${cy}" fill="none" stroke="${C.ink}" stroke-width="6" stroke-linecap="round"/>`;
    }
  }

  function limbs(pose, line) {
    const s = `stroke="${line || C.ink}" stroke-width="7" stroke-linecap="round" fill="none"`;
    let out = '';
    // legs + sneakers
    out += `<path d="M128 382 L122 432" ${s}/><path d="M192 382 L198 432" ${s}/>`;
    out += `<path d="M104 438 Q104 424 122 426 L136 430 Q140 442 128 444 L108 444 Q102 443 104 438 Z" fill="${C.pink}" stroke="${C.ink}" stroke-width="5"/>`;
    out += `<path d="M216 438 Q216 424 198 426 L184 430 Q180 442 192 444 L212 444 Q218 443 216 438 Z" fill="${C.pink}" stroke="${C.ink}" stroke-width="5"/>`;
    const hand = (x, y) => `<circle cx="${x}" cy="${y}" r="12" fill="${C.white}" stroke="${C.ink}" stroke-width="5"/>`;
    if (pose === 'wave') {
      out += `<path d="M44 230 Q20 270 34 300" ${s}/>` + hand(36, 306);
      out += `<path d="M276 210 Q306 170 296 128" ${s}/>` + hand(296, 120);
      out += `<path d="M310 104 q10 -6 14 -18 M318 128 q14 -2 22 -10" stroke="${C.ink}" stroke-width="4" stroke-linecap="round" fill="none"/>`;
    } else if (pose === 'hips') {
      out += `<path d="M44 220 Q6 250 30 280 Q38 288 44 282" ${s}/>`;
      out += `<path d="M276 220 Q314 250 290 280 Q282 288 276 282" ${s}/>`;
    } else if (pose === 'point') {
      out += `<path d="M44 230 Q20 270 34 300" ${s}/>` + hand(36, 306);
      out += `<path d="M276 220 Q320 214 352 196" ${s}/>` + hand(356, 194);
    } else if (pose === 'hold') {
      out += `<path d="M44 200 Q14 150 40 92" ${s}/>` + hand(42, 86);
      out += `<path d="M276 200 Q306 150 280 92" ${s}/>` + hand(278, 86);
    } else if (pose === 'phone') {
      out += `<path d="M44 230 Q20 270 34 300" ${s}/>` + hand(36, 306);
      out += `<path d="M44 230 Q20 270 34 300" ${s}/>`;
      out += `<path d="M276 230 Q300 262 284 290" ${s}/>` + hand(282, 296);
    }
    return out;
  }

  function mascotSVG(o = {}) {
    const expr = o.expr || 'happy', pose = o.pose || 'wave', w = o.w || 320;
    const ghost = !!o.ghost;
    const vb = '-40 40 400 420';
    let body = '';
    // shadow
    body += `<ellipse cx="160" cy="448" rx="110" ry="10" fill="${C.ink}" opacity="0.10"/>`;
    body += limbs(ghost ? 'none' : pose, o.line);
    // phone body
    body += `<rect x="40" y="70" width="240" height="320" rx="46" fill="${C.teal}" stroke="${C.ink}" stroke-width="6"/>`;
    body += `<rect x="60" y="94" width="200" height="272" rx="30" fill="${C.bg}"/>`;
    body += `<rect x="128" y="102" width="64" height="16" rx="8" fill="${C.ink}"/>`;
    body += `<circle cx="180" cy="110" r="3.5" fill="#3a5a63"/>`;
    // side button
    body += `<rect x="278" y="150" width="8" height="40" rx="4" fill="${C.tealDark}" stroke="${C.ink}" stroke-width="3"/>`;
    // blush
    body += `<ellipse cx="96" cy="250" rx="17" ry="10" fill="${C.pink}" opacity="0.35"/><ellipse cx="224" cy="250" rx="17" ry="10" fill="${C.pink}" opacity="0.35"/>`;
    body += eye(114, 198, expr, -1) + eye(206, 198, expr, 1);
    body += mouth(expr);
    if (ghost) {
      // bedsheet ghost costume draped over the phone, eye holes show the eyes
      body = `<ellipse cx="160" cy="448" rx="120" ry="10" fill="${C.ink}" opacity="0.10"/>` +
        `<path d="M160 40 C60 40 28 140 30 250 C30 330 24 400 14 438 Q44 420 66 440 Q92 420 116 442 Q140 420 162 442 Q188 420 210 442 Q234 420 258 440 Q280 420 306 438 C296 400 290 330 290 250 C292 140 260 40 160 40 Z" fill="${C.white}" stroke="${C.ink}" stroke-width="6"/>` +
        `<path d="M70 300 Q90 330 86 380 M250 290 Q236 340 244 390" fill="none" stroke="#d6dfe0" stroke-width="5" stroke-linecap="round"/>` +
        `<ellipse cx="118" cy="170" rx="34" ry="38" fill="${C.ink}"/><ellipse cx="202" cy="170" rx="34" ry="38" fill="${C.ink}"/>` +
        eye(118, 172, expr, -1).split(C.bg).join(C.white).replace(/fill="#FFFFFF" stroke="#14252A" stroke-width="5"/, `fill="${C.white}" stroke="none"`) +
        eye(202, 172, expr, 1).split(C.bg).join(C.white).replace(/fill="#FFFFFF" stroke="#14252A" stroke-width="5"/, `fill="${C.white}" stroke="none"`) +
        `<path d="M146 236 Q160 246 174 236" fill="none" stroke="#c9d3d4" stroke-width="5" stroke-linecap="round"/>` +
        `<ellipse cx="112" cy="232" rx="13" ry="7" fill="${C.pink}" opacity="0.25"/><ellipse cx="208" cy="232" rx="13" ry="7" fill="${C.pink}" opacity="0.25"/>`;
    }
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${w}" height="${w * 420 / 400}">${body}</svg>`;
  }

  g.mascotSVG = mascotSVG;
  g.VX = C;
})(typeof window !== 'undefined' ? window : globalThis);
