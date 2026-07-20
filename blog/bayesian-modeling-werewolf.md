---
title: "Bayesian Modeling: A Werewolf Walkthrough"
date: 2026-06-15
summary: An extended, no-statistics-background-required walkthrough of Bayesian updating using the social deduction game Werewolf including behavioral history, Beta priors, and why the same observation means different things for different players.
---

This post exists because of an argument. On a cold, winter night in Chicago (the night before an **I Fight Dragons** concert we were attending), I was with some friends passing the time playing **Werewolf**. The story begins with a friend of mine acting suspiciously; a friend of my sister's said that alone was reason enough
to vote him out. I pushed back: we already know this particular friend always acts suspicious, werewolf or not,
so we need to weigh in our prior information (our "Bayesian priors," if you will) before treating
the current round's behavior as real evidence. That kicked off a genuine debate over whether "he's just like
that" even counts as a Bayesian prior in any rigorous sense.

It does (in other words, I was right), though the honest answer is more interesting than one might originally expect: it isn't the prior on whether he's the werewolf, it's a prior for the likelihood of his
behavior, and working out exactly what that means, and why it isn't just a semantic trick, is the
point of this post. Werewolf turns out to map almost perfectly onto the structure of Bayesian
inference, which is convenient, since I already love the game. No statistics background required (though a statistics background will certainly make this easier).

### The Setup

Imagine that you're playing Werewolf: 5 players, 1 is secretly the werewolf. You don't know who. During the
game you observe someone acting suspiciously. Should that update your belief that they're the
werewolf? It depends entirely on their *baseline rate of acting suspicious*, and critically on
whether that rate differs between their werewolf and innocent roles. Compare two players from
past games (Charles is, more or less, my friend from that game in Chicago):

<div class="player-pair">
  <div class="player-card-math">
    <h4>Charles: always suspicious</h4>
    <p>
      As werewolf, Charles acted suspiciously 8 out of 10 rounds.
      As an innocent, he acted suspiciously 8 out of 10 rounds.
      His behavior tells you nothing about his role; it's just his personality.
    </p>
    <span class="prior-tag">θ_w ~ Beta(8, 2) &nbsp;· mean ≈ 0.80</span>
    <span class="prior-tag">θ_i ~ Beta(8, 2) &nbsp;· mean ≈ 0.80</span>
    <span class="verdict-tag">→ suspicious acts: uninformative</span>
  </div>
  <div class="player-card-math">
    <h4>Spencer: only suspicious as werewolf</h4>
    <p>
      As werewolf, Spencer acted suspiciously 8 out of 10 rounds.
      As an innocent, he acted suspiciously only 2 out of 10 rounds.
      His suspicious behavior strongly distinguishes his roles.
    </p>
    <span class="prior-tag">θ_w ~ Beta(8, 2) &nbsp;· mean ≈ 0.80</span>
    <span class="prior-tag">θ_i ~ Beta(2, 8) &nbsp;· mean ≈ 0.20</span>
    <span class="verdict-tag">→ suspicious acts: highly informative</span>
  </div>
</div>

### Behavioral History

Before the current round starts, you've been keeping mental tally marks across all previous
rounds. For each player you track two columns: how often they acted suspiciously *when they were
the werewolf*, and how often they acted suspiciously *when they were innocent*. We encode these
counts as Beta distributions:

```math
// behavioral history in count form · W = werewolf role, I = innocent role
θ_w ~ Beta(α_w, β_w)   where α_w = suspicious acts as W
                             β_w = non-suspicious acts as W

θ_i ~ Beta(α_i, β_i)   where α_i = suspicious acts as I
                             β_i = non-suspicious acts as I

// E[θ_w] = α_w / (α_w + β_w) · E[θ_i] = α_i / (α_i + β_i)
// More past rounds → larger α+β → narrower distribution → more reliable estimate.
// Charles: α_w=8, β_w=2, α_i=8, β_i=2 → E[θ_w] = E[θ_i] = 0.80. Identical.
// Spencer: α_w=8, β_w=2, α_i=2, β_i=8 → E[θ_w] = 0.80, E[θ_i] = 0.20. Separated.
```

These distributions are fixed for the duration of the current round — you're using what you
learned before to make inferences now.

### Updating P(W)

A new round begins. `P(W) = 1/5` — one werewolf among five players. Each observation updates it
via Bayes' rule, and the result becomes the new `P(W)` going into the next observation. The
likelihoods come directly from the behavioral history:

```math
// likelihoods · from behavioral history
P(S  | W) = E[θ_w] = α_w / (α_w + β_w)
P(S  | I) = E[θ_i] = α_i / (α_i + β_i)

P(¬S | W) = 1 − E[θ_w] = β_w / (α_w + β_w)
P(¬S | I) = 1 − E[θ_i] = β_i / (α_i + β_i)
```

```math
// full update rule · after observing S
P(W | S) =          P(W) · α_w/(α_w+β_w)
           ──────────────────────────────────────────────────────────────
           P(W) · α_w/(α_w+β_w) + (1−P(W)) · α_i/(α_i+β_i)

// after ¬S: replace α_w with β_w and α_i with β_i above
// α_w, β_w, α_i, β_i are fixed within a round — they come from past rounds
```

How much `P(W)` moves is controlled by the likelihood ratio
`[α_w/(α_w+β_w)] / [α_i/(α_i+β_i)]` — that is, `P(S|W) / P(S|I)`. For Charles, `0.80 / 0.80 = 1`:
S is equally likely under either role, so it leaves `P(W)` unchanged. For Spencer,
`0.80 / 0.20 = 4`: each S quadruples the odds he's the werewolf. Same observation, same rule —
different behavioral history, different inference.

Each observation within the current round produces a single updated number — not a distribution,
just one probability — and that number becomes the new `P(W)` going into the next observation:

```math
// sequential updating within a round · Spencer as example
prior = P(W) = 1/5      → observe S₁  → posterior = P(W | S₁)
prior = P(W | S₁)       → observe S₂  → posterior = P(W | S₁, S₂)
prior = P(W | S₁, S₂)   → observe ¬S₃ → posterior = P(W | S₁, S₂, ¬S₃)

// each posterior is one number, not a distribution
// each posterior becomes the prior for the next observation
```

> **Deeper dive — where the likelihoods come from:** Think of `θ_w` as Charles's true suspicious
> rate as werewolf — a fixed number in [0,1] governing how likely he is to act suspiciously in
> any given round as W. Like the true probability of heads on a coin, it exists independently of
> any particular observation and can never be directly observed — only S or ¬S outcomes in each
> round. It is the *mechanism* connecting past observations to the current round's likelihood:
> past rounds inform `θ_w`, and `θ_w` generates S. Without it, there is no path from "Charles was
> the werewolf in past rounds" to a probability for S.
>
> The full derivation conditions on everything we know throughout:
>
> ```math
> // full outer derivation · let pr = past rounds throughout
> P(W | S, pr) = P(S | W, pr) · P(W | pr) / P(S | pr)
>
> // expanding P(S | pr) via total probability
>
>                P(S | W, pr) · P(W | pr)
>   = ──────────────────────────────────────────────────────────
>     P(S | W, pr) · P(W | pr) + P(S | ¬W, pr) · P(¬W | pr)
> ```
>
> `P(S | W, pr)` has no direct formula — `θ_w` is the intermediate quantity that connects past
> rounds to S. We introduce it via the law of total probability and marginalize over it:
>
> ```math
> // introducing θ_w via law of total probability
> P(S | W, pr)
>
>   = ∫ P(S, θ_w | W, pr) dθ_w
>
>   // expanding the joint via the chain rule
>   = ∫ P(S | θ_w, W, pr) · p(θ_w | pr) dθ_w
>
>   // θ_w is defined as Charles's suspicious rate as werewolf — it already encodes
>   // everything W tells us about S, so W and pr drop out of P(S | θ_w)
>   = ∫ P(S | θ_w) · p(θ_w | pr) dθ_w
>
>   // P(S | θ_w) = θ_w by definition — θ_w is the probability of S given that rate
>   = ∫ θ_w · p(θ_w | pr) dθ_w
>
>   // this last step is definitional — E[X] = ∫ x · p(x) dx for any continuous random variable.
>   // each possible value of θ_w is weighted by its probability density and summed continuously,
>   // the exact continuous analogue of the discrete weighted average Σ xᵢ · P(X = xᵢ)
>   = E[θ_w]
> ```
>
> The last step — `E[θ_w] = α_w / (α_w + β_w)` — only holds because `p(θ_w | pr)` is a Beta
> distribution, whose mean is α/(α+β). Here is where that comes from.
>
> We build `p(θ_w | pr)` by applying Bayes' rule once per past round where Charles was the
> werewolf. Before any data, the prior is Beta(1,1) — flat, every rate equally plausible. Each
> round's likelihood contains only that round's single observation (S or ¬S), and each posterior
> becomes the prior for the next round:
>
> ```math
> // sequential updating · two past rounds, S then ¬S
> // round 1 · prior = Beta(1,1), density = 1 everywhere · observe S₁
> p(θ_w | S₁) ∝ P(S₁ | θ_w) · p(θ_w)
>              = θ_w · 1
>              = θ_w^(2−1) · (1−θ_w)^(1−1)
>              = Beta(2, 1) → becomes prior for round 2
>
> // round 2 · prior = Beta(2,1) from round 1 · observe ¬S₂
> p(θ_w | S₁, ¬S₂) ∝ P(¬S₂ | θ_w) · p(θ_w | S₁)
>                   = (1−θ_w) · θ_w^(2−1) · (1−θ_w)^(1−1)
>                   = θ_w^(2−1) · (1−θ_w)^(2−1)
>                   = Beta(2, 2) → becomes prior for round 3
> ```
>
> No matter how many rounds accumulate, each suspicious observation adds 1 to the exponent on
> `θ_w` and each non-suspicious observation adds 1 to the exponent on `(1−θ_w)` — regardless of
> order. So the sequential updates always produce:
>
> ```math
> // result of sequential updating · α_w and β_w are counts
> p(θ_w | pr) = Beta(α_w, β_w)
>
> // α_w = total suspicious rounds as W
> // β_w = total non-suspicious rounds as W
>
> E[θ_w] = α_w / (α_w + β_w)
> ```
>
> Plugging back into the outer derivation:
>
> ```math
> // final result
> P(W | S, pr)
>
>                [α_w / (α_w+β_w)] · (1/5)
>   = ────────────────────────────────────────────────────────────────────────────
>     [α_w / (α_w+β_w)] · (1/5) + [α_i / (α_i+β_i)] · (4/5)
> ```
>
> Notice there are two separate layers of updating here. `p(θ_w | pr)` is built across past
> rounds — each round where Charles was the werewolf contributing one Bernoulli observation that
> increments `α_w` or `β_w`. The resulting likelihoods `P(S|W)` and `P(S|I)` are then fixed for
> the current round. Meanwhile, `P(W | pr) = 1/5` is updated within the current round — each new
> observation moves it and the posterior becomes the prior for the next observation. Prior and
> likelihood are mathematical roles, not labels for new vs. old data.

> **Fun fact — neural networks as Bayesian reasoners:** The Bayesian framework may be more than a
> metaphor for cognition. Recent work by Kapatsinski (2026) demonstrates that GPT-2 performs
> *adaptive partial pooling*: rare contexts borrow more information from similar contexts, while
> frequent contexts rely on their own specific evidence. This is mathematically equivalent to
> Bayesian hierarchical regression. A neural network trained purely on next-word prediction
> converges on the same inferential solution that a Bayesian statistician derives analytically.

<div class="demo-card" style="margin-top:2rem;">
  <span class="demo-label">// interactive demo · Bayesian updating with Beta priors</span>
  <p class="demo-desc">
    Select a player. The top chart shows their Beta priors built from past rounds: the
    <span style="color:#7c6ef7;font-family:var(--mono);font-size:0.82em;">purple</span> curve
    is <span class="im">θ_w</span> (suspicious rate in role W) and the
    <span style="color:rgba(148,144,168,0.9);font-family:var(--mono);font-size:0.82em;">gray</span>
    curve is <span class="im">θ_i</span> (suspicious rate in role I). Wide overlap
    (Charles) means no S can move <span class="im">P(W)</span>; clear separation
    (Spencer) means each S carries real information.
    Add observations and watch P(W) update below.
  </p>
  <div class="scenario-btns" id="bayes-player-btns" style="margin-bottom:1.25rem;">
    <button class="scenario-btn active" data-aw="8" data-bw="2" data-ab="8" data-bb="2">Charles · always suspicious</button>
    <button class="scenario-btn" data-aw="7" data-bw="3" data-ab="3" data-bb="7">Wyatt · sometimes suspicious</button>
    <button class="scenario-btn" data-aw="8" data-bw="2" data-ab="2" data-bb="8">Spencer · only suspicious as werewolf</button>
  </div>
  <canvas id="prior-canvas" height="120"></canvas>
  <canvas id="bayes-canvas" height="180" style="margin-top:0.75rem;"></canvas>
  <div class="bayes-btns">
    <button class="bayes-btn primary" id="bayes-hit">+ Suspicious</button>
    <button class="bayes-btn" id="bayes-miss">+ Innocent</button>
    <button class="bayes-btn" id="bayes-reset">Reset Round</button>
  </div>
  <div class="bayes-btns" style="margin-top:0.5rem;padding-top:0.75rem;border-top:1px solid var(--border);">
    <span style="font-family:var(--mono);font-size:11px;color:var(--text-muted);align-self:center;">end round →</span>
    <button class="bayes-btn" id="bayes-reveal-wolf">Reveal: Werewolf</button>
    <button class="bayes-btn" id="bayes-reveal-inno">Reveal: Innocent</button>
    <button class="bayes-btn" id="bayes-reset-all" style="margin-left:auto;">Reset All</button>
  </div>
  <div id="bayes-stats">
    Round: <span id="b-round">1</span> &nbsp;|&nbsp;
    n: <span id="b-n">0</span> &nbsp;|&nbsp;
    S: <span id="b-h">0</span> &nbsp;|&nbsp;
    P(W): <span id="b-mean">0.200</span>
  </div>
</div>

The key takeaway: **what you know about a player from past rounds directly shapes what you can
infer from their behavior now.** The priors θ_w and θ_i aren't just background noise. They encode
the entire history of how each player has acted across roles. A player who was always suspicious
as the werewolf *and* always suspicious as an innocent gives you nothing to work with. A player
whose suspicious behavior reliably tracks their role is the one whose actions actually move the
needle.

Which finally settles the Chicago argument, in my favor: "he's always like that" is a genuine
Bayesian prior, exactly as I said that night. Worth being precise about which one, though. It
isn't the prior that gets multiplied by the likelihood in the current round's Bayes' rule, that one is still
`P(W) = 1/5`, same as everyone else at the table, untouched by anything about his personality.
It's a prior *on the parameter that defines the likelihood itself*. `P(S|W) = θ_w` is a function
of θ_w, so before you can even compute that likelihood, you need a belief about θ_w, and
supplying that belief is exactly the job Beta(α_w, β_w) is doing. It just happens that
this particular prior isn't a blank guess: it's the posterior from a separate, earlier Bayesian
problem (his behavioral history across every past round), reused here as a fixed, already-settled
input. 

<script>
(function(){
  var priorCanvas = document.getElementById('prior-canvas');
  var bayesCanvas = document.getElementById('bayes-canvas');
  var pCtx = priorCanvas.getContext('2d');
  var bCtx = bayesCanvas.getContext('2d');
  var DPR = window.devicePixelRatio || 1;

  // Player-specific Beta prior counts (set by button)
  var aw = 8, bw = 2, ab = 8, bb = 2;
  // Initial counts per player — restored on Reset All
  var initAw = 8, initBw = 2, initAb = 8, initBb = 2;
  // Previous round's counts — drawn as faded overlay on prior canvas
  var prevAw = null, prevBw = null, prevAb = null, prevBb = null;
  // Prior P(werewolf) — 1 in 5 players
  var P0 = 0.20;
  var history = [P0];
  var obsTypes = [];  // 'S' or 'I' for each observation
  var roundNum = 1;
  var MAX_OBS = 15;

  // ── Likelihood from prior counts ──
  function updatePWolf(isSuspicious, currentP) {
    var lw = isSuspicious ? aw / (aw + bw) : bw / (aw + bw);
    var li = isSuspicious ? ab / (ab + bb) : bb / (ab + bb);
    var num = currentP * lw;
    var den = num + (1 - currentP) * li;
    return den > 0 ? num / den : currentP;
  }

  function betaPDF(x, alpha, beta) {
    if (x <= 0 || x >= 1) return 0;
    // Unnormalized — B(α,β) constant omitted since we normalize by maxDens for display
    return Math.pow(x, alpha - 1) * Math.pow(1 - x, beta - 1);
  }

  // ── Draw prior canvas (two Beta distributions) ──
  function drawPrior() {
    var ps = window.getComputedStyle(priorCanvas.parentElement);
    var W2 = priorCanvas.parentElement.clientWidth - parseFloat(ps.paddingLeft) - parseFloat(ps.paddingRight);
    priorCanvas.width = W2 * DPR; priorCanvas.height = 120 * DPR;
    priorCanvas.style.width = W2 + 'px'; priorCanvas.style.height = '120px';
    var w = W2 * DPR, h = 120 * DPR;
    pCtx.clearRect(0, 0, w, h);

    var pad = {top: 10 * DPR, right: 20 * DPR, bot: 30 * DPR, left: 20 * DPR};
    var pw = w - pad.left - pad.right, ph = h - pad.top - pad.bot;

    // Sample Beta PDFs
    var N = 200;
    var xs = [], wVals = [], bVals = [];
    for (var i = 0; i <= N; i++) {
      var x = 0.002 + 0.996 * i / N;
      xs.push(x);
      wVals.push(betaPDF(x, aw, bw));
      bVals.push(betaPDF(x, ab, bb));
    }
    var maxDens = Math.max.apply(null, wVals.concat(bVals));
    // Include previous round curves in scale so both are visually comparable
    if (prevAw !== null) {
      for (var i = 0; i <= N; i++) {
        maxDens = Math.max(maxDens, betaPDF(xs[i], prevAw, prevBw), betaPDF(xs[i], prevAb, prevBb));
      }
    }
    if (maxDens <= 0) maxDens = 1;

    function toX(x) { return pad.left + pw * x; }
    function toY(d) { return pad.top + ph * (1 - d / maxDens); }
    var baseline = pad.top + ph;

    // Clip to plot rect
    pCtx.save(); pCtx.beginPath(); pCtx.rect(pad.left, pad.top, pw, ph); pCtx.clip();

    // Previous round distributions (faded dashed overlay)
    if (prevAw !== null) {
      pCtx.setLineDash([3 * DPR, 3 * DPR]);
      pCtx.lineWidth = 1;
      pCtx.strokeStyle = 'rgba(148,144,168,0.30)';
      pCtx.beginPath();
      for (var i = 0; i <= N; i++) {
        var d = betaPDF(xs[i], prevAb, prevBb);
        if (i === 0) pCtx.moveTo(toX(xs[i]), toY(d));
        else pCtx.lineTo(toX(xs[i]), toY(d));
      }
      pCtx.stroke();
      pCtx.strokeStyle = 'rgba(124,110,247,0.30)';
      pCtx.beginPath();
      for (var i = 0; i <= N; i++) {
        var d = betaPDF(xs[i], prevAw, prevBw);
        if (i === 0) pCtx.moveTo(toX(xs[i]), toY(d));
        else pCtx.lineTo(toX(xs[i]), toY(d));
      }
      pCtx.stroke();
      pCtx.setLineDash([]);
    }

    // Draw θ_i (innocent) — gray, behind
    pCtx.beginPath();
    pCtx.moveTo(toX(xs[0]), baseline);
    for (var i = 0; i <= N; i++) pCtx.lineTo(toX(xs[i]), toY(bVals[i]));
    pCtx.lineTo(toX(xs[N]), baseline);
    pCtx.closePath();
    pCtx.fillStyle = 'rgba(148,144,168,0.18)';
    pCtx.fill();
    pCtx.strokeStyle = 'rgba(148,144,168,0.55)'; pCtx.lineWidth = 1.5;
    pCtx.beginPath();
    for (var i = 0; i <= N; i++) {
      if (i === 0) pCtx.moveTo(toX(xs[i]), toY(bVals[i]));
      else pCtx.lineTo(toX(xs[i]), toY(bVals[i]));
    }
    pCtx.stroke();

    // Draw θ_w (werewolf) — purple, in front
    pCtx.beginPath();
    pCtx.moveTo(toX(xs[0]), baseline);
    for (var i = 0; i <= N; i++) pCtx.lineTo(toX(xs[i]), toY(wVals[i]));
    pCtx.lineTo(toX(xs[N]), baseline);
    pCtx.closePath();
    pCtx.fillStyle = 'rgba(124,110,247,0.22)';
    pCtx.fill();
    pCtx.strokeStyle = 'rgba(124,110,247,0.85)'; pCtx.lineWidth = 2;
    pCtx.beginPath();
    for (var i = 0; i <= N; i++) {
      if (i === 0) pCtx.moveTo(toX(xs[i]), toY(wVals[i]));
      else pCtx.lineTo(toX(xs[i]), toY(wVals[i]));
    }
    pCtx.stroke();

    pCtx.restore(); // end clip

    // X-axis ticks
    pCtx.fillStyle = 'rgba(255,255,255,0.2)'; pCtx.font = (9 * DPR) + 'px "JetBrains Mono"';
    [0, 0.25, 0.5, 0.75, 1.0].forEach(function(v) {
      pCtx.textAlign = v === 0 ? 'left' : (v === 1 ? 'right' : 'center');
      pCtx.fillText(v.toFixed(2), toX(v), baseline + 13 * DPR);
    });

    // X-axis title
    pCtx.fillStyle = 'rgba(255,255,255,0.25)'; pCtx.font = (9 * DPR) + 'px "JetBrains Mono"';
    pCtx.textAlign = 'center';
    pCtx.fillText('θ (suspicious rate)', pad.left + pw / 2, h - 1 * DPR);

    // Legend — top-right, outside clip
    pCtx.font = (9 * DPR) + 'px "JetBrains Mono"'; pCtx.textAlign = 'right';
    pCtx.fillStyle = 'rgba(124,110,247,0.85)';
    pCtx.fillText('θ_w · werewolf', pad.left + pw - 4 * DPR, pad.top + 13 * DPR);
    pCtx.fillStyle = 'rgba(148,144,168,0.75)';
    pCtx.fillText('θ_i · innocent', pad.left + pw - 4 * DPR, pad.top + 25 * DPR);
    if (prevAw !== null) {
      pCtx.fillStyle = 'rgba(255,255,255,0.22)';
      pCtx.fillText('dashed · prev round', pad.left + pw - 4 * DPR, pad.top + 37 * DPR);
    }
  }

  // ── Draw Bayes canvas (P(werewolf) history) ──
  function drawBayes() {
    var ps = window.getComputedStyle(bayesCanvas.parentElement);
    var W2 = bayesCanvas.parentElement.clientWidth - parseFloat(ps.paddingLeft) - parseFloat(ps.paddingRight);
    bayesCanvas.width = W2 * DPR; bayesCanvas.height = 180 * DPR;
    bayesCanvas.style.width = W2 + 'px'; bayesCanvas.style.height = '180px';
    var w = W2 * DPR, h = 180 * DPR;
    bCtx.clearRect(0, 0, w, h);

    var pad = {top: 16 * DPR, right: 20 * DPR, bot: 38 * DPR, left: 52 * DPR};
    var pw = w - pad.left - pad.right, ph = h - pad.top - pad.bot;

    function toX(i) { return pad.left + pw * i / MAX_OBS; }
    function toY(p) { return pad.top + ph * (1 - p); }

    var curP = history[history.length - 1];

    // Clip to plot rect
    bCtx.save(); bCtx.beginPath(); bCtx.rect(pad.left, pad.top, pw, ph); bCtx.clip();

    // Grid lines
    bCtx.strokeStyle = 'rgba(255,255,255,0.05)'; bCtx.lineWidth = 1;
    [0, 0.25, 0.5, 0.75, 1.0].forEach(function(v) {
      bCtx.beginPath(); bCtx.moveTo(pad.left, toY(v)); bCtx.lineTo(pad.left + pw, toY(v)); bCtx.stroke();
    });

    // 0.5 coin-flip reference (dashed)
    bCtx.strokeStyle = 'rgba(255,255,255,0.12)'; bCtx.setLineDash([4 * DPR, 4 * DPR]); bCtx.lineWidth = 1;
    bCtx.beginPath(); bCtx.moveTo(pad.left, toY(0.5)); bCtx.lineTo(pad.left + pw, toY(0.5)); bCtx.stroke();
    bCtx.setLineDash([]);

    // P0 prior reference (dashed)
    bCtx.strokeStyle = 'rgba(124,110,247,0.22)'; bCtx.setLineDash([3 * DPR, 3 * DPR]); bCtx.lineWidth = 1;
    bCtx.beginPath(); bCtx.moveTo(pad.left, toY(P0)); bCtx.lineTo(pad.left + pw, toY(P0)); bCtx.stroke();
    bCtx.setLineDash([]);

    // Observation dots near bottom of plot
    obsTypes.forEach(function(o, i) {
      bCtx.fillStyle = o === 'S' ? 'rgba(239,68,68,0.75)' : 'rgba(52,211,153,0.75)';
      bCtx.beginPath();
      bCtx.arc(toX(i + 0.5), toY(0) - 7 * DPR, 3.5 * DPR, 0, 2 * Math.PI);
      bCtx.fill();
    });

    // P(werewolf) history line
    if (history.length > 1) {
      bCtx.strokeStyle = '#7c6ef7'; bCtx.lineWidth = 2.5; bCtx.lineJoin = 'round';
      bCtx.beginPath();
      history.forEach(function(p, i) {
        if (i === 0) bCtx.moveTo(toX(i), toY(p)); else bCtx.lineTo(toX(i), toY(p));
      });
      bCtx.stroke();
    }

    // Current P dot
    bCtx.fillStyle = '#7c6ef7';
    bCtx.beginPath(); bCtx.arc(toX(history.length - 1), toY(curP), 5 * DPR, 0, 2 * Math.PI); bCtx.fill();

    // Labels inside plot
    bCtx.font = (9 * DPR) + 'px "JetBrains Mono"'; bCtx.textAlign = 'left';
    bCtx.fillStyle = 'rgba(124,110,247,0.5)';
    bCtx.fillText('prior = ' + P0.toFixed(2), pad.left + 4 * DPR, toY(P0) - 4 * DPR);
    bCtx.fillStyle = 'rgba(255,255,255,0.18)';
    bCtx.fillText('coin flip', pad.left + 4 * DPR, toY(0.5) - 4 * DPR);

    bCtx.restore(); // end clip

    // Y-axis labels
    bCtx.fillStyle = 'rgba(255,255,255,0.2)'; bCtx.font = (9 * DPR) + 'px "JetBrains Mono"'; bCtx.textAlign = 'right';
    [0, 0.25, 0.5, 0.75, 1.0].forEach(function(v) {
      bCtx.fillText(v.toFixed(2), pad.left - 4 * DPR, toY(v) + 3 * DPR);
    });

    // Y-axis title (rotated)
    bCtx.save();
    bCtx.translate(12 * DPR, pad.top + ph / 2);
    bCtx.rotate(-Math.PI / 2);
    bCtx.fillStyle = 'rgba(255,255,255,0.2)'; bCtx.font = (9 * DPR) + 'px "JetBrains Mono"'; bCtx.textAlign = 'center';
    bCtx.fillText('P(werewolf)', 0, 0);
    bCtx.restore();

    // X-axis label
    bCtx.fillStyle = 'rgba(255,255,255,0.25)'; bCtx.font = (10 * DPR) + 'px "JetBrains Mono"'; bCtx.textAlign = 'center';
    bCtx.fillText('Observation #', pad.left + pw / 2, h - 5 * DPR);

    // X ticks
    bCtx.fillStyle = 'rgba(255,255,255,0.18)'; bCtx.font = (9 * DPR) + 'px "JetBrains Mono"';
    [0, 5, 10, 15].forEach(function(t) {
      bCtx.textAlign = t === 0 ? 'left' : (t === 15 ? 'right' : 'center');
      bCtx.fillText(String(t), toX(t), pad.top + ph + 14 * DPR);
    });

    // Stats
    var nObs = obsTypes.length;
    var nSus = obsTypes.filter(function(o) { return o === 'S'; }).length;
    document.getElementById('b-round').textContent = roundNum;
    document.getElementById('b-n').textContent = nObs;
    document.getElementById('b-h').textContent = nSus;
    document.getElementById('b-mean').textContent = curP.toFixed(3);
  }

  function draw() { drawPrior(); drawBayes(); }

  function addObs(isSuspicious) {
    if (obsTypes.length >= MAX_OBS) return;
    obsTypes.push(isSuspicious ? 'S' : 'I');
    history.push(updatePWolf(isSuspicious, history[history.length - 1]));
    draw();
  }

  function endRound(wasWerewolf) {
    var nSus = obsTypes.filter(function(o) { return o === 'S'; }).length;
    var nInno = obsTypes.length - nSus;
    prevAw = aw; prevBw = bw; prevAb = ab; prevBb = bb;
    if (wasWerewolf) { aw += nSus; bw += nInno; }
    else             { ab += nSus; bb += nInno; }
    roundNum++;
    history = [P0]; obsTypes = [];
    draw();
  }

  // Player buttons
  document.querySelectorAll('#bayes-player-btns .scenario-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      document.querySelectorAll('#bayes-player-btns .scenario-btn').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      aw = parseInt(btn.dataset.aw); bw = parseInt(btn.dataset.bw);
      ab = parseInt(btn.dataset.ab); bb = parseInt(btn.dataset.bb);
      initAw = aw; initBw = bw; initAb = ab; initBb = bb;
      prevAw = null; prevBw = null; prevAb = null; prevBb = null;
      history = [P0]; obsTypes = []; roundNum = 1;
      draw();
    });
  });

  document.getElementById('bayes-hit').addEventListener('click', function() { addObs(true); });
  document.getElementById('bayes-miss').addEventListener('click', function() { addObs(false); });
  document.getElementById('bayes-reset').addEventListener('click', function() {
    history = [P0]; obsTypes = []; draw();
  });
  document.getElementById('bayes-reveal-wolf').addEventListener('click', function() { endRound(true); });
  document.getElementById('bayes-reveal-inno').addEventListener('click', function() { endRound(false); });
  document.getElementById('bayes-reset-all').addEventListener('click', function() {
    aw = initAw; bw = initBw; ab = initAb; bb = initBb;
    prevAw = null; prevBw = null; prevAb = null; prevBb = null;
    history = [P0]; obsTypes = []; roundNum = 1; draw();
  });
  window.addEventListener('resize', draw);
  draw();
})();
</script>
