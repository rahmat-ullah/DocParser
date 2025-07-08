# UI Primitives

This directory contains reusable UI primitive components that use Tailwind theme tokens for consistent theming.

## Components

### Button
A versatile button component with multiple variants and sizes.

```tsx
import { Button } from '@/components/ui/button';

<Button variant="default" size="lg">Click me</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline" size="sm">Cancel</Button>
```

### IconButton
A specialized button for icons with hover states and multiple variants.

```tsx
import { IconButton } from '@/components/ui/icon-button';
import { Search, Settings } from 'lucide-react';

<IconButton icon={<Search className="w-4 h-4" />} variant="ghost" />
<IconButton icon={<Settings className="w-5 h-5" />} variant="default" size="lg" />
```

### Panel
A versatile container component with header, content, and footer sections.

```tsx
import { Panel, PanelHeader, PanelTitle, PanelContent } from '@/components/ui/panel';

<Panel variant="elevated">
  <PanelHeader>
    <PanelTitle>Settings</PanelTitle>
  </PanelHeader>
  <PanelContent>
    Content goes here
  </PanelContent>
</Panel>
```

### Sidebar
A sidebar component with sections for navigation and content organization.

```tsx
import { 
  Sidebar, 
  SidebarHeader, 
  SidebarTitle, 
  SidebarContent, 
  SidebarItem 
} from '@/components/ui/sidebar';

<Sidebar>
  <SidebarHeader>
    <SidebarTitle>Navigation</SidebarTitle>
  </SidebarHeader>
  <SidebarContent>
    <SidebarItem active>Dashboard</SidebarItem>
    <SidebarItem>Settings</SidebarItem>
  </SidebarContent>
</Sidebar>
```

## Theme Tokens

All components use Tailwind CSS theme tokens defined in the configuration:

- `text-foreground` - Primary text color
- `text-muted-foreground` - Secondary text color  
- `bg-background` - Background color
- `bg-card` - Card background
- `bg-primary` - Primary brand color
- `bg-secondary` - Secondary background
- `bg-muted` - Muted background
- `border-border` - Border color
- `border-input` - Input border color

## Dark Mode

All components automatically support dark mode through CSS custom properties defined in `globals.css`. The theme tokens adapt to the current color scheme.

## Future Palette Changes

To change the entire color palette, simply update the CSS custom properties in `app/globals.css`:

```css
:root {
  --primary: 234 64% 25%; /* HSL values */
  --secondary: 0 0% 100%;
  /* etc. */
}
```

All components will automatically adapt to the new colors.
