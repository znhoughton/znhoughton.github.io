/* ═══════════════════════════════════════════════════════════
   Easter Eggs — znhoughton.github.io
   ═══════════════════════════════════════════════════════════ */

// ── 1. Console Message ───────────────────────────────────────
console.log(
  '%c znhoughton.github.io %c\n\n' +
  'You opened DevTools — respect.\n\n' +
  'This is a linguist\'s website, so naturally it has a\n' +
  'linguist\'s console message.\n\n' +
  '💡 Try typing "chomsky" anywhere on the page.\n' +
  '💡 Try the Konami code: ↑↑↓↓←→←→BA\n' +
  '💡 There may or may not be a /secret page.\n\n' +
  '%c  ə  θ  ʃ  ŋ  ɪ  æ  ɔ  ʒ  — phonetics gang  %c',
  'background:#7c6ef7;color:#fff;font-family:monospace;font-size:13px;font-weight:700;padding:3px 10px;border-radius:3px;',
  'color:#9490a8;font-family:monospace;font-size:13px;',
  'background:#1a1a1f;color:#7c6ef7;font-family:monospace;font-size:12px;padding:3px 8px;border-radius:3px;',
  ''
);

// ── Toast helper ──────────────────────────────────────────────
function showToast(html, duration) {
  duration = duration || 4000;
  var toast = document.getElementById('ee-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'ee-toast';
    Object.assign(toast.style, {
      position: 'fixed',
      bottom: '2rem',
      right: '2rem',
      background: '#1a1a1f',
      border: '1px solid rgba(124,110,247,0.45)',
      color: '#f0eff5',
      fontFamily: "'JetBrains Mono', monospace",
      fontSize: '13px',
      padding: '0.85rem 1.25rem',
      borderRadius: '10px',
      maxWidth: '340px',
      lineHeight: '1.65',
      zIndex: '9999',
      boxShadow: '0 8px 32px rgba(0,0,0,0.55)',
      transition: 'opacity 0.3s, transform 0.3s',
      opacity: '0',
      transform: 'translateY(10px)',
      pointerEvents: 'none',
    });
    document.body.appendChild(toast);
  }
  toast.innerHTML = html;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';
  clearTimeout(toast._timer);
  toast._timer = setTimeout(function () {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
  }, duration);
}

// ── 2. Konami Code → IPA Rain ────────────────────────────────
var KONAMI_SEQ = [
  'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
  'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
  'b', 'a'
];
var konamiIdx = 0;

document.addEventListener('keydown', function (e) {
  if (e.key === KONAMI_SEQ[konamiIdx]) {
    konamiIdx++;
    if (konamiIdx === KONAMI_SEQ.length) {
      konamiIdx = 0;
      startIPARain();
    }
  } else {
    konamiIdx = (e.key === KONAMI_SEQ[0]) ? 1 : 0;
  }
});

function startIPARain() {
  if (document.getElementById('ee-rain-canvas')) return;

  showToast(
    '🌧️ <strong>IPA Rain activated</strong><br>' +
    '<span style="color:#9490a8;font-size:12px">↑↑↓↓←→←→BA — nice.</span>',
    2800
  );

  var canvas = document.createElement('canvas');
  canvas.id = 'ee-rain-canvas';
  Object.assign(canvas.style, {
    position: 'fixed', top: '0', left: '0',
    width: '100vw', height: '100vh',
    zIndex: '8888', pointerEvents: 'none',
    opacity: '1', transition: 'opacity 0.8s',
  });
  document.body.appendChild(canvas);

  var ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  var IPA_CHARS = [
    'ə','ɛ','æ','ʌ','ɔ','ʊ','ɪ','iː','uː','ɑ',
    'θ','ð','ʃ','ʒ','ŋ','ɹ','j','w','l','m',
    'n','p','b','t','d','k','g','f','v','s',
    'z','h','tʃ','dʒ','ɾ','ʔ','ɬ','ɦ','ç','β'
  ];

  var colW = 22;
  var cols = Math.floor(canvas.width / colW);
  var drops = [];
  for (var i = 0; i < cols; i++) {
    drops[i] = Math.random() * -canvas.height / 20;
  }

  var frame = 0;
  var totalFrames = 480; // ~16 seconds at 33ms

  var interval = setInterval(function () {
    ctx.fillStyle = 'rgba(13,13,15,0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (var i = 0; i < drops.length; i++) {
      var bright = Math.random() > 0.93;
      ctx.fillStyle = bright
        ? 'rgba(200,190,255,0.95)'
        : ('rgba(124,110,247,' + (0.35 + Math.random() * 0.45) + ')');
      ctx.font = (bright ? '15px' : '13px') + ' "JetBrains Mono", monospace';
      var sym = IPA_CHARS[Math.floor(Math.random() * IPA_CHARS.length)];
      ctx.fillText(sym, i * colW, drops[i] * 20);
      if (drops[i] * 20 > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }

    frame++;
    if (frame >= totalFrames) {
      clearInterval(interval);
      canvas.style.opacity = '0';
      setTimeout(function () { canvas.remove(); }, 900);
    }
  }, 33);
}

// ── 3. Type "chomsky" anywhere → Quote Toast ─────────────────
var CHOMSKY_QUOTES = [
  {
    q: '"We do not assume that the goal of learning is the formulation of explicit rules. Rather, we assume it is the acquisition of connection strengths which allow a network of simple units to act as though it knew the rules."',
    attr: '— Rumelhart &amp; McClelland, <em>Parallel Distributed Processing</em>, 1986',
    paraphrase: false
  },
  {
    q: '"Acquisition of language and other abilities occurs via gradual adjustment of the connections among simple processing units. Characterizations of performance as \'rule-governed\' are viewed as approximate descriptions of patterns of language use; no actual rules operate in the processing of language."',
    attr: '— McClelland &amp; Patterson, <em>Trends in Cognitive Sciences</em>, 2002',
    paraphrase: false
  },
  {
    q: 'Grammar is the cognitive organization of one\'s experience with language. Categories and schemas emerge gradually from patterns of use, shaped by frequency of exposure and entrenchment across repeated encounters.',
    attr: '— Bybee, <em>Language, Usage and Cognition</em>, 2010 (paraphrased)',
    paraphrase: true
  },
  {
    q: '"High-frequency words and phrases have stronger representations in the sense that they are more easily accessed."',
    attr: '— Bybee, <em>Phonology and Language Use</em>, 2001',
    paraphrase: false
  },
];
var chomskyIdx = 0;
var typedBuf = '';

document.addEventListener('keypress', function (e) {
  var tag = document.activeElement && document.activeElement.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA') return;
  typedBuf = (typedBuf + e.key).slice(-7).toLowerCase();
  if (typedBuf === 'chomsky') {
    var item = CHOMSKY_QUOTES[chomskyIdx % CHOMSKY_QUOTES.length];
    chomskyIdx++;
    var qHtml = item.paraphrase
      ? item.q
      : '<em>' + item.q + '</em>';
    showToast(
      '<span style="color:#7c6ef7;font-size:11px">// chomsky detected — here\'s a better quote</span><br><br>' +
      qHtml + '<br>' +
      '<span style="color:#9490a8;font-size:11px">' + item.attr + '</span>',
      7000
    );
  }
});

// ── 4. ZNH Logo — click 5× ───────────────────────────────────
var ZNH_MSGS = [
  '🔍 <strong>One.</strong> Curious.',
  '🔍 <strong>Two.</strong> Persistent.',
  '🔍 <strong>Three.</strong> You\'re going to find it, aren\'t you.',
  '🔍 <strong>Four.</strong> Almost…',
  '🎉 <strong>You found it.</strong><br>' +
    '<span style="color:#9490a8;font-size:12px">' +
    'ZNH = Zachary <em>Nicholas</em> Houghton.<br>' +
    'Now you know.<br><br>' +
    '<span style="color:#5c5870;font-size:11px">ps: have you tried /secret?</span>' +
    '</span>',
];
var znhClicks = 0;
var znhResetTimer = null;

document.addEventListener('DOMContentLoaded', function () {

  // ZNH logo clicks
  var logo = document.querySelector('.nav-logo');
  if (logo) {
    logo.addEventListener('click', function (e) {
      e.preventDefault();
      znhClicks = Math.min(znhClicks + 1, ZNH_MSGS.length);
      clearTimeout(znhResetTimer);
      showToast(ZNH_MSGS[znhClicks - 1], 4000);
      if (znhClicks >= ZNH_MSGS.length) {
        znhResetTimer = setTimeout(function () { znhClicks = 0; }, 20000);
      }
    });
  }

  // ── 5. Headshot clicks — speech bubbles ──────────────────
  var headshot = document.getElementById('ee-headshot');
  if (headshot) {
    var HEADSHOT_MSGS = [
      '/ˈzæk.ər.i/',
      'ə schwa a day keeps the prescriptivists away.',
      'frequency effects are real.',
      'please cite your sources.',
      'error-driven learning in action.',
      'ok you can stop now.',
      'i mean it.',
      '…/ə/.',
      '(╯°□°）╯︵ ┻━┻',
    ];
    var hsClicks = 0;
    headshot.style.cursor = 'pointer';
    headshot.addEventListener('click', function () {
      var msg = HEADSHOT_MSGS[Math.min(hsClicks, HEADSHOT_MSGS.length - 1)];
      showHeadshotBubble(msg, headshot, hsClicks);
      hsClicks++;
    });
  }


});

// ── Headshot bubble helper ────────────────────────────────────
function showHeadshotBubble(text, anchor, clickNum) {
  var rect = anchor.getBoundingClientRect();
  var bubble = document.createElement('div');
  bubble.innerHTML = text;

  // Stack bubbles upward, cycling every 4 clicks
  var stackOffset = (clickNum % 4) * 40;
  var topPos = Math.max(65, rect.top - 50 - stackOffset);
  var leftPos = rect.left + 8;

  Object.assign(bubble.style, {
    position: 'fixed',
    background: '#1a1a1f',
    border: '1px solid rgba(124,110,247,0.5)',
    color: '#f0eff5',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '12px',
    padding: '0.45rem 0.85rem',
    borderRadius: '8px',
    whiteSpace: 'nowrap',
    zIndex: '9500',
    pointerEvents: 'none',
    opacity: '1',
    transition: 'opacity 0.5s, transform 0.5s',
    top: topPos + 'px',
    left: leftPos + 'px',
  });

  document.body.appendChild(bubble);

  // If bubble overflows right edge, nudge it left
  var bRect = bubble.getBoundingClientRect();
  if (bRect.right > window.innerWidth - 12) {
    bubble.style.left = Math.max(10, window.innerWidth - bRect.width - 16) + 'px';
  }

  setTimeout(function () {
    bubble.style.opacity = '0';
    bubble.style.transform = 'translateY(-10px)';
  }, 2300);
  setTimeout(function () { bubble.remove(); }, 2900);
}
