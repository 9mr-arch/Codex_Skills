# Reference-video analysis and prompt architecture

Read this guide for replacements, previs finishing, timed effects, multi-shot clips, source-audio preservation, or multi-asset jobs.

## 1. Evidence pass

Record only observable facts. Do not turn guesses into shot instructions.

### Clip facts

- duration, frame rate, dimensions, and aspect ratio;
- number and approximate position of cuts;
- opening and ending state;
- whether the camera or subject supplies most of the motion;
- whether audio exists, only when verified.

### Per-shot facts

For each shot, capture framing and camera height; principal camera movement and direction; subject blocking, orientation, and screen direction; speed profile; lighting and palette; transition; effect trigger and trajectory; and contact, occlusion, reflection, and shadow relationships.

Use approximate time windows only when they locate a cut, edit, effect, or endpoint.

## 2. Interpret the source type

### Previs, animatic, or gray-box 3D

Treat it as a blueprint rather than a look reference.

Usually preserve total duration, shot order, camera path, framing progression, cut points, blocking, screen direction, relative scale, and effect timing.

Usually replace or refine proxy meshes, temporary products, flat shaders, placeholder lighting, low-detail backgrounds, guides, grids, labels, handles, preview overlays, and crude effects. Preserve a placeholder effect's timing and trajectory only when it represents the intended action.

Do not automatically preserve the previs palette, texture quality, or placeholder audio.

### Live-action reference

Decide which layer is evidence: performance and body mechanics; handheld or stabilized camera behavior; lens breathing, focus pull, exposure response, or motion blur; production design, natural light, and surface response; edit rhythm; or audio performance.

Do not copy an identifiable person, logo, wardrobe, location, or voice unless the user assigned that asset this job and supplied it for use.

### Finished commercial or VFX reference

Separate the effect system from branded content. Transfer the physical logic—trigger, propagation, refraction, glow, particles, deformation, and environmental response—without silently copying unrelated products, marks, text, or claims.

## 3. Choose edit versus recreation

Use **video edit** when the desired result is the same clip with local changes:

```text
Strictly edit @Video 1 (source clip). Preserve [named invariants]. Replace/add/remove [target] at [time or event]. Keep all unmentioned content unchanged.
```

Use **multimodal recreation** when the source is a motion or camera blueprint for a new clip:

```text
Use only [named properties] from @Video 1 (motion/camera reference); do not transfer [people, product, set, palette, branding, audio]. Apply those properties to @Image 1 (new subject or product) in [new environment].
```

Use **previs finishing** when shot layout remains while appearance is replaced:

```text
Use @Video 1 (previs blueprint) for duration, shot order, camera path, blocking, screen direction, transition points, and effect timing. Replace all proxy geometry and placeholder rendering with [final subjects and finish]. Do not reproduce guides, overlays, low-detail meshes, or temporary text.
```

## 4. Four-layer transfer ledger

### Preserve

Name the minimum source truths that define the shot: camera, timing, blocking, contact, lighting direction, background, reflections, source audio, or cut rhythm.

### Replace

Identify the target by source appearance and spatial role, then bind the new asset. Avoid “replace the object” when several objects are present.

### Add or refine

Describe only new visual information missing from the source: final materials, color, lighting finish, particles, fluid behavior, refractive wave, atmosphere, or environmental response.

### Exclude

Prevent reference leakage: original actor or product, unwanted palette, source branding, guide overlays, placeholder text, unwanted audio, extra instances, or invented controls.

## 5. Timed effect grammar

For an effect edit, include:

1. **Trigger** — contact, activation, impact, landing, or source effect onset.
2. **Origin** — exact screen or world location, or an object part.
3. **Trajectory** — radial, axial, upward, along-surface, or following the source path.
4. **Evolution** — form, expand, refract, break, fade, or settle.
5. **Material** — opacity, color gradient, thickness, dispersion, or particle size.
6. **Integration** — cast or reflected light, shadows, occlusion, surface deformation, or atmosphere.

Weak:

```text
Add a blue wave at the end.
```

Strong:

```text
At the exact onset of the source ending effect, replace it with three transparent concentric waves that originate beneath the product, expand radially along the floor, thin and fade outward, and cast pale-blue refracted caustics onto the floor and lower product edge.
```

## 6. Product-reference binding

An image used for product identity should transfer only approved product traits: silhouette and proportions; cap, base, seams, controls, ports, and indicator count; material, finish, and color; label and logo placement when required.

State what the image must not donate when needed: pose, background, shadow, framing, or image lighting. The source video's motion, scale relationship, contact, occlusion, camera, and timing remain authoritative unless the user says otherwise.

For generated typography or small package copy, exact legibility is probabilistic; legally critical copy should be composited in post.

## 7. Audio behavior

- For an edit, preserve source audio only when requested or clearly required by “same clip.” State it explicitly and mark provider control for verification.
- For recreation, source audio does not transfer by default. Describe required ambience or effects separately.
- Do not enable fresh generated audio merely because the source contains audio.
- If audio was not heard, say “audio unverified”; do not infer dialogue, music, or effects from frames.

## 8. Output template

```text
[Direct operation and asset bindings.]

[Preserve source truths.]

[Replace/add/refine the target, including timing or event anchor.]

[Describe material, motion, and environmental integration.]

[Short continuity and exclusion tail.]
```

Asset order example:

- `@Video 1` — source/previs; transfers camera, motion, timing, and effect onset; does not transfer proxy product or placeholder look.
- `@Image 1` — final product; transfers geometry, material, and color; does not transfer pose, background, or shadow.

Keep model variant, duration, aspect ratio, resolution, and audio behavior outside the prompt.
