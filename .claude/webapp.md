i# RedAmon Webapp Development Guidelines

## Project Overview

RedAmon is a security reconnaissance and vulnerability visualization tool. The webapp provides a graph-based interface for exploring security data from Neo4j.

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: CSS Modules + CSS Custom Properties (Design Tokens)
- **Icons**: Lucide React
- **State Management**: React hooks + TanStack Query
- **Graph Visualization**: react-force-graph-2d / react-force-graph-3d

---

## Design System

### Color Palette

**Primary Brand Color (Crimson Red)** - Used for logo, navigation active states, primary actions
```css
--accent-primary: #e53935 (--color-crimson-500)
```

**Secondary Color (Blue)** - Used for toggles, info states, links, focus rings
```css
--accent-secondary: #3b82f6 (--color-blue-500)
```

### Using Colors

Always use semantic tokens from `styles/tokens/semantic.css`, never raw color values:

```css
/* CORRECT */
color: var(--text-primary);
background: var(--bg-secondary);
border-color: var(--accent-primary);

/* INCORRECT */
color: #fafafa;
background: #18181b;
border-color: #e53935;
```

### Key Semantic Tokens

| Token | Usage |
|-------|-------|
| `--bg-primary` | Main app background |
| `--bg-secondary` | Cards, panels, headers |
| `--bg-tertiary` | Nested elements, toolbars |
| `--text-primary` | Main text |
| `--text-secondary` | Muted text |
| `--text-tertiary` | Disabled, placeholders |
| `--border-default` | Standard borders |
| `--accent-primary` | Brand color (crimson) |
| `--accent-secondary` | Secondary actions (blue) |

---

## Component Architecture

### File Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── graph/              # Graph page
│   │   ├── components/     # Page-specific components
│   │   ├── hooks/          # Page-specific hooks
│   │   ├── types/          # Page-specific types
│   │   ├── config/         # Page-specific constants
│   │   ├── utils/          # Page-specific utilities
│   │   ├── page.tsx        # Page component
│   │   └── page.module.css # Page styles
│   └── layout.tsx          # Root layout
├── components/             # Shared components
│   ├── layout/             # Layout components (GlobalHeader, Footer, etc.)
│   ├── ui/                 # Reusable UI components (Toggle, Modal, Tooltip, etc.)
│   └── ThemeToggle/        # Theme toggle component
├── hooks/                  # Shared hooks
├── styles/                 # Global styles
│   ├── tokens/             # Design tokens
│   │   ├── colors.css      # Color primitives
│   │   ├── semantic.css    # Semantic tokens
│   │   ├── typography.css  # Font sizes, weights
│   │   ├── spacing.css     # Spacing scale, radius
│   │   └── shadows.css     # Shadows, transitions
│   ├── themes/             # Theme overrides
│   │   ├── dark.css        # Dark theme (default)
│   │   └── light.css       # Light theme
│   ├── components/         # Shared component styles
│   │   ├── buttons.css     # Buttons, toggles, dividers
│   │   ├── inputs.css      # Inputs, selects, forms
│   │   ├── chips.css       # Chips, tags, badges
│   │   ├── feedback.css    # Tooltips, modals, menus
│   │   ├── loading.css     # Spinners, skeletons
│   │   ├── containers.css  # Cards, lists, tables
│   │   └── status.css      # Status, alerts, severity
│   ├── base/               # Reset and globals
│   └── index.css           # Main entry point
└── lib/                    # Utilities, API clients
```

### Component Pattern

Each component should have its own folder:

```
ComponentName/
├── ComponentName.tsx       # Component logic
├── ComponentName.module.css # Scoped styles
└── index.ts                # Export
```

**index.ts pattern:**
```typescript
export { ComponentName } from './ComponentName'
```

---

## Styling Guidelines

### CSS Modules

All component styles use CSS Modules (`.module.css`):

```tsx
import styles from './Component.module.css'

<div className={styles.container}>
  <span className={styles.label}>Text</span>
</div>
```

### Spacing

Use spacing tokens for consistency:

```css
padding: var(--space-2) var(--space-4);
gap: var(--space-3);
margin-bottom: var(--space-4);
```

**Spacing Scale:**
- `--space-0-5`: 2px
- `--space-1`: 4px
- `--space-1-5`: 6px
- `--space-2`: 8px
- `--space-3`: 12px
- `--space-4`: 16px
- `--space-6`: 24px

### Typography

Use typography tokens:

```css
font-size: var(--text-xs);    /* 12px */
font-size: var(--text-sm);    /* 14px */
font-size: var(--text-base);  /* 16px */
font-weight: var(--font-medium);
font-weight: var(--font-semibold);
font-weight: var(--font-bold);
```

### Border Radius

```css
border-radius: var(--radius-sm);      /* 4px */
border-radius: var(--radius-md);      /* 6px */
border-radius: var(--radius-default); /* 8px */
border-radius: var(--radius-full);    /* 9999px */
```

### Transitions

```css
transition: var(--transition-fast);    /* 150ms */
transition: var(--transition-default); /* 200ms */
transition: var(--transition-slow);    /* 300ms */
transition: var(--transition-all);     /* all properties */
```

---

## Icons

Use **Lucide React** for all icons:

```tsx
import { Search, Bell, Settings } from 'lucide-react'

<Search size={16} />
<Bell size={18} className={styles.icon} />
```

### Icon Sizes

| Context | Size |
|---------|------|
| Small buttons, inputs | 14px |
| Standard buttons | 16px |
| Headers, navigation | 18px |

---

## Layout Structure

### Global Layout

```
┌─────────────────────────────────────┐ ← GlobalHeader (36px, fixed)
├─────────────────────────────────────┤ ← NavigationBar (~32px, fixed)
│                                     │
│           Main Content              │ ← Scrollable area
│                                     │
├─────────────────────────────────────┤
└─────────────────────────────────────┘ ← Footer (~36px, fixed)
```

### Graph Page Layout

```
┌─────────────────────────────────────┐
│ GraphToolbar                        │ ← Fixed
├──────────┬──────────────────────────┤
│ Drawer   │     Graph Canvas         │ ← Drawer scrollable, canvas fixed
│ (left)   │                          │
├──────────┴──────────────────────────┤
│ PageBottomBar (legend + stats)      │ ← Fixed
└─────────────────────────────────────┘
```

### Fixed Layout Pattern

For fixed headers/footers that don't shrink:

```css
.header {
  flex-shrink: 0;
  height: 36px;
}
```

For scrollable content areas:

```css
.content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}
```

---

## UI Components Strategy

**IMPORTANT**: All UI elements MUST follow these guidelines for consistency.

### When to Use React Components vs CSS Classes

| Use **React Component** | Use **CSS Class** |
|------------------------|-------------------|
| Has internal state (on/off, open/close) | Pure visual styling |
| Requires event handlers (onClick, onClose) | No JavaScript behavior |
| Needs accessibility (aria, keyboard nav) | Static or simple hover states |
| Complex behavior (positioning, timers) | Composable with other elements |
| Would be error-prone to reimplement | Easy to apply correctly |

### Decision Rules

**USE REACT COMPONENT when:**
1. Component manages its own state (toggle checked, modal open)
2. Requires keyboard handling (Escape to close, arrow keys)
3. Needs focus management (focus trap in modals)
4. Has timing/animation logic (toast auto-dismiss)
5. Requires portal rendering (modals, tooltips)
6. Accessibility is complex (aria-expanded, aria-controls)

**USE CSS CLASS when:**
1. Only visual styling needed (colors, spacing, borders)
2. No internal state required
3. Works with native HTML elements
4. Behavior is simple (hover, focus-visible)
5. Developer should control the element directly

### Component Classification

| Element | Type | Reason |
|---------|------|--------|
| **Toggle** | React Component | State, accessibility, keyboard |
| **Modal** | React Component | Focus trap, escape key, portal |
| **Tooltip** | React Component | Positioning, delays, portal |
| **Toast** | React Component | Auto-dismiss timer, stacking |
| **Dropdown Menu** | React Component | Click outside, keyboard nav |
| **Button** | CSS Class | Native button works fine |
| **IconButton** | CSS Class | Just styling on button |
| **Card** | CSS Class | Pure container styling |
| **Chip/Tag** | CSS Class | Visual only |
| **Input** | CSS Class | Native input + styling |
| **Badge** | CSS Class | Visual indicator only |
| **Spinner** | CSS Class | CSS animation only |
| **Skeleton** | CSS Class | CSS animation only |
| **Alert** | CSS Class | Static message block |
| **StatusDot** | CSS Class | Visual indicator only |

### File Locations

| Type | Location | Import |
|------|----------|--------|
| React Components | `src/components/ui/` | `import { Toggle } from '@/components/ui'` |
| CSS Classes | `src/styles/components/` | `composes: className from global` |

---

## React UI Components

Located in `src/components/ui/`. Import from `@/components/ui`.

### Toggle

Binary on/off switch with accessibility support.

```tsx
import { Toggle } from '@/components/ui'

<Toggle
  checked={is3D}
  onChange={setIs3D}
  labelOff="2D"
  labelOn="3D"
  aria-label="Toggle view mode"
/>
```

**Props:**
- `checked: boolean` - Current state
- `onChange: (checked: boolean) => void` - State change handler
- `labelOff?: string` - Label for off state (left)
- `labelOn?: string` - Label for on state (right)
- `disabled?: boolean` - Disable interaction
- `size?: 'small' | 'default'` - Size variant

### Modal

Dialog overlay with focus trap and keyboard handling.

```tsx
import { Modal } from '@/components/ui'

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
  footer={
    <>
      <button className="secondaryButton" onClick={onClose}>Cancel</button>
      <button className="primaryButton" onClick={onConfirm}>Confirm</button>
    </>
  }
>
  <p>Are you sure you want to proceed?</p>
</Modal>
```

**Props:**
- `isOpen: boolean` - Whether modal is visible
- `onClose: () => void` - Close handler
- `title?: string` - Modal title
- `children: ReactNode` - Modal content
- `footer?: ReactNode` - Footer content (buttons)
- `size?: 'small' | 'default' | 'large' | 'full'`
- `closeOnOverlayClick?: boolean` - Close on backdrop click (default: true)
- `closeOnEscape?: boolean` - Close on Escape key (default: true)

### Tooltip

Contextual popup on hover with positioning.

```tsx
import { Tooltip } from '@/components/ui'

<Tooltip content="This is a helpful tip" position="top">
  <button className="iconButton">
    <HelpCircle size={14} />
  </button>
</Tooltip>
```

**Props:**
- `content: ReactNode` - Tooltip content
- `children: ReactNode` - Trigger element
- `position?: 'top' | 'bottom' | 'left' | 'right'`
- `delay?: number` - Show delay in ms (default: 200)
- `disabled?: boolean` - Disable tooltip

### Toast / useToast

Notification system with auto-dismiss.

**Setup:** ToastProvider is already in root layout.

```tsx
import { useToast } from '@/components/ui'

function MyComponent() {
  const { success, error, warning, info } = useToast()

  const handleSave = async () => {
    try {
      await save()
      success('Changes saved successfully')
    } catch (e) {
      error('Failed to save changes', 'Error')
    }
  }
}
```

**useToast methods:**
- `success(message, title?)` - Green success toast
- `error(message, title?)` - Red error toast
- `warning(message, title?)` - Yellow warning toast
- `info(message, title?)` - Blue info toast
- `addToast({ type, message, title?, duration? })` - Custom toast

### Menu

Dropdown menu with keyboard navigation.

```tsx
import { Menu, MenuItem, MenuDivider, MenuLabel } from '@/components/ui'
import { Settings, LogOut, User } from 'lucide-react'

<Menu
  trigger={<button className="iconButton"><MoreVertical size={14} /></button>}
  align="right"
>
  <MenuLabel>Account</MenuLabel>
  <MenuItem icon={<User size={14} />} onClick={handleProfile}>
    Profile
  </MenuItem>
  <MenuItem icon={<Settings size={14} />} onClick={handleSettings}>
    Settings
  </MenuItem>
  <MenuDivider />
  <MenuItem icon={<LogOut size={14} />} onClick={handleLogout} destructive>
    Log out
  </MenuItem>
</Menu>
```

**Menu Props:**
- `trigger: ReactNode` - Element that opens menu
- `children: ReactNode` - Menu items
- `align?: 'left' | 'right'` - Alignment relative to trigger

**MenuItem Props:**
- `onClick?: () => void` - Click handler
- `icon?: ReactNode` - Icon before label
- `destructive?: boolean` - Red destructive style
- `disabled?: boolean` - Disable item

---

## Shared Component Styles (CSS Classes)

Use these for **pure styling** without behavior. Located in `styles/components/`.

### Component Files

| File | Contains |
|------|----------|
| `buttons.css` | Buttons, toggles, dividers |
| `inputs.css` | Text inputs, selects, checkboxes, radios, forms |
| `chips.css` | Chips, tags, count badges |
| `feedback.css` | Tooltips, toasts, modals, popovers, menus |
| `loading.css` | Spinners, skeletons, progress bars, empty states |
| `containers.css` | Cards, panels, lists, tables, tabs, accordions |
| `status.css` | Status dots, alerts, severity indicators, CVSS scores |

### How to Use

```css
/* Compose in CSS Modules */
.closeButton { composes: iconButtonBordered from global; }
.myInput { composes: textInput from global; }
```

```tsx
/* Or direct className */
<button className="primaryButton">Submit</button>
```

---

### Buttons (`buttons.css`)

| Class | Use Case |
|-------|----------|
| `.iconButton` | 24x24 icon button |
| `.iconButtonBordered` | Icon button with border |
| `.textButton` | Text-only button |
| `.primaryButton` | Primary CTA (crimson) |
| `.secondaryButton` | Secondary (outlined) |
| `.toggleSwitch` + `.toggleKnob` | Binary toggle |
| `.badge` | Notification counter |
| `.divider` | Vertical separator |

### Inputs (`inputs.css`)

| Class | Use Case |
|-------|----------|
| `.textInput` | Standard text input |
| `.searchInput` | Search field with icon |
| `.select` | Dropdown select |
| `.checkbox` / `.radio` | Check/radio inputs |
| `.textarea` | Multi-line input |
| `.formGroup` / `.formLabel` | Form structure |
| `.formError` / `.inputError` | Error states |

### Chips (`chips.css`)

| Class | Use Case |
|-------|----------|
| `.chip` | Basic chip |
| `.chipPrimary/Success/Warning/Error` | Colored variants |
| `.chipClickable` / `.chipSelected` | Interactive states |
| `.tag` | Compact tag |
| `.countBadge` | Numeric counter |

### Feedback (`feedback.css`)

| Class | Use Case |
|-------|----------|
| `.tooltip` + `.tooltipContent` | Hover tooltip |
| `.toast` / `.toastSuccess/Error` | Notifications |
| `.modal` / `.modalOverlay` | Dialog modal |
| `.popover` | Contextual popup |
| `.menu` + `.menuItem` | Dropdown menu |

### Loading (`loading.css`)

| Class | Use Case |
|-------|----------|
| `.spinner` / `.spinnerSmall` | Loading spinner |
| `.skeleton` / `.skeletonText` | Placeholder shimmer |
| `.progressBar` + `.progressFill` | Progress indicator |
| `.emptyState` | No data state |
| `.pulseDot` | Animated indicator |

### Containers (`containers.css`)

| Class | Use Case |
|-------|----------|
| `.card` / `.cardHeader/Body/Footer` | Card component |
| `.panel` | Simple container |
| `.list` + `.listItem` | Vertical list |
| `.table` + `.tableRow/Cell` | Data table |
| `.tabs` + `.tab` | Tab navigation |
| `.accordion` | Expandable sections |
| `.statCard` | Stat display |

### Status (`status.css`)

| Class | Use Case |
|-------|----------|
| `.statusDot` | Small indicator |
| `.statusBadge` | Labeled status |
| `.alert` / `.alertError/Warning` | Message block |
| `.severity` / `.severityCritical/High` | Vuln severity |
| `.cvssScore` | CVSS display |
| `.connectionStatus` | Online/offline |

---

### Standard Specs

- **Buttons**: 24x24 icon, crimson primary, all have hover/focus/disabled
- **Inputs**: ~28px height, `--accent-secondary` focus ring
- **Cards**: `--bg-secondary`, 1px border, `--radius-default`
- **Drawer**: 300px width, left slide, `.iconButtonBordered` close

---

## Hooks

### Data Fetching

Use TanStack Query for server state:

```tsx
import { useQuery } from '@tanstack/react-query'

const { data, isLoading, error } = useQuery({
  queryKey: ['graph', projectId],
  queryFn: () => fetchGraphData(projectId),
})
```

### Local State

Use React hooks for UI state:

```tsx
const [isOpen, setIsOpen] = useState(false)
const [is3D, setIs3D] = useState(true)
```

---

## TypeScript

### Type Definitions

Define types in dedicated files:

```typescript
// types/index.ts
export interface GraphNode {
  id: string
  name: string
  type: string
  properties: Record<string, unknown>
}

export interface GraphLink {
  source: string
  target: string
  type: string
}
```

### Props Interfaces

```typescript
interface ComponentProps {
  data: GraphData | undefined
  isLoading: boolean
  onSelect: (node: GraphNode) => void
}
```

---

## Theme Support

The app supports light and dark themes via `data-theme` attribute on `<html>`.

### Theme Detection

1. Check localStorage for saved preference
2. Fall back to OS preference (`prefers-color-scheme`)
3. Default to dark theme

### Adding Theme-Aware Styles

Styles automatically adapt via CSS custom properties. For theme-specific overrides:

```css
/* In themes/light.css */
[data-theme='light'] {
  --bg-primary: var(--color-gray-50);
  --text-primary: var(--color-gray-900);
}
```

---

## Best Practices

### Do

- Use semantic tokens for all colors
- Keep components small and focused
- Use CSS Modules for scoping
- Use Lucide icons consistently

### Don't

- Use inline styles
- Use raw color values
- Create deeply nested components
- Mix styling approaches (CSS-in-JS with CSS Modules)
- Forget to handle loading and error states

---

## Graph Node Colors

Node colors are defined in `config/index.ts` and should match semantic tokens:

| Node Type | Color |
|-----------|-------|
| Domain | Blue 900 |
| Subdomain | Blue 600 |
| IP | Teal 600 |
| Port | Cyan 700 |
| Service | Cyan 500 |
| Vulnerability | Red 500 |
| CVE | Red 600 |
| Technology | Green 500 |

---

## File Naming Conventions

- Components: `PascalCase.tsx`
- Styles: `PascalCase.module.css`
- Hooks: `camelCase.ts` (prefixed with `use`)
- Utils: `camelCase.ts`
- Types: `camelCase.ts` or `index.ts`
- Constants/Config: `camelCase.ts` or `index.ts`

---

## Next.js & React Architecture Principles

These principles separate "code that works" from "code that scales."

### 1. Single Responsibility (SOLID-S)

Each component, hook, or utility should do **one thing well**.

```tsx
// CORRECT: Separated concerns
function UserCard({ user }: { user: User }) {
  return <div>{user.name}</div>  // Only displays
}

function useUserData(id: string) {
  return useQuery({ queryKey: ['user', id], queryFn: () => fetchUser(id) })
}

// INCORRECT: Mixed responsibilities
function UserCard({ userId }: { userId: string }) {
  const [user, setUser] = useState(null)
  useEffect(() => { fetch(`/api/users/${userId}`).then(...) }, [])  // Fetching in display component
  return <div>{user?.name}</div>
}
```

### 2. Smart DRY (Don't Repeat Yourself)

Extract patterns only when they appear **3+ times** with the same purpose.

**Custom Hooks** - For repeated logic:
```tsx
// Extract when same pattern appears in multiple components
function useGraphData(projectId: string) {
  return useQuery({
    queryKey: ['graph', projectId],
    queryFn: () => fetchGraphData(projectId),
  })
}
```

**Avoid Hasty Abstractions (AHA)**: If two components look similar but serve different purposes, don't merge them. Wait until a clear pattern emerges.

### 3. KISS (Keep It Simple)

**State Minimalism**: Only use global state (Context) when data is needed across unrelated components. Otherwise, keep state local.

```tsx
// CORRECT: Local state for local concerns
function SearchInput() {
  const [query, setQuery] = useState('')  // Only this component needs it
  return <input value={query} onChange={e => setQuery(e.target.value)} />
}

// INCORRECT: Over-engineering with global state
// Don't put every piece of state in Context/Redux
```

**Readable JSX**: Avoid nested ternaries. Extract complex conditions.

```tsx
// CORRECT
const showEmptyState = !isLoading && nodes.length === 0
const showGraph = !isLoading && nodes.length > 0

return (
  <>
    {isLoading && <Loader />}
    {showEmptyState && <EmptyState />}
    {showGraph && <Graph nodes={nodes} />}
  </>
)

// INCORRECT
return isLoading ? <Loader /> : nodes.length === 0 ? <EmptyState /> : <Graph />
```

### 4. Single Source of Truth (SSOT)

Never duplicate state. Derive computed values instead.

```tsx
// CORRECT: Derive values
const { nodes, links } = graphData
const nodeCount = nodes.length           // Derived
const hasVulnerabilities = nodes.some(n => n.type === 'vulnerability')  // Derived

// INCORRECT: Duplicated state
const [nodes, setNodes] = useState([])
const [nodeCount, setNodeCount] = useState(0)  // Syncing nightmare
```

**URL as Source of Truth**: For filters, pagination, search - use URL query params.

```tsx
// Use searchParams instead of useState for shareable/bookmarkable state
const searchParams = useSearchParams()
const filter = searchParams.get('filter') ?? 'all'
```

### 5. YAGNI (You Ain't Gonna Need It)

Don't build for hypothetical future requirements.

| Don't Build | Until You Need |
|-------------|----------------|
| Complex state library (Redux) | `useState` + `useContext` becomes painful |
| Theme engine with 10 themes | More than 2 themes are actually needed |
| Generic abstraction layer | 3+ concrete implementations exist |
| Form library (Formik/React Hook Form) | Forms have complex validation needs |

### 6. Composition Over Configuration

Use component composition instead of prop-heavy components.

```tsx
// CORRECT: Composition
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>{content}</Card.Body>
  <Card.Footer><Button>Action</Button></Card.Footer>
</Card>

// INCORRECT: Prop overload
<Card
  title="Title"
  content={content}
  footerButtonText="Action"
  footerButtonOnClick={handleClick}
  showFooter={true}
  headerVariant="large"
  // ... 15 more props
/>
```

### 7. Interface Segregation (SOLID-I)

Pass only what components need, not entire objects.

```tsx
// CORRECT: Minimal props
function NodeLabel({ name, type }: { name: string; type: string }) {
  return <span className={styles[type]}>{name}</span>
}

// Usage
<NodeLabel name={node.name} type={node.type} />

// INCORRECT: Passing entire object
function NodeLabel({ node }: { node: GraphNode }) {
  return <span>{node.name}</span>  // Only uses name, but receives everything
}
```

### 8. Server vs Client Components (Next.js App Router)

**Default to Server Components**. Only use `'use client'` when needed.

| Use Client Component | Use Server Component |
|---------------------|---------------------|
| `useState`, `useEffect` | Data fetching |
| Event handlers (`onClick`) | Static rendering |
| Browser APIs | Database queries |
| Third-party client libraries | Sensitive logic (API keys) |

```tsx
// Server Component (default) - no directive needed
async function GraphPage({ params }: { params: { id: string } }) {
  const data = await fetchGraphData(params.id)  // Direct async
  return <GraphClient initialData={data} />
}

// Client Component - interactive features
'use client'
function GraphClient({ initialData }: { initialData: GraphData }) {
  const [selectedNode, setSelectedNode] = useState(null)
  return <ForceGraph data={initialData} onNodeClick={setSelectedNode} />
}
```

### 9. Error Boundaries & Loading States

Always handle the three states: loading, error, success.

```tsx
// In page or layout
import { Suspense } from 'react'

<Suspense fallback={<GraphSkeleton />}>
  <GraphContent />
</Suspense>

// With TanStack Query
const { data, isLoading, error } = useGraphData(projectId)

if (isLoading) return <Skeleton />
if (error) return <ErrorState message={error.message} />
return <Graph data={data} />
```

### Summary Checklist

Before creating a component or abstraction, ask:

- [ ] Does it have a single, clear responsibility?
- [ ] Is this pattern repeated 3+ times? (DRY check)
- [ ] Is this the simplest solution? (KISS check)
- [ ] Am I building for a real need, not a hypothetical? (YAGNI check)
- [ ] Is state stored in exactly one place? (SSOT check)
- [ ] Am I passing only necessary props? (Interface Segregation)
- [ ] Should this be a Server or Client Component?
