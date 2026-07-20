---
title: Distributed Mental Representations
date: 2026-07-19
summary: Meaning isn't stored in a single place. It's distributed across overlapping patterns of neural activation, shaped by every context a word has appeared in.
---

### The case against one entry per word

How is meaning represented in the brain? There's no simple answer: cognitive science has argued
about this for decades. But it's worth being concrete about the alternative being ruled out,
because it's a natural first guess: maybe there's something like a "dog neuron," a
single dedicated unit (or a small, clean cluster of them) that lights up for the concept *dog* and
nothing else, the way a row in a database is either there or it isn't. This idea has a real name in
neuroscience: the **grandmother cell** hypothesis, named after an anecdote the neurophysiologist
Jerry Lettvin used in an MIT lecture around 1969, about a hypothetical surgeon who removes the one
neuron that recognizes your grandmother (Lettvin's own version of the story was never published;
the full history of how it entered the neuroscience literature is traced in @gross2002), and while it's a
perfectly coherent hypothesis, it's also one we have good reason to reject as the general story,
for a few converging reasons.

First, a scaling argument: a person can
recognize an effectively unbounded number of concepts, and an even larger number of *combinations*
of concepts (not just *dog*, but *your neighbor's three-legged dog barking at the mail truck last
Tuesday*). A theory that needs one dedicated cell per concept runs out of cells long before it runs
out of concepts to represent. A distributed representation doesn't have this problem, for a simple
combinatorial reason: a population of N units, each of which can be more-or-less active rather
than strictly on or off, can in principle distinguish far more than N patterns, because the
*pattern of relative activation across the whole population* is doing the encoding, not any single
unit's on/off state. Compare it to color vision: the human eye has only three types of cone cell,
each broadly tuned to a range of wavelengths with heavy overlap, and yet the specific *ratio* of
activation across those three types lets you distinguish millions of colors. No single cone is
"the crimson cone"; crimson is a pattern across all three.

Second, the behavioral evidence doesn't look like what you'd expect from a clean, symbolic
one-entry-per-word system. If retrieving a word meant flipping on one dedicated unit, you'd expect
retrieval to be all-or-nothing: either the entry is accessible or it isn't. Instead, the
overwhelmingly common experience is the *tip-of-the-tongue* state: you can't produce the word, but
you can often say how many syllables it has, what it sounds like, or a near-miss that's clearly
"in the neighborhood," which is exactly what partial activation of a distributed pattern would
predict and hard to explain if the word were a single indivisible symbol you either have or don't.
Similarly, brain damage or degenerative disease essentially never knocks out one specific word
while leaving every semantically related word untouched, the way deleting one row from a database
would; the deficits that do occur tend to be graded and to cluster across related concepts, not
surgically isolated to individual words.

None of this means grandmother cells are a myth. Rodrigo Quiroga and colleagues [@quiroga2005],
recording directly from single neurons in the human medial temporal lobe (in epilepsy patients undergoing
electrode monitoring for surgery), found a single neuron that fired when patients were shown
photographs of the actor Jennifer Aniston, but not when they were shown photographs of other
people, the so-called "Jennifer Aniston neuron" (other neurons in the same study responded just as
selectively to a person's name in written text, not only their picture), and since generalized to a
broader class of sparse, highly selective **concept cells**.
Decades earlier, Horace Barlow [@barlow1972] had actually argued for something like this on
theoretical grounds, explicitly rejecting a fully distributed, combinatorial code in favor of
perception resting on a modest number of highly selective "cardinal cells," each corresponding to
something roughly as complex as a word. So the real picture is more interesting than a clean
binary: highly selective single neurons do exist, but as the minority pattern, not the rule.
Something similar shows up in my own research, too, where high-frequency linguistic constructions
seem to be represented in an item-specific manner. The working picture in the field is thus
closer to *dense, distributed* representations.

### A less computer-science-flavored way to say the same thing

Part of why this took so long to sort out is that the dominant metaphor for the mind, for most of
the twentieth century, was a very specific kind of computer: a serial, symbol-manipulating one that
reads a symbol, applies a rule, and writes the next symbol, one step at a time. That's a good
description of a CPU executing a program. It's a much worse description of a brain. When David
Rumelhart, Jay McClelland, and the Parallel Distributed Processing (PDP) research group made this
case in their landmark books [@rumelhart1986], their alternative was a system built from many
simple units, all active *at once*, individually meaningless on their own. In their system, a concept is the
specific pattern of activity spread across the whole population of neurons rather than a symbol sitting in a
single memory slot. That shift, from one symbol in one place to a pattern spread across many
places, is the idea this post is about, and among the ideas cognitive science was arguing about in
the 1980s, it's held up unusually well.

### Distributed representations, made concrete

Applied to language, this is usually called a **distributed representation**: no single neuron
"holds" the word *dog*. Instead, meaning is a pattern of activation spread across millions of
interconnected neurons: which neurons fire, and how strongly each one fires, together encode the
concept, shaped by every context in which that word has ever appeared. Two consequences fall out
of this immediately, and they're both visible in the demo below. First, related concepts share
*part* of their pattern rather than being either identical or unrelated: *dog* and *cat* overlap
heavily (both mammals, both common pets, both appearing in similar sentences), *dog* and *oak*
barely overlap at all. Second, there's no reason the shared part has to be small or simple; it can
be a large, structured chunk of the population, which is what lets fine-grained similarity (dog is
closer to wolf than to rabbit) sit naturally alongside coarse-grained similarity (all six animals
share a "living thing" core that the six plants don't). In fact, even within a category, specific dogs can be more or less "dog-like" depending on how much overlap the activation for the specific dog is to the rest of dogs.

You can get a feel for this below. Click words from the two groups. Notice that words within the
same category activate **overlapping but distinct** patterns, while words from different
categories share only a small core encoding general biological knowledge.

<div class="demo-card">
  <span class="demo-label">// interactive demo · distributed neural activation</span>
  <div id="brain-wrap">
    <canvas id="brain-canvas"></canvas>
  </div>
  <div class="group-row">
    <div class="group-set">
      <span class="group-set-label animal">Animals</span>
      <button class="word-pill" data-word="wolf"   data-group="animal">wolf</button>
      <button class="word-pill" data-word="dog"    data-group="animal">dog</button>
      <button class="word-pill" data-word="cat"    data-group="animal">cat</button>
      <button class="word-pill" data-word="rabbit" data-group="animal">rabbit</button>
      <button class="word-pill" data-word="fox"    data-group="animal">fox</button>
      <button class="word-pill" data-word="bear"   data-group="animal">bear</button>
    </div>
    <div class="group-set">
      <span class="group-set-label plant">Plants</span>
      <button class="word-pill" data-word="oak"  data-group="plant">oak</button>
      <button class="word-pill" data-word="rose" data-group="plant">rose</button>
      <button class="word-pill" data-word="fern" data-group="plant">fern</button>
      <button class="word-pill" data-word="moss" data-group="plant">moss</button>
      <button class="word-pill" data-word="ivy"  data-group="plant">ivy</button>
      <button class="word-pill" data-word="reed" data-group="plant">reed</button>
    </div>
  </div>
  <p class="brain-caption">Within-category words share most of their pattern. Cross-category words share only a small "living things" core.</p>
  <p class="brain-caption" style="margin-top:0.35rem;opacity:0.6;">Neuron overlap is weighted by GloVe 50d cosine similarity, so dog/cat share more than dog/wolf, and animals share little with plants. Layout is illustrative, not measured neural data.</p>
</div>

### Why go to the trouble?

The most intuitive advantage of a distributed representation is that it makes categories *graded* instead
of all-or-nothing. Classical symbolic accounts of concepts tried to define a category as a fixed
list of necessary and sufficient features (a *bird* is a thing with feathers, that lays eggs,
that flies, and so on) and then hit the same problem over and over: real categories are full of
exceptions that a strict feature list can't absorb. A dog that's lost a leg in an accident is
obviously still a dog. A penguin doesn't fly, and is still obviously a bird. A person born without
an arm is still, just as obviously, a person. A rigid feature list has no graceful way to handle
any of this: every exception either breaks the definition or has to be bolted on as an ad hoc
patch. A population of neurons voting on a graded, high-dimensional pattern has no such problem:
the three-legged dog just lands a little further from the *dog* prototype than a four-legged one,
not outside some hard boundary. This is essentially the same insight behind Eleanor Rosch's work
on prototype theory [@rosch1975], the idea that real categories are organized around a graded
notion of typicality rather than a checklist of defining features (though many other competing theories, such as various exemplar theories, are also compatible with distributed representations).

There's a second advantage that's easy to miss: this is exactly the computational move that makes
modern word embeddings work, including the GloVe vectors driving the demo above. The
distributional hypothesis behind them, the idea that you shall know a word by the company it
keeps, as J.R. Firth put it [@firth1957], says a word's meaning can be approximated by the
statistical pattern of contexts it appears in. Train a model to predict context from co-occurrence
statistics at large enough scale, and the vector it lands on for *dog* ends up close to *cat* and
far from *oak* for essentially the same reason the demo's neuron patterns overlap: both are
compressed summaries of shared usage history, not lookups into a symbolic dictionary entry.

This isn't only a computational analogy: it's been tested directly against real brain activity.
Tom Mitchell and colleagues [@mitchell2008] trained a model to predict fMRI activation patterns
for concrete nouns from each word's co-occurrence statistics with a small set of sensory-motor
verbs (*eat*, *touch*, *hear*, and so on), then used it to predict the brain-activity pattern for
nouns it had never seen during training, and to pick out which of two held-out words a novel
activation pattern belonged to at well above chance. That's a genuinely strong result: it means
the distributed, statistically-derived structure a model like this learns from text isn't just a
useful engineering trick, it's recoverable from measured neural activity for the same words.

### How many concepts can you actually pack in?

So distributed codes capture graded meaning and line up with real brain activity. But there's a
more basic question sitting underneath both of those results, one this post raised at the very
start and then left hanging: if you're not spending one dedicated unit per concept, how many
concepts can a fixed number of units actually hold? Recall the scaling argument from the "case
against one entry per word" section: a population of *d* units can in
principle distinguish far more than *d* patterns. It's worth being precise about
*how much* more, because this turns out to be an actual theorem, not just an intuition, and it's
become one of the central tools in how machine learning researchers now reverse-engineer trained
neural networks.

Start with the geometry. In a *d*-dimensional space, you can fit at most *d* vectors that are all
perfectly orthogonal to each other (at right angles, zero overlap). But if you're willing to
tolerate a little overlap (vectors that are only *almost* orthogonal, with some small nonzero dot
product between them), the number you can fit grows explosively, roughly exponentially in *d*
rather than linearly. This isn't a hand-wavy claim; it's the content of the Johnson–Lindenstrauss
lemma [@johnson1984], a classical result in high-dimensional geometry showing that a large set of
points can be projected into a much lower-dimensional space while approximately preserving how far
apart they all are, provided you accept a small, controllable amount of distortion. Nearly
orthogonal directions are simply far more abundant than exactly orthogonal ones.

Here's the picture underneath that claim: a dot product is a projection, the "shadow" one vector
casts on another's direction, and that shadow shrinks to nothing at a right angle.

<div class="demo-card">
  <span class="demo-label">// figure · what a 90° angle means for shared information</span>
  <svg viewBox="0 0 600 190" width="100%" height="auto" style="max-width:600px;display:block;margin:0 auto;">
    <defs>
      <marker id="arrow-accent" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6 Z" fill="#7c6ef7" />
      </marker>
      <marker id="arrow-muted" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6 Z" fill="rgba(240,239,245,0.55)" />
      </marker>
    </defs>
    <g>
      <line x1="30" y1="150" x2="136" y2="150" stroke="rgba(240,239,245,0.55)" stroke-width="2" marker-end="url(#arrow-muted)" />
      <line x1="30" y1="150" x2="129.6" y2="113.8" stroke="#7c6ef7" stroke-width="2" marker-end="url(#arrow-accent)" />
      <line x1="129.6" y1="113.8" x2="129.6" y2="150" stroke="rgba(240,239,245,0.4)" stroke-width="1.2" stroke-dasharray="3,3" />
      <line x1="30" y1="150" x2="129.6" y2="150" stroke="#6fe695" stroke-width="4" />
      <text x="52" y="136" fill="rgba(240,239,245,0.7)" font-size="11" font-family="JetBrains Mono, monospace">20°</text>
      <text x="80" y="178" fill="#6fe695" font-size="10.5" text-anchor="middle" font-family="JetBrains Mono, monospace">big shadow</text>
    </g>
    <g transform="translate(200,0)">
      <line x1="30" y1="150" x2="136" y2="150" stroke="rgba(240,239,245,0.55)" stroke-width="2" marker-end="url(#arrow-muted)" />
      <line x1="30" y1="150" x2="83" y2="58.2" stroke="#7c6ef7" stroke-width="2" marker-end="url(#arrow-accent)" />
      <line x1="83" y1="58.2" x2="83" y2="150" stroke="rgba(240,239,245,0.4)" stroke-width="1.2" stroke-dasharray="3,3" />
      <line x1="30" y1="150" x2="83" y2="150" stroke="#6fe695" stroke-width="4" />
      <text x="42" y="128" fill="rgba(240,239,245,0.7)" font-size="11" font-family="JetBrains Mono, monospace">60°</text>
      <text x="56" y="178" fill="#6fe695" font-size="10.5" text-anchor="middle" font-family="JetBrains Mono, monospace">smaller shadow</text>
    </g>
    <g transform="translate(400,0)">
      <line x1="30" y1="150" x2="136" y2="150" stroke="rgba(240,239,245,0.55)" stroke-width="2" marker-end="url(#arrow-muted)" />
      <line x1="30" y1="150" x2="30" y2="44" stroke="#7c6ef7" stroke-width="2" marker-end="url(#arrow-accent)" />
      <line x1="30" y1="44" x2="30" y2="150" stroke="rgba(240,239,245,0.4)" stroke-width="1.2" stroke-dasharray="3,3" />
      <path d="M30,142 L38,142 L38,150" fill="none" stroke="rgba(240,239,245,0.55)" stroke-width="1.2" />
      <circle cx="30" cy="150" r="4" fill="#6fe695" />
      <text x="40" y="130" fill="rgba(240,239,245,0.7)" font-size="11" font-family="JetBrains Mono, monospace">90°</text>
      <text x="30" y="178" fill="#6fe695" font-size="10.5" text-anchor="middle" font-family="JetBrains Mono, monospace">zero shadow</text>
    </g>
  </svg>
  <p style="font-family:var(--mono);font-size:11px;color:var(--text-muted);margin-top:0.75rem;text-align:center;">
    The purple arrow's shadow on the gray reference direction (green) shrinks as the angle between them grows, vanishing entirely at 90°. That vanishing shadow <em>is</em> the dot product: zero shadow means zero dot product, which means moving along one direction leaves your position along the other completely unaffected, exactly what "no shared information" means in coordinates.
  </p>
</div>

That figure makes one half of the formula `u · v = ‖u‖ ‖v‖ cos θ` visible: the `cos θ` half, the
part that depends purely on angle. But it does that by holding both arrows at the same fixed
length across all three panels, so it can't show the other half: the `‖u‖ ‖v‖` part, where the
dot product also scales with how long the two vectors actually are. A shadow can shrink for two
completely different reasons, a widening angle or a shrinking vector, and the static figure only
has room to demonstrate one of them.

The demo below is the same picture, but with the lengths unlocked. Drag the angle slider and
you'll see the same shrinking-shadow effect as above. Drag either length slider instead, and
watch what moves: stretching *u* stretches the shadow right along with it, while stretching *v*
doesn't move the shadow at all, it only scales the number reported for `u · v`. That split is the
whole content of the formula: the shadow is purely a fact about *u* and the angle, and `‖v‖` only
enters afterward, as a multiplier.

<div class="demo-card">
  <span class="demo-label">// interactive demo · the dot product as a scaled shadow</span>
  <canvas id="dotprod-canvas" height="230"></canvas>
  <div class="slider-row">
    <label>‖u‖ small</label>
    <input type="range" id="dotprod-len" min="0.2" max="1.8" step="0.01" value="1.1" />
    <label class="right">‖u‖ large</label>
  </div>
  <div class="slider-row">
    <label>0°</label>
    <input type="range" id="dotprod-angle" min="0" max="180" step="1" value="35" />
    <label class="right">180°</label>
  </div>
  <div class="slider-row">
    <label>‖v‖ small</label>
    <input type="range" id="dotprod-vlen" min="0.2" max="1.8" step="0.01" value="1.0" />
    <label class="right">‖v‖ large</label>
  </div>
  <p style="font-family:var(--mono);font-size:11px;color:var(--text-muted);margin-top:0.75rem;">
    Drag any slider: the dashed line is light falling straight down from <em>u</em>'s tip onto
    <em>v</em>'s direction, and the highlighted segment is the resulting shadow. Stretch
    <em>u</em> longer at a fixed angle and the shadow stretches right along with it, the one thing
    the static figure above couldn't show. But watch what happens when you stretch <em>v</em>
    instead: the shadow doesn't move at all, it only depends on <em>u</em> and the angle, while the
    displayed u · v scales right up with <em>v</em>'s length. That's the difference between the
    shadow itself and the dot product: `u · v = shadow × ‖v‖`. Past 90° the shadow falls behind the
    origin and the dot product goes negative.
  </p>
</div>

> **Deeper dive: the linear algebra behind "far more than *d*"**. Two facts do all the work
> here: exact orthogonality caps out hard at *d* vectors, and relaxing it to "almost orthogonal"
> breaks that cap completely. Worth slowing down on both, since the whole argument lives in the
> gap between them.
>
> **What orthogonality actually means.** In plain English, two directions are orthogonal if they
> share nothing: moving along one tells you absolutely nothing about your position along the
> other. Geometrically, the two directions are perpendicular. Mathematically, the dot product
> `u · v = Σᵢ uᵢvᵢ` is the standard way to measure how much two vectors *agree* in direction, and
> the geometric reason it does that job is projection. Picture shining a light straight down onto
> the line `v` points along, and looking at the shadow `u` casts on that line: the length of that
> shadow, scaled by how long `v` is, is exactly `u · v`. Two vectors that mostly point the same
> way cast a long shadow on each other: a large dot product, a lot of shared direction. At a right
> angle, that shadow shrinks to nothing no matter how long `u` is: none of `u`'s extent shows up
> along `v`'s direction at all. That's the geometric content of `u · v = ‖u‖ ‖v‖ cos θ`: it comes
> out to exactly zero when `θ = 90°`, because `cos 90° = 0` kills the shadow term completely. In an
> embedding space, if two concept directions are orthogonal, moving along one leaves your position
> along the other completely unchanged, which is exactly what "shares no information" means once
> you're working in coordinates rather than words. That's why "orthogonal" and "dot product equals
> zero" get treated as the same statement from here on: one is the picture, the other is the test
> for it.
>
> **Why orthogonality caps out at exactly *d*, and not one more.** Suppose you have *k* nonzero,
> pairwise orthogonal directions `v_1, ..., v_k` in a *d*-dimensional space. The claim is `k ≤ d`,
> and the proof works by asking a single question: can any *nontrivial* combination of these
> directions, one that doesn't just use all-zero weights, add up to the zero vector? If it could,
> you could rearrange that equation to write one direction as a combination of the rest, meaning it
> wasn't contributing anything the others didn't already cover. Ruling that out for every direction
> at once is exactly what shows each one is doing genuinely separate work, which is the property a
> *d*-dimensional space can only support up to *d* times over (that's what "*d*-dimensional" means).
> So the proof starts by writing down a combination that equals the zero vector, the exact scenario
> that needs ruling out, and shows orthogonality forces every weight in it to be zero.
>
> ```math
> // suppose v_1, ..., v_k are nonzero and pairwise orthogonal: vᵢ · vⱼ = 0 for i ≠ j
> // does SOME nontrivial combination of them reach the zero vector?
> c_1 v_1 + c_2 v_2 + ... + c_k v_k = 0
> ```
>
> That's one equation, but *k* unknowns, the coefficients `c_1, ..., c_k`, all tangled together in
> a single sum. To make progress we need a way to pull just one coefficient back out on its own,
> and that's exactly what dotting both sides with one particular `v_j` does: because the set is
> orthogonal, `vᵢ · vⱼ = 0` for every term where `i ≠ j`, so taking the dot product with `v_j`
> kills every term in the sum except the one that actually involves `v_j`. This move only works
> *because* the set is orthogonal: for a non-orthogonal set the cross terms wouldn't vanish, and
> you'd still be stuck with all *k* unknowns knotted into one equation.
>
> ```math
> // dot both sides with v_j -- orthogonality kills every term except the j-th
> (c_1 v_1 + c_2 v_2 + ... + c_k v_k) · v_j = 0 · v_j
> c_j (v_j · v_j) = 0
> ```
>
> One more small fact closes it out: `v_j · v_j` is a vector dotted with *itself*, which is the
> same `‖u‖ ‖v‖ cos θ` formula with `θ = 0`, so `cos θ = 1` and `v_j · v_j = ‖v_j‖²`, just the
> squared length of `v_j`. Since `v_j` was assumed nonzero, `‖v_j‖²` is a strictly positive number,
> and the only way `c_j` times a positive number can equal zero is if `c_j` itself is zero:
>
> ```math
> c_j ‖v_j‖² = 0     and     ‖v_j‖² > 0     =>     c_j = 0
> ```
>
> Nothing about that argument singled out any particular `j`; the same reasoning applies no matter
> which vector we dotted with, so it holds for every coefficient at once:
> `c_1 = c_2 = ... = c_k = 0`. The only combination that reaches zero is the all-zero one, so none
> of `v_1, ..., v_k` can be rebuilt out of a combination of the rest, each one is doing genuinely
> separate work. And a *d*-dimensional space doesn't have room for more than *d* directions doing
> separate work like that: `k ≤ d`. (We'll come back to exactly this ceiling in a later post about
> sparse autoencoders, since prying apart superposed features is fundamentally about working
> around it.)
>
> **From "exactly zero" to "almost zero."** Now relax the requirement: instead of demanding
> `vᵢ · vⱼ = 0`, allow `|vᵢ · vⱼ| ≤ ε` for some small tolerance `ε`, directions that sit close to
> 90° rather than exactly on it. In plain terms, "exactly perpendicular" is one single angle out of
> an entire continuum of possible angles: an extremely narrow target. "Within ε of perpendicular"
> is a far more generous target, and in high dimensions that generosity turns out to be enormous.
> That gap, zero tolerance versus a little tolerance, is where the whole exponential blowup comes
> from.
>
> Rather than try to build such a large set of almost-orthogonal directions by hand, ask a
> different question: if you just pick directions *at random*, how likely are they to already be
> almost orthogonal? This is the **probabilistic method** as a proof strategy: instead of
> constructing an object directly, show that a random guess succeeds with high enough probability,
> which proves a successful object must exist somewhere, even without ever writing one down.
>
> ```math
> // two random unit vectors in d dimensions -- how close to orthogonal are they, typically?
> u, v ~ random unit vectors in R^d, drawn independently
> u · v = Σᵢ uᵢvᵢ              E[uᵢ · vᵢ] = 0 for each i
> ```
>
> Each term `uᵢvᵢ` in that sum is a small random number, positive or negative with roughly equal
> chance, since `u` and `v` are independent random directions with no reason to line up on any
> particular coordinate. Across *d* coordinates, the positive and negative contributions tend to
> cancel rather than pile up in one direction, the same reason the running imbalance in a long
> sequence of coin flips shrinks *relative to the number of flips* the longer you keep flipping.
> More coordinates to sum over means more opportunity for cancellation, so the total concentrates
> more tightly around zero as *d* grows:
>
> ```math
> SD(u · v) ≈ 1 / √d
> ```
>
> **Packing many at once.** That already says a *single random pair* is close to orthogonal for
> large *d*, essentially for free. But storing many concepts needs a whole *set* of *N* directions
> that are all pairwise almost orthogonal *at once*, not just one lucky pair, so the real question
> is how large *N* can get before some pair among them breaks the ε tolerance.
>
> ```math
> // draw N random unit vectors -- there are ~N²/2 pairs that could break the tolerance
> // each single pair's failure probability shrinks exponentially in d (concentration of
> // measure on the sphere -- exact constants vary by derivation):
> P(one pair exceeds ε)               ≲ exp(−d·ε² / 2)
>
> // "union bound": the chance that AT LEAST ONE of many events happens is at most the
> // sum of their individual chances -- a crude bound, but always valid and easy to use,
> // which matters here because computing the exact joint probability directly is hard
> P(some pair among all N exceeds ε)  ≲ N² · exp(−d·ε² / 2)
> ```
>
> Solve for how large `N` can be while keeping that total risk below 1:
>
> ```math
> N² · exp(−d·ε² / 2) < 1
> N² < exp(d·ε² / 2)
> N  < exp(d·ε² / 4)
> ```
>
> Here's why that comes out exponential rather than linear: the per-pair failure probability
> shrinks *exponentially* in *d*, so it can absorb a number of pairs that itself grows
> exponentially in *d* before the total risk climbs back up to 1, and because the number of pairs
> grows like `N²`, letting the pair count grow exponentially means `N` itself grows like the square
> root of that exponential, which is still exponential (just with a smaller rate in the exponent).
> That's the whole mechanism in one line: concentration of measure makes near-orthogonality
> overwhelmingly likely once there are enough dimensions to spread the residual overlap thin
> across, and thin-enough overlap can be shared by exponentially many directions at once.
>
> Because the total failure probability came out below 1, failure can't be happening on *every*
> random draw, so on at least some fraction of draws, all `N` vectors land within `ε` of mutually
> orthogonal. A satisfying configuration must therefore exist, even though nothing here ever
> constructed one by hand. That's the gap the superposition hypothesis exploits: swap exact
> orthogonality for approximate, and the ceiling on how many concepts fit in *d* dimensions jumps
> from *d* to exponential in *d*.

Whether or not you followed the algebra above, the headline claim is simple: relaxing exact
orthogonality to a small tolerance ε should let you pack in far more than *d* directions, and the
demo below lets you watch that happen rather than take it on faith. At each dimension *d*, it
starts from *d* exactly-orthogonal directions (the hard cap this section opened with, drawn as the
dashed line below) and greedily tries to add more random directions on top, keeping any candidate
that stays within ε of orthogonal to every direction already kept. Whatever it manages to add
beyond *d* is the extra capacity ε buys you, plotted on a log scale.

<div class="demo-card">
  <span class="demo-label">// interactive demo · how many near-orthogonal directions fit in d dimensions</span>
  <canvas id="capacity-canvas" height="340"></canvas>
  <div class="slider-row">
    <label>Tight (ε=0.15)</label>
    <input type="range" id="capacity-slider" min="0.15" max="0.4" step="0.01" value="0.3" />
    <label class="right">Loose (ε=0.4)</label>
  </div>
  <p style="font-family:var(--mono);font-size:11px;color:var(--text-muted);margin-top:0.75rem;">
    Each dimension starts from a guaranteed-valid set of exactly <em>d</em> exactly-orthogonal
    directions, then 500 random unit vectors are drawn and greedily added on top whenever a
    candidate stays within ε of orthogonal to every direction already kept (an empirical
    illustration, not the theoretical bound itself, so the purple line can only sit at or above
    the dashed <em>d</em> cap, never below it). Drag the slider and release: below a threshold ε
    the purple line just traces the dashed one exactly, no room to add anything; past that
    threshold it peels away fast, the same kind of sharp transition Elhage and colleagues found
    for superposition itself.
  </p>
</div>

This is exactly the mechanism behind the **superposition hypothesis** in current mechanistic
interpretability research on large language models. Elhage and colleagues [@elhage2022] trained
small networks to represent more input features than they had hidden dimensions, and asked when
and how the network manages it. The answer: if the features are *sparse*, rarely more than a
handful active on any given input, the network learns to assign them almost-orthogonal directions
that share the same dimensions, tolerating a bit of mutual interference because any two
interfering features are unlikely to both be "on" at once. They found a sharp phase transition
between a regime where the network keeps important features in their own dedicated dimension (much
like a grandmother cell) and a regime where it packs many more features than it has dimensions into
superposition, governed by exactly two things: how sparse the features are, and the ratio of
features to dimensions: a direct, quantitative descendant of the same population-coding argument
from the top of this post, now with a precise answer for how much capacity you actually get.

The follow-up work made this concrete rather than theoretical. Bricken and colleagues
[@bricken2023] applied a **sparse autoencoder** (an algorithm built specifically to unpack a
superposed representation back into its individual, disentangled features) to a real trained
language model, and recovered thousands of individually interpretable features from a layer with
only a few hundred neurons: features for specific things like base64 strings, Arabic script, or
DNA sequences, each cleanly separable despite sharing the same cramped neuron space. That's the
modern, quantitative version of the very question this post opened with. Is meaning one dedicated
unit per concept, or a pattern spread across a population? Inside a trained neural network, the
answer now comes with a number attached: far more concepts than dimensions, exactly as many as the
sparsity of those concepts' co-occurrence will allow.

The same technique extends past text, too. Pluth and colleagues [@pluth2026] applied sparse
autoencoders to Whisper, a speech-recognition model, and found diverse monosemantic features
spanning both linguistic and non-linguistic distinctions in its encoder representations, with some
of those features steerable across languages, superposition and all the capacity it buys showing
up in an acoustic model exactly the way it does in a language model.

None of this is free, though. A representation spread across a large, overlapping population is
harder to inspect and reason about than a clean symbolic label: you can't point to "the dog
neuron" and explain what it's doing the way you could point to a line in a lookup table. Overlap
that buys you graceful generalization can also cause interference: teach a distributed network a
new pattern that shares a lot of structure with an old one, and the old pattern can degrade,
an effect connectionist researchers call *catastrophic interference*. Symbolic, localist codes
don't have this failure mode, precisely because they don't share resources across items in the
first place. The brain's actual solution to this tradeoff, how it gets the graded generalization of
a distributed code without losing everything it already knew, is still a live research question,
and one worth its own post.

<script>
(function () {
  function makeRng(seed) {
    var s = seed >>> 0;
    return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  }

  function randomUnitVector(d, rand) {
    var v = new Array(d);
    for (var i = 0; i < d; i += 2) {
      var u1 = Math.max(rand(), 1e-12), u2 = rand();
      var r = Math.sqrt(-2 * Math.log(u1)), th = 2 * Math.PI * u2;
      v[i] = r * Math.cos(th);
      if (i + 1 < d) v[i + 1] = r * Math.sin(th);
    }
    var norm = 0;
    for (var i = 0; i < d; i++) norm += v[i] * v[i];
    norm = Math.sqrt(norm);
    for (var i = 0; i < d; i++) v[i] /= norm;
    return v;
  }

  function dot(a, b) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }

  function packCount(d, eps, attempts, rand) {
    // seed with the d standard basis vectors: exactly orthogonal, so trivially
    // within any eps >= 0 tolerance -- guarantees the count can never fall
    // below the hard d cap, then greedily tries to add more on top of that
    var accepted = [];
    for (var b = 0; b < d; b++) {
      var e = new Array(d).fill(0); e[b] = 1;
      accepted.push(e);
    }
    for (var a = 0; a < attempts; a++) {
      var cand = randomUnitVector(d, rand);
      var ok = true;
      for (var i = 0; i < accepted.length; i++) {
        if (Math.abs(dot(cand, accepted[i])) > eps) { ok = false; break; }
      }
      if (ok) accepted.push(cand);
    }
    return accepted.length;
  }

  var DIMS = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40];
  var ATTEMPTS = 500, YMAX = 600, YMIN = 1, PAD = 52;

  var canvas = document.getElementById('capacity-canvas'), cctx = canvas.getContext('2d');
  var cslider = document.getElementById('capacity-slider');
  var cDPR = window.devicePixelRatio || 1;
  var cW, cH, counts = [];

  function cResize() {
    cW = canvas.parentElement.clientWidth; cH = 340;
    canvas.width = cW * cDPR; canvas.height = cH * cDPR;
    canvas.style.width = cW + 'px'; canvas.style.height = cH + 'px';
  }

  function xForDim(d) {
    var pad = PAD * cDPR, pw = cW * cDPR - pad * 2;
    var t = (d - DIMS[0]) / (DIMS[DIMS.length - 1] - DIMS[0]);
    return pad + t * pw;
  }
  function yForVal(v) {
    var pad = PAD * cDPR, ph = cH * cDPR - pad * 2;
    var vv = Math.max(v, YMIN);
    var t = (Math.log(vv) - Math.log(YMIN)) / (Math.log(YMAX) - Math.log(YMIN));
    return pad + (1 - t) * ph;
  }

  var curEps = 0.3;

  function cRecompute() {
    curEps = parseFloat(cslider.value);
    var rand = makeRng(964);
    counts = DIMS.map(function (d) { return packCount(d, curEps, ATTEMPTS, rand); });
    cDraw();
  }

  function cDraw() {
    var w = cW * cDPR, h = cH * cDPR, pad = PAD * cDPR;
    cctx.clearRect(0, 0, w, h);

    [1, 10, 100, 600].forEach(function (tick) {
      var y = yForVal(tick);
      cctx.strokeStyle = 'rgba(255,255,255,0.06)'; cctx.lineWidth = 1;
      cctx.beginPath(); cctx.moveTo(pad, y); cctx.lineTo(w - pad, y); cctx.stroke();
      cctx.font = (10 * cDPR) + 'px "JetBrains Mono"'; cctx.fillStyle = 'rgba(240,239,245,0.4)'; cctx.textAlign = 'right';
      cctx.fillText(String(tick), pad - 6 * cDPR, y + 3 * cDPR);
    });
    DIMS.forEach(function (d) {
      var x = xForDim(d);
      cctx.font = (10 * cDPR) + 'px "JetBrains Mono"'; cctx.fillStyle = 'rgba(240,239,245,0.4)'; cctx.textAlign = 'center';
      cctx.fillText(String(d), x, h - pad + 16 * cDPR);
    });

    // dashed cap line drawn wider than the solid line on top of it, so it
    // still peeks out as a visible track even where the two exactly coincide
    cctx.setLineDash([6 * cDPR, 5 * cDPR]);
    cctx.strokeStyle = 'rgba(240,239,245,0.5)'; cctx.lineWidth = 5 * cDPR;
    cctx.lineCap = 'round';
    cctx.beginPath();
    DIMS.forEach(function (d, i) {
      var x = xForDim(d), y = yForVal(d);
      if (i === 0) cctx.moveTo(x, y); else cctx.lineTo(x, y);
    });
    cctx.stroke();
    cctx.setLineDash([]);

    cctx.strokeStyle = '#7c6ef7'; cctx.lineWidth = 2.2 * cDPR;
    cctx.beginPath();
    DIMS.forEach(function (d, i) {
      var x = xForDim(d), y = yForVal(counts[i]);
      if (i === 0) cctx.moveTo(x, y); else cctx.lineTo(x, y);
    });
    cctx.stroke();
    DIMS.forEach(function (d, i) {
      var x = xForDim(d), y = yForVal(counts[i]);
      cctx.beginPath(); cctx.arc(x, y, 3.5 * cDPR, 0, Math.PI * 2);
      cctx.fillStyle = '#7c6ef7'; cctx.fill();
      // exact value label on every point, so the log-scale position is never
      // ambiguous: you can read the number instead of eyeballing the axis
      cctx.font = (9.5 * cDPR) + 'px "JetBrains Mono"'; cctx.fillStyle = '#c9c3ff'; cctx.textAlign = 'center';
      cctx.fillText(String(counts[i]), x, y - 8 * cDPR);
    });

    var lastD = DIMS[DIMS.length - 1];
    var yEmp = yForVal(counts[counts.length - 1]), yCap = yForVal(lastD);
    cctx.textAlign = 'right'; cctx.font = 'bold ' + (11 * cDPR) + 'px "JetBrains Mono"';
    cctx.fillStyle = '#7c6ef7';
    cctx.fillText('within ε=' + curEps.toFixed(2) + ' of orthogonal', w - pad, yEmp - 18 * cDPR);
    cctx.fillStyle = 'rgba(240,239,245,0.75)'; cctx.font = (10 * cDPR) + 'px "JetBrains Mono"';
    cctx.fillText('exact cap (=d)', w - pad, yCap + 14 * cDPR);

    cctx.save();
    cctx.font = (11 * cDPR) + 'px "JetBrains Mono"'; cctx.fillStyle = 'rgba(240,239,245,0.5)';
    cctx.textAlign = 'center';
    cctx.fillText('dimension (d)', w / 2, h - 6 * cDPR);
    cctx.translate(16 * cDPR, h / 2); cctx.rotate(-Math.PI / 2);
    cctx.fillText('vectors packed (log scale)', 0, 0);
    cctx.restore();
  }

  var cDebounce = null;
  cslider.addEventListener('input', function () {
    clearTimeout(cDebounce);
    cDebounce = setTimeout(cRecompute, 120);
  });
  window.addEventListener('resize', function () { cResize(); cDraw(); });
  cResize(); cRecompute();
})();
(function () {
  var canvas = document.getElementById('dotprod-canvas'), dctx = canvas.getContext('2d');
  var lenSlider = document.getElementById('dotprod-len');
  var angleSlider = document.getElementById('dotprod-angle');
  var vlenSlider = document.getElementById('dotprod-vlen');
  var dDPR = window.devicePixelRatio || 1;
  var dW, dH, UNIT;

  function dResize() {
    dW = canvas.parentElement.clientWidth; dH = 230;
    canvas.width = dW * dDPR; canvas.height = dH * dDPR;
    canvas.style.width = dW + 'px'; canvas.style.height = dH + 'px';
    UNIT = 95 * dDPR;
  }

  function dDraw() {
    var w = dW * dDPR, h = dH * dDPR;
    dctx.clearRect(0, 0, w, h);

    var L = parseFloat(lenSlider.value);
    var Lv = parseFloat(vlenSlider.value);
    var thetaDeg = parseFloat(angleSlider.value);
    var theta = thetaDeg * Math.PI / 180;
    var ox = w * 0.45, oy = h * 0.62;

    // full reference line through the origin in both directions, so a
    // negative shadow (theta > 90) still has a visible track to land on
    dctx.strokeStyle = 'rgba(240,239,245,0.18)'; dctx.lineWidth = 1 * dDPR;
    dctx.beginPath(); dctx.moveTo(ox - UNIT * 1.9, oy); dctx.lineTo(ox + UNIT * 1.9, oy); dctx.stroke();

    var vx = ox + Lv * UNIT, vy = oy;
    var ux = ox + L * UNIT * Math.cos(theta), uy = oy - L * UNIT * Math.sin(theta);
    // the shadow's position depends only on u and the angle, never on v's
    // length -- that independence is the whole point of this slider
    var px = ux, py = oy;
    var shadow = L * Math.cos(theta);
    var dot = shadow * Lv;

    // light falling straight down from u's tip onto v's line
    dctx.strokeStyle = 'rgba(240,239,245,0.4)'; dctx.lineWidth = 1.2 * dDPR;
    dctx.setLineDash([4 * dDPR, 4 * dDPR]);
    dctx.beginPath(); dctx.moveTo(ux, uy); dctx.lineTo(px, py); dctx.stroke();
    dctx.setLineDash([]);

    // the shadow itself, from the origin to the projection point
    dctx.strokeStyle = '#6fe695'; dctx.lineWidth = 5 * dDPR; dctx.lineCap = 'round';
    dctx.beginPath(); dctx.moveTo(ox, oy); dctx.lineTo(px, py); dctx.stroke();

    // v, the fixed unit reference arrow
    drawArrow(ox, oy, vx, vy, 'rgba(240,239,245,0.6)', 2 * dDPR);
    // u, the adjustable arrow
    drawArrow(ox, oy, ux, uy, '#7c6ef7', 2.2 * dDPR);

    dctx.font = (11 * dDPR) + 'px "JetBrains Mono"'; dctx.textAlign = 'left';
    dctx.fillStyle = 'rgba(240,239,245,0.6)'; dctx.fillText('v', vx + 8 * dDPR, vy + 4 * dDPR);
    dctx.fillStyle = '#c9c3ff'; dctx.fillText('u', ux + 8 * dDPR, uy);

    dctx.textAlign = 'left'; dctx.font = (12 * dDPR) + 'px "JetBrains Mono"';
    dctx.fillStyle = 'rgba(240,239,245,0.75)';
    dctx.fillText('‖u‖=' + L.toFixed(2) + '   ‖v‖=' + Lv.toFixed(2) + '   θ=' + thetaDeg.toFixed(0) + '°   shadow=' + shadow.toFixed(2), 12 * dDPR, 22 * dDPR);
    dctx.fillStyle = '#7c6ef7'; dctx.font = 'bold ' + (13 * dDPR) + 'px "JetBrains Mono"';
    dctx.fillText('u · v = shadow × ‖v‖ = ' + dot.toFixed(2), 12 * dDPR, 44 * dDPR);
  }

  function drawArrow(x1, y1, x2, y2, color, width) {
    dctx.strokeStyle = color; dctx.lineWidth = width; dctx.lineCap = 'round';
    dctx.beginPath(); dctx.moveTo(x1, y1); dctx.lineTo(x2, y2); dctx.stroke();
    var ang = Math.atan2(y2 - y1, x2 - x1), size = 9 * dDPR;
    dctx.beginPath();
    dctx.moveTo(x2, y2);
    dctx.lineTo(x2 - size * Math.cos(ang - Math.PI / 7), y2 - size * Math.sin(ang - Math.PI / 7));
    dctx.lineTo(x2 - size * Math.cos(ang + Math.PI / 7), y2 - size * Math.sin(ang + Math.PI / 7));
    dctx.closePath();
    dctx.fillStyle = color; dctx.fill();
  }

  lenSlider.addEventListener('input', dDraw);
  angleSlider.addEventListener('input', dDraw);
  vlenSlider.addEventListener('input', dDraw);
  window.addEventListener('resize', function () { dResize(); dDraw(); });
  dResize(); dDraw();
})();
(function () {
  var canvas = document.getElementById('brain-canvas');
  var wrap   = document.getElementById('brain-wrap');
  var DPR    = window.devicePixelRatio || 1;
  var W, H, ctx;
  var N_NEURONS = 120;
  var neurons   = [];

  var BIO_IDX    = makeRange(0,  10);
  var ANIMAL_IDX = makeRange(10, 65);
  var PLANT_IDX  = makeRange(65, 120);

  function makeRange(a, b) { var r=[]; for(var i=a;i<b;i++) r.push(i); return r; }

  function seededSample(pool, n, seed) {
    var arr = pool.slice();
    for (var i=arr.length-1; i>0; i--) {
      seed = (seed*1664525+1013904223)>>>0;
      var j = seed%(i+1);
      var t=arr[i]; arr[i]=arr[j]; arr[j]=t;
    }
    return arr.slice(0, n);
  }

  // Conservative ellipse: keeps neurons well inside the visual brain outline
  function insideBrain(nx, ny) {
    var dx = (nx - 0.50) / 0.33;
    var dy = (ny - 0.48) / 0.36;
    return (dx*dx + dy*dy) < 1.0;
  }

  function initNeurons() {
    neurons = [];
    var rng = 12345;
    function rand() { rng=(rng*1664525+1013904223)>>>0; return rng/4294967296; }
    var attempts = 0;
    while (neurons.length < N_NEURONS && attempts < 12000) {
      attempts++;
      var nx = 0.17 + rand()*0.66;
      var ny = 0.12 + rand()*0.72;
      if (insideBrain(nx, ny)) {
        neurons.push({ x: nx, y: ny, r: 1.8 + rand()*1.4 });
      }
    }
  }

  var wordPatterns = {};
  var WORDS_META = [
    {word:'wolf',  group:'animal'},{word:'dog',    group:'animal'},
    {word:'cat',   group:'animal'},{word:'rabbit', group:'animal'},
    {word:'fox',   group:'animal'},{word:'bear',   group:'animal'},
    {word:'oak',   group:'plant'}, {word:'rose',   group:'plant'},
    {word:'fern',  group:'plant'}, {word:'moss',   group:'plant'},
    {word:'ivy',   group:'plant'}, {word:'reed',   group:'plant'},
  ];
  var GROUP_COLOR = { animal:'#7c6ef7', plant:'#6fe695' };

  // Approximate GloVe 50d cosine similarities (computed from pretrained vectors)
  var SIM = {
    wolf:  {wolf:1.00,fox:0.77,bear:0.70,dog:0.74,cat:0.63,rabbit:0.54,oak:0.22,rose:0.19,fern:0.21,moss:0.20,ivy:0.22,reed:0.23},
    fox:   {wolf:0.77,fox:1.00,bear:0.64,dog:0.66,cat:0.61,rabbit:0.54,oak:0.21,rose:0.19,fern:0.20,moss:0.19,ivy:0.21,reed:0.21},
    bear:  {wolf:0.70,fox:0.64,bear:1.00,dog:0.60,cat:0.57,rabbit:0.55,oak:0.23,rose:0.20,fern:0.22,moss:0.21,ivy:0.22,reed:0.23},
    dog:   {wolf:0.74,fox:0.66,bear:0.60,dog:1.00,cat:0.84,rabbit:0.67,oak:0.26,rose:0.24,fern:0.23,moss:0.22,ivy:0.25,reed:0.23},
    cat:   {wolf:0.63,fox:0.61,bear:0.57,dog:0.84,cat:1.00,rabbit:0.71,oak:0.24,rose:0.27,fern:0.23,moss:0.22,ivy:0.26,reed:0.22},
    rabbit:{wolf:0.54,fox:0.54,bear:0.55,dog:0.67,cat:0.71,rabbit:1.00,oak:0.22,rose:0.25,fern:0.22,moss:0.21,ivy:0.23,reed:0.23},
    oak:   {wolf:0.22,fox:0.21,bear:0.23,dog:0.26,cat:0.24,rabbit:0.22,oak:1.00,rose:0.51,fern:0.60,moss:0.57,ivy:0.55,reed:0.53},
    rose:  {wolf:0.19,fox:0.19,bear:0.20,dog:0.24,cat:0.27,rabbit:0.25,oak:0.51,rose:1.00,fern:0.49,moss:0.47,ivy:0.57,reed:0.44},
    fern:  {wolf:0.21,fox:0.20,bear:0.22,dog:0.23,cat:0.23,rabbit:0.22,oak:0.60,rose:0.49,fern:1.00,moss:0.64,ivy:0.56,reed:0.60},
    moss:  {wolf:0.20,fox:0.19,bear:0.21,dog:0.22,cat:0.22,rabbit:0.21,oak:0.57,rose:0.47,fern:0.64,moss:1.00,ivy:0.59,reed:0.62},
    ivy:   {wolf:0.22,fox:0.21,bear:0.22,dog:0.25,cat:0.26,rabbit:0.23,oak:0.55,rose:0.57,fern:0.56,moss:0.59,ivy:1.00,reed:0.52},
    reed:  {wolf:0.23,fox:0.21,bear:0.23,dog:0.23,cat:0.22,rabbit:0.23,oak:0.53,rose:0.44,fern:0.60,moss:0.62,ivy:0.52,reed:1.00}
  };

  function buildPatterns() {
    WORDS_META.forEach(function(m, i) {
      var seed = (i+1)*2311+7;
      var bioSet  = seededSample(BIO_IDX, 7, seed);
      var coreSet = m.group==='animal'
        ? seededSample(ANIMAL_IDX, 33, seed+100)
        : seededSample(PLANT_IDX,  33, seed+200);
      wordPatterns[m.word] = bioSet.concat(coreSet);
    });
  }

  var activeWord=null, activeGroup=null;
  var animLevel={}, animTarget={};

  function setWord(word, group) {
    if (activeWord===word) { activeWord=null; activeGroup=null; }
    else { activeWord=word; activeGroup=group; }
    document.querySelectorAll('.word-pill').forEach(function(p) {
      p.classList.remove('active-animal','active-plant');
      if (p.dataset.word===activeWord) p.classList.add('active-'+activeGroup);
    });
    var targets = [];
    for (var i=0; i<N_NEURONS; i++) targets[i] = 0;
    if (activeWord && SIM[activeWord]) {
      WORDS_META.forEach(function(m) {
        var s = SIM[activeWord][m.word] || 0;
        var pat = wordPatterns[m.word];
        for (var k=0; k<pat.length; k++) {
          var ni = pat[k];
          if (s > targets[ni]) targets[ni] = s;
        }
      });
    }
    for (var i=0; i<N_NEURONS; i++) animTarget[i] = targets[i];
  }

  function brainPath(ctx, w, h) {
    ctx.beginPath();
    var pts=[
      [0.50,0.05],[0.62,0.05],[0.72,0.08],[0.80,0.15],
      [0.87,0.20],[0.90,0.28],[0.88,0.38],[0.91,0.46],
      [0.89,0.55],[0.84,0.60],[0.87,0.68],[0.85,0.76],
      [0.78,0.80],[0.70,0.82],[0.65,0.85],[0.60,0.88],
      [0.55,0.90],[0.50,0.90],[0.45,0.90],[0.40,0.88],
      [0.35,0.85],[0.30,0.82],[0.22,0.80],[0.15,0.76],
      [0.13,0.68],[0.16,0.60],[0.11,0.55],[0.09,0.46],
      [0.12,0.38],[0.10,0.28],[0.13,0.20],[0.20,0.15],
      [0.28,0.08],[0.38,0.05],[0.50,0.05],
    ];
    ctx.moveTo(pts[0][0]*w,pts[0][1]*h);
    for(var i=1;i<pts.length-2;i++){
      var mx=(pts[i][0]+pts[i+1][0])/2*w, my=(pts[i][1]+pts[i+1][1])/2*h;
      ctx.quadraticCurveTo(pts[i][0]*w,pts[i][1]*h,mx,my);
    }
    ctx.closePath();
  }

  function drawFissures(ctx, w, h) {
    ctx.strokeStyle='rgba(255,255,255,0.04)'; ctx.lineWidth=1.2;
    [[[ 0.50,0.07],[0.50,0.45]],
     [[0.30,0.22],[0.50,0.35],[0.70,0.22]],
     [[0.22,0.38],[0.40,0.50],[0.60,0.50],[0.78,0.38]],
     [[0.30,0.62],[0.50,0.70],[0.70,0.62]],
     [[0.20,0.50],[0.35,0.42]],[[0.80,0.50],[0.65,0.42]],
     [[0.40,0.75],[0.50,0.80],[0.60,0.75]],
    ].forEach(function(pts){
      ctx.beginPath(); ctx.moveTo(pts[0][0]*w,pts[0][1]*h);
      for(var i=1;i<pts.length;i++) ctx.lineTo(pts[i][0]*w,pts[i][1]*h);
      ctx.stroke();
    });
  }

  function hexRGB(hex){ return [parseInt(hex.slice(1,3),16),parseInt(hex.slice(3,5),16),parseInt(hex.slice(5,7),16)]; }

  function drawFrame() {
    if(!ctx) return;
    var w=W*DPR, h=H*DPR;
    ctx.clearRect(0,0,w,h);
    ctx.save(); brainPath(ctx,w,h);
    ctx.fillStyle='#1a1a24'; ctx.fill();
    var g=ctx.createRadialGradient(w*.5,h*.35,0,w*.5,h*.5,w*.55);
    g.addColorStop(0,'rgba(124,110,247,0.07)'); g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fill(); ctx.restore();
    ctx.save(); brainPath(ctx,w,h); ctx.clip(); drawFissures(ctx,w,h); ctx.restore();
    ctx.save(); brainPath(ctx,w,h); ctx.strokeStyle='rgba(255,255,255,0.09)'; ctx.lineWidth=1.5; ctx.stroke(); ctx.restore();

    for(var i=0;i<N_NEURONS;i++) animLevel[i]+=(animTarget[i]-animLevel[i])*0.11;

    var col=activeGroup?GROUP_COLOR[activeGroup]:'#7c6ef7';
    var rgb=hexRGB(col);

    if(activeWord){
      var pat=wordPatterns[activeWord];
      for(var ai=0;ai<pat.length;ai++){
        for(var aj=ai+1;aj<pat.length;aj++){
          if((ai+aj)%4!==0) continue;
          var na=neurons[pat[ai]],nb=neurons[pat[aj]]; if(!na||!nb) continue;
          var dx=na.x-nb.x,dy=na.y-nb.y,d=Math.sqrt(dx*dx+dy*dy);
          if(d>0.22) continue;
          var alpha=(animLevel[pat[ai]]+animLevel[pat[aj]])/2*(1-d/0.22)*0.3;
          ctx.beginPath(); ctx.moveTo(na.x*w,na.y*h); ctx.lineTo(nb.x*w,nb.y*h);
          ctx.strokeStyle='rgba('+rgb[0]+','+rgb[1]+','+rgb[2]+','+alpha+')';
          ctx.lineWidth=0.8; ctx.stroke();
        }
      }
    }

    for(var i=0;i<N_NEURONS;i++){
      var n=neurons[i],lv=animLevel[i],r=n.r*DPR;
      if(lv>0.02){
        var gw=ctx.createRadialGradient(n.x*w,n.y*h,0,n.x*w,n.y*h,r*5*lv);
        gw.addColorStop(0,'rgba('+rgb[0]+','+rgb[1]+','+rgb[2]+','+(0.5*lv)+')');
        gw.addColorStop(1,'rgba('+rgb[0]+','+rgb[1]+','+rgb[2]+',0)');
        ctx.beginPath(); ctx.arc(n.x*w,n.y*h,r*5*lv,0,Math.PI*2); ctx.fillStyle=gw; ctx.fill();
        ctx.beginPath(); ctx.arc(n.x*w,n.y*h,r+lv*2.5*DPR,0,Math.PI*2);
        ctx.fillStyle='rgba('+rgb[0]+','+rgb[1]+','+rgb[2]+','+(0.2+0.8*lv)+')'; ctx.fill();
      } else {
        ctx.beginPath(); ctx.arc(n.x*w,n.y*h,r,0,Math.PI*2);
        ctx.fillStyle='rgba(255,255,255,0.18)'; ctx.fill();
      }
    }
    requestAnimationFrame(drawFrame);
  }

  function resize(){
    W=wrap.clientWidth; H=Math.round(W*0.62);
    canvas.style.height=H+'px'; canvas.width=W*DPR; canvas.height=H*DPR;
    ctx=canvas.getContext('2d');
  }

  document.querySelectorAll('.word-pill').forEach(function(p){
    p.addEventListener('click',function(){ setWord(p.dataset.word,p.dataset.group); });
  });
  window.addEventListener('resize',resize);
  resize(); initNeurons(); buildPatterns();
  for(var i=0;i<N_NEURONS;i++){animLevel[i]=0;animTarget[i]=0;}
  drawFrame();
})();
</script>
