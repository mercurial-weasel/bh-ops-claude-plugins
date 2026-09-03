---
name: excalidraw
description: >
  Generate complex, animated Excalidraw diagrams using the Excalidraw MCP server. Creates flowcharts,
  architecture diagrams, sequence diagrams, mind maps, ER diagrams, network topologies, state machines,
  and custom illustrations with professional styling and progressive camera animations.

  Use this skill whenever the user asks to: draw a diagram, create an excalidraw, visualize architecture,
  make a flowchart, draw a sequence diagram, sketch a system design, illustrate a process, create a
  mind map, show entity relationships, map a network topology, diagram a state machine, or any request
  involving visual diagrams or hand-drawn-style illustrations. Also trigger when users say things like
  "show me how X works" or "can you visualize this" where a diagram would be the best answer.
---

# Excalidraw Diagram Generator

You create rich, animated Excalidraw diagrams using the Excalidraw MCP tools. The diagrams stream in element-by-element with draw-on animations and camera pans, creating an engaging visual experience.

## Workflow

### Step 1: Call read_me (mandatory, once per conversation)

Before your first `create_view` call, you MUST call `mcp__excalidraw__read_me`. This loads the full element format reference, color palette, and examples. Do NOT call it again after the first time — it returns the same content.

### Step 2: Plan the diagram

Before writing any JSON, plan your layout:

1. **Identify the diagram type** — flowchart, architecture, sequence, mind map, ER, network, state machine, or freeform
2. **List all nodes and connections** — what shapes, what labels, what connects to what
3. **Choose a layout strategy** — left-to-right flow, top-down hierarchy, radial, grid, or swimlanes
4. **Pick a camera strategy** — how many camera positions, what order to reveal content
5. **Estimate total dimensions** — this determines your camera size (see sizing guide below)

### Step 3: Build and render with create_view

Call `mcp__excalidraw__create_view` with a JSON array of Excalidraw elements. The elements stream in order, so drawing order matters for both z-index and animation feel.

### Step 4: Iterate if needed

Each `create_view` call returns a `checkpointId`. To build on a previous diagram, start your next elements array with `{"type": "restoreCheckpoint", "id": "<checkpointId>"}` followed by new elements. This restores the previous state (including any user edits made in fullscreen) and appends your additions.

---

## Element Construction Rules

### Drawing Order (critical for streaming animation)

Emit elements in this order — it creates the best visual flow:

1. **cameraUpdate** — always first, frames the upcoming content
2. **Background zones** — large translucent rectangles that group related elements
3. **Shapes with labels** — rectangles, ellipses, diamonds (use `label` property, not separate text)
4. **Arrows with bindings** — connect shapes using `startBinding`/`endBinding` with `fixedPoint`
5. **Standalone text** — titles, annotations (only when text can't be a shape label)
6. **Decorations** — illustrative art, icons drawn last as finishing touches

BAD: all rectangles, then all text, then all arrows (boring, no progressive reveal)
GOOD: camera → zone → shape+label → arrow → shape+label → arrow → ... (each section builds naturally)

### Camera Strategy

Camera updates are what make Excalidraw diagrams feel alive. Use them generously to guide attention.

**Camera sizes (must be 4:3 ratio):**
| Size | Dimensions | Use case |
|------|-----------|----------|
| S | 400x300 | Close-up on 2-3 elements |
| M | 600x450 | A section of a diagram |
| L | 800x600 | Standard full diagram (default) |
| XL | 1200x900 | Large overview (min font 18) |
| XXL | 1600x1200 | Panorama (min font 21) |

**Camera patterns by diagram type:**

- **Flowchart**: Start zoomed in (M) on the first step, pan right/down as you add steps, zoom out (L/XL) at the end for overview
- **Architecture**: Start with title (M), zoom out to show layers one at a time, final panorama (XL)
- **Sequence diagram**: Pan across actors right-to-left to introduce them, then follow message flow top-down
- **Mind map**: Start at center (M), zoom out as branches grow, final overview
- **ER diagram**: Introduce entity groups with focused cameras, zoom out for full schema

Always start with a `cameraUpdate` as the very first element. Leave padding — don't match camera exactly to content bounds.

### Labeled Shapes (preferred)

Use the `label` property on shapes instead of separate text elements — it auto-centers and the container resizes to fit:

```json
{
  "type": "rectangle", "id": "r1", "x": 100, "y": 100,
  "width": 200, "height": 80,
  "backgroundColor": "#a5d8ff", "fillStyle": "solid",
  "roundness": {"type": 3},
  "label": {"text": "My Label", "fontSize": 20}
}
```

### Arrow Bindings

Connect arrows to shapes using `fixedPoint` coordinates:
- **Right edge**: `[1, 0.5]`
- **Left edge**: `[0, 0.5]`
- **Top edge**: `[0.5, 0]`
- **Bottom edge**: `[0.5, 1]`

```json
{
  "type": "arrow", "id": "a1", "x": 300, "y": 150,
  "width": 150, "height": 0,
  "points": [[0,0],[150,0]],
  "endArrowhead": "arrow",
  "startBinding": {"elementId": "source_id", "fixedPoint": [1, 0.5]},
  "endBinding": {"elementId": "target_id", "fixedPoint": [0, 0.5]}
}
```

### Sizing Minimums

- Shapes: minimum 120x60 for labeled rectangles/ellipses
- Font: minimum 16 for body text, 20 for titles, never below 14
- Gaps: at least 20-30px between elements
- Prefer fewer, larger elements over many tiny ones

### Color Palette

**Shape fills (pastel backgrounds):**
| Color | Hex | Semantic use |
|-------|-----|-------------|
| Light Blue | `#a5d8ff` | Input, sources, primary |
| Light Green | `#b2f2bb` | Success, output, completed |
| Light Orange | `#ffd8a8` | Warning, pending, external |
| Light Purple | `#d0bfff` | Processing, middleware |
| Light Red | `#ffc9c9` | Error, critical, alerts |
| Light Yellow | `#fff3bf` | Notes, decisions |
| Light Teal | `#c3fae8` | Storage, data |
| Light Pink | `#eebefa` | Analytics, metrics |

**Stroke/accent colors:**
| Color | Hex | Use |
|-------|-----|-----|
| Blue | `#4a9eed` | Primary |
| Green | `#22c55e` | Success |
| Amber | `#f59e0b` | Warning |
| Red | `#ef4444` | Error |
| Purple | `#8b5cf6` | Accent |
| Cyan | `#06b6d4` | Info |

**Background zones** (use with `opacity: 30`):
| Color | Hex | Layer |
|-------|-----|-------|
| Blue zone | `#dbe4ff` | UI / frontend |
| Purple zone | `#e5dbff` | Logic / agent |
| Green zone | `#d3f9d8` | Data / tools |

### Text Contrast

On white backgrounds: minimum text color is `#757575`. For colored text on light fills, use dark variants (`#15803d` not `#22c55e`, `#2563eb` not `#4a9eed`). Never use light gray on white.

### Things That Don't Work

- No emoji in text — Excalidraw's font doesn't render them
- No `textAlign`/`width` for positioning standalone text — position with `x` coordinate instead
- Estimate standalone text width as `text.length * fontSize * 0.5`, then set `x = centerX - estimatedWidth/2`

---

## Dark Mode

When the user requests dark mode, start with a massive dark background rectangle BEFORE the first cameraUpdate:

```json
{"type": "rectangle", "id": "darkbg", "x": -4000, "y": -3000,
 "width": 10000, "height": 7500,
 "backgroundColor": "#1e1e2e", "fillStyle": "solid",
 "strokeColor": "transparent", "strokeWidth": 0}
```

Then use dark fills (`#1e3a5f`, `#1a4d2e`, `#2d1b69`, `#5c3d1a`, `#5c1a1a`, `#1a4d4d`) and light text (`#e5e5e5` primary, `#a0a0a0` secondary). Never use text darker than `#555` on dark backgrounds.

---

## Animation Mode

For transformation effects, use delete-and-replace within a single `create_view` call:

1. Draw initial elements
2. Emit a `cameraUpdate` (slight shift for motion feel)
3. `{"type": "delete", "ids": "old1,old2"}`
4. Draw replacement elements at same coordinates with new content/colors
5. Repeat

Never reuse deleted element IDs — always assign fresh IDs to replacements.

---

## Diagram Type Templates

For detailed layout patterns per diagram type, read `references/diagram-patterns.md`. It contains spacing formulas, node arrangement strategies, and complete examples for each supported diagram type.

---

## Checklist Before Rendering

Before calling `create_view`, verify:
- [ ] First element is `cameraUpdate` with 4:3 ratio dimensions
- [ ] All elements have unique `id` strings
- [ ] No font size below 14, titles at 20+
- [ ] No shapes smaller than 120x60 (labeled)
- [ ] Arrow `points` are `[dx, dy]` offsets from the arrow's `x, y`
- [ ] Background zones drawn before foreground shapes
- [ ] Labels use the `label` property on shapes, not separate text elements
- [ ] No emoji in any text field
- [ ] Multiple camera positions for diagrams with 5+ elements
- [ ] JSON is valid — no comments, no trailing commas
