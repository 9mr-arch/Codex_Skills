---
name: reference-to-style-prompts
description: Extract reusable visual-style instructions from reference imagery as an English six-shot styleframe image prompt and an English MOOD insert for an existing video prompt; when product or character references are supplied, generate and inspect a text-free six-panel styleframe board. Use for style extraction, look transfer, mood prompt extraction, or advertising styleframe boards. Do not use for generic image captioning or a full video screenplay.
---

# Reference to Style Prompts

Separate transferable visual treatment from the reference's people, products, location, copy, and story. Explanations are in the user's language; copy-ready generation prompts are English unless the user asks otherwise.

Read [references/workflow.md](references/workflow.md) for the full analysis rubric, six-panel layout, MOOD restrictions, generation workflow, and validation checklist.

## Route the request

### Style reference only

Inspect the image and return both outputs immediately:

1. an English image-generation prompt for a text-free six-shot styleframe board;
2. an English MOOD-body paragraph intended to be inserted into an existing structured video prompt.

Do not generate an image yet. Do not invent a product/character reference or numbered media tag. End with a brief invitation to provide a product or character image unless the user requested prompt-only output.

### Style plus product or character reference

Return the two prompts and generate one finished six-panel board using the available image-generation capability. Assign the style image only to palette, contrast, lighting, texture, optics, space, and medium; assign the target image to identity, silhouette, geometry, color, wardrobe, controls, markings, logo, or label as applicable.

If the target arrives in a follow-up after style extraction, treat it as continuation and generate without asking again. Ask only when it is materially unclear which image is style and which is the target.

## Style analysis

Observe palette, tonal curve, light direction and softness, shadow and highlight behavior, texture/noise, optical diffusion, depth, perspective, foreground occlusion, framing, medium, and composition. Distinguish observation from inference; do not assert a camera, lens, film stock, LUT, date, or location from appearance alone.

Do not universalize a reference-specific neon, vintage, Y2K, water, glass, prism, fabric, grain, fog, shallow depth, or handheld effect. Translate scene objects into abstract visual behavior only when useful.

## Six-panel image prompt

Default to one 3:2 landscape board with two rows of three panels and thin white separators. The panels must feel like six shots from one advertising production, not crops, mirrors, or turnaround views. Maintain one subject, environment, lighting design, and grade while varying at least three camera directions/heights and three distances:

- hero close-up;
- clearly different low or side angle;
- opposing three-quarter or depth shot;
- medium-wide environment shot;
- extreme macro detail;
- product-only beauty shot or character detail.

No overlay copy, title, subtitle, angle label, panel number, watermark, signature, or reserved text area. Preserve text already printed on the real product only when it is an identity feature; do not duplicate it as graphic copy.

## MOOD insert

Write roughly 80–160 English words describing only transferable emotional tone, palette, grade, contrast, highlight roll-off, shadows, lighting texture, skin/material response, optical bloom, and cross-scene consistency.

Do not add or alter duration, ratio, characters, wardrobe, scenes, shot order, camera movement, action, transition, dialogue, music, or audio. Do not carry the six-panel layout into MOOD. End by stating that each scene's specified lighting, time of day, visibility, character, costume, framing, action, transition, and audio constraints remain authoritative.

## Generation and validation

When generation is required, include every necessary style and target reference in the image tool input. Do not substitute HTML, SVG, a prompt, or the original image for the generated board. Inspect the result for target fidelity, medium and palette match, six distinct views/distances, consistent subject and product geometry, hand/contact quality, and absence of overlay text. Make at most one focused corrective generation for a material mismatch, then disclose remaining differences.

Do not invoke an external paid service or upload files elsewhere unless the user specifically requests it.
