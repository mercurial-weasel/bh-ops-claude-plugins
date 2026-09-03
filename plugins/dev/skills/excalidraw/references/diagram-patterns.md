# Diagram Type Patterns

Detailed layout strategies, spacing formulas, and examples for each supported diagram type.

## Table of Contents
1. [Flowcharts](#flowcharts)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Sequence Diagrams](#sequence-diagrams)
4. [Mind Maps](#mind-maps)
5. [Entity-Relationship Diagrams](#entity-relationship-diagrams)
6. [Network Topology](#network-topology)
7. [State Machines](#state-machines)
8. [Custom Illustrations](#custom-illustrations)

---

## Flowcharts

### Layout Strategy
- **Direction**: Left-to-right (default) or top-to-bottom
- **Node spacing**: 80px horizontal gap between nodes, 60px vertical gap between rows
- **Decision diamonds**: 150x150, with Yes/No branches going right and down
- **Start/End**: Rounded rectangles with green (#b2f2bb) fill

### Node Types
| Shape | Use | Fill |
|-------|-----|------|
| Rounded rectangle | Process step | `#a5d8ff` |
| Diamond | Decision | `#fff3bf` |
| Rounded rectangle | Start/End | `#b2f2bb` |
| Rectangle | I/O operation | `#ffd8a8` |

### Camera Strategy
1. Camera M (600x450) on start node + first 2-3 steps
2. Pan right/down as flow progresses
3. Camera L (800x600) or XL (1200x900) for final overview

### Arrow Pattern
- Straight horizontal arrows for linear flow: `points: [[0,0],[gap,0]]`
- Right-angle arrows for branches: use two points `[[0,0],[dx,0],[dx,dy]]` — but note Excalidraw arrows auto-route, so straight two-point arrows between bound shapes work well
- Label decision arrows with "Yes"/"No" using `label: {"text": "Yes", "fontSize": 14}`

### Example Layout (5-step flow with decision)
```
x=100  x=330  x=560  x=790  x=1020
Start → Process → Decision → Process → End
                      ↓
                   Alt Path
```
- Each node: width=180, height=70
- Gaps: 50px between node edge and arrow start
- Total width ~1100px → use Camera XL (1200x900) for overview

---

## Architecture Diagrams

### Layout Strategy
- **Layers**: Stack horizontally or vertically (frontend on top, backend middle, data bottom)
- **Background zones**: Large translucent rectangles (opacity: 30-35) behind each layer
- **Components**: Rounded rectangles inside zones
- **Layer spacing**: 40px gap between zone edges
- **Component spacing**: 30px inside zones

### Zone Colors
| Layer | Zone fill | Zone stroke | Component fill |
|-------|-----------|-------------|---------------|
| Frontend/UI | `#dbe4ff` | `#4a9eed` | `#a5d8ff` |
| API/Logic | `#e5dbff` | `#8b5cf6` | `#d0bfff` |
| Data/Storage | `#d3f9d8` | `#22c55e` | `#c3fae8` |
| External | `#ffd8a8` | `#f59e0b` | `#fff3bf` |

### Camera Strategy
1. Camera M — title and high-level overview label
2. Camera M per layer — zoom into each layer as you draw its components
3. Camera L/XL — zoom out, draw cross-layer arrows
4. Camera XL — final overview

### Vertical Stack Example
```
y=50:  Title
y=100: ┌─── Frontend Zone (opacity 30) ───┐
       │  [React App]  [Mobile App]       │
y=280: └──────────────────────────────────┘
y=320: ┌─── API Zone ────────────────────┐
       │  [API Gateway]  [Auth Service]  │
y=500: └──────────────────────────────────┘
y=540: ┌─── Data Zone ──────────────────┐
       │  [PostgreSQL]  [Redis]  [S3]   │
y=720: └────────────────────────────────┘
```

---

## Sequence Diagrams

### Layout Strategy
- **Actors**: Evenly spaced across the top, 170-200px apart
- **Lifelines**: Dashed vertical arrows from each actor header
- **Messages**: Horizontal arrows between lifelines, 40-50px vertical spacing
- **Activation boxes**: Optional thin rectangles on lifelines during processing

### Actor Header
- Rounded rectangle: width=130, height=40
- Each gets a different pastel fill

### Message Arrows
- Solid arrows → synchronous calls
- Dashed arrows (`strokeStyle: "dashed"`) → responses/async
- Label with operation name: `label: {"text": "getData()", "fontSize": 14}`

### Camera Strategy (the snake pattern)
1. Camera M — title
2. Camera S/M — pan across actors right-to-left to introduce each one
3. Camera M — follow message flow top-down, panning as needed
4. Camera L — final overview

### Spacing Formula
```
Actor spacing: 200px center-to-center
Lifeline start: actor.y + actor.height
Message vertical gap: 40px
First message y: lifeline_start + 40px
```

---

## Mind Maps

### Layout Strategy
- **Center node**: Large rounded rectangle or ellipse at center
- **Branches**: Radiate outward in 4-8 directions
- **Sub-branches**: Smaller nodes connected to branch nodes
- **Spacing**: First ring 200px from center, second ring 400px

### Branch Colors
Assign each main branch a consistent color family:
- Branch 1: Blue (#a5d8ff / #4a9eed)
- Branch 2: Green (#b2f2bb / #22c55e)
- Branch 3: Orange (#ffd8a8 / #f59e0b)
- Branch 4: Purple (#d0bfff / #8b5cf6)
- Branch 5: Red (#ffc9c9 / #ef4444)
- Branch 6: Teal (#c3fae8 / #06b6d4)

### Camera Strategy
1. Camera M — draw center node
2. Camera M — pan to each branch direction as you draw it
3. Camera L/XL — zoom out for complete map

### Radial Position Formula
For N branches evenly distributed:
```
angle = (2 * PI * i) / N  (where i = 0..N-1)
node_x = center_x + radius * cos(angle) - node_width/2
node_y = center_y + radius * sin(angle) - node_height/2
```

---

## Entity-Relationship Diagrams

### Layout Strategy
- **Entities**: Rectangles with bold title label
- **Attributes**: Listed as text inside or below the entity rectangle
- **Relationships**: Arrows with cardinality labels (1, N, M)
- **Layout**: Grid arrangement, related entities close together

### Entity Style
- Width: 160-200px depending on attribute text length
- Height: varies (60px base + 20px per attribute shown)
- Fill: `#a5d8ff` for main entities, `#d0bfff` for junction/weak entities
- Title fontSize: 18, attribute fontSize: 14-16

### Relationship Arrows
- Use labeled arrows with cardinality: `label: {"text": "1:N", "fontSize": 14}`
- Solid lines for identifying relationships
- Dashed lines for non-identifying

### Camera Strategy
1. Camera M — introduce core entities first
2. Pan to related entity groups
3. Camera XL — full schema overview

---

## Network Topology

### Layout Strategy
- **Core/backbone**: Center of diagram
- **Distribution**: Ring around core
- **Access/endpoints**: Outer ring
- **Use ellipses** for network devices, rectangles for servers/services

### Device Colors
| Device | Fill | Stroke |
|--------|------|--------|
| Router/Switch | `#ffd8a8` | `#f59e0b` |
| Server | `#a5d8ff` | `#4a9eed` |
| Database | `#c3fae8` | `#06b6d4` |
| Firewall | `#ffc9c9` | `#ef4444` |
| Client/User | `#d0bfff` | `#8b5cf6` |
| Cloud | `#b2f2bb` | `#22c55e` |

### Connection Styles
- Solid arrows: primary connections
- Dashed: redundant/backup paths
- Label with protocol/bandwidth: `label: {"text": "HTTPS", "fontSize": 14}`

---

## State Machines

### Layout Strategy
- **States**: Rounded rectangles
- **Initial state**: Small filled ellipse (30x30, dark fill)
- **Final state**: Double ellipse (outer 40x40, inner 24x24)
- **Transitions**: Labeled arrows between states
- **Direction**: Generally left-to-right or top-down

### State Colors
| State type | Fill | Stroke |
|-----------|------|--------|
| Normal | `#a5d8ff` | `#4a9eed` |
| Active/Current | `#b2f2bb` | `#22c55e` |
| Error | `#ffc9c9` | `#ef4444` |
| Waiting | `#fff3bf` | `#f59e0b` |

### Transition Labels
Format: `event [guard] / action`
Keep labels short — if they overflow the arrow, make the arrow longer or abbreviate.

---

## Custom Illustrations

### Drawing Art with Basic Shapes

Excalidraw only has rectangle, ellipse, diamond, arrow, and line — but you can combine them creatively:

- **Person/stick figure**: ellipse (head) + thin rectangle (body) + arrows (arms/legs)
- **Sun**: ellipse (center) + 8 short arrows radiating outward (no arrowheads)
- **Cloud**: overlapping ellipses of different sizes
- **Tree**: rectangle (trunk) + overlapping ellipses (foliage, green fills)
- **House**: rectangle (body) + diamond (roof)
- **Star**: overlapping diamonds at angles (approximate)

### Tips for Art
- Draw illustrations LAST, after the main diagram content
- Use consistent stroke width (2 for most things)
- Fill shapes with appropriate colors
- Keep illustrations small relative to the diagram — they're accents, not the focus
- Use slight camera shifts between art elements for a playful animation feel

---

## General Spacing Reference

| Element relationship | Minimum gap |
|---------------------|-------------|
| Between sibling nodes | 30px |
| Between parent and child | 50px |
| Between zones/groups | 40px |
| Arrow label to shape edge | 10px |
| Title to first content | 30px |
| Zone padding (internal) | 20px |

## Common Pitfalls

1. **Camera too tight**: Always leave 50-100px padding around content in the camera view
2. **Arrows too short for labels**: A label like "HTTP Request" needs an arrow at least 150px wide
3. **Overlapping text**: Check y-coordinates — shapes stacked with <60px vertical gap will overlap
4. **Invisible zone labels**: Zone labels placed at top-left of zones can overlap with shapes inside — offset them properly
5. **Forgetting to bind arrows**: Unbound arrows don't move when shapes are repositioned in fullscreen editing
