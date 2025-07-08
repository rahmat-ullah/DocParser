import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const sidebarVariants = cva(
  'flex flex-col h-full bg-card border-border overflow-hidden',
  {
    variants: {
      variant: {
        default: 'bg-card border-r border-border',
        floating: 'bg-card border border-border rounded-lg shadow-lg m-2',
        transparent: 'bg-transparent border-0',
        secondary: 'bg-secondary border-r border-border',
      },
      width: {
        sm: 'w-64',
        default: 'w-80',
        lg: 'w-96',
        auto: 'w-auto',
        full: 'w-full',
      },
      position: {
        left: 'order-first',
        right: 'order-last',
      },
    },
    defaultVariants: {
      variant: 'default',
      width: 'default',
      position: 'left',
    },
  }
);

export interface SidebarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof sidebarVariants> {}

const Sidebar = React.forwardRef<HTMLDivElement, SidebarProps>(
  ({ className, variant, width, position, ...props }, ref) => {
    return (
      <aside
        className={cn(sidebarVariants({ variant, width, position, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Sidebar.displayName = 'Sidebar';

const SidebarHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex flex-col space-y-2 p-4 border-b border-border bg-background/50',
      className
    )}
    {...props}
  />
));
SidebarHeader.displayName = 'SidebarHeader';

const SidebarTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h2
    ref={ref}
    className={cn(
      'text-lg font-semibold text-foreground leading-none tracking-tight',
      className
    )}
    {...props}
  />
));
SidebarTitle.displayName = 'SidebarTitle';

const SidebarContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex-1 overflow-auto', className)}
    {...props}
  />
));
SidebarContent.displayName = 'SidebarContent';

const SidebarFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center justify-between p-4 border-t border-border bg-background/50',
      className
    )}
    {...props}
  />
));
SidebarFooter.displayName = 'SidebarFooter';

const SidebarSection = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('space-y-2 p-2', className)}
    {...props}
  />
));
SidebarSection.displayName = 'SidebarSection';

const SidebarItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    active?: boolean;
    disabled?: boolean;
  }
>(({ className, active, disabled, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-colors',
      active && 'bg-primary/10 text-primary border border-primary/20',
      !active && 'hover:bg-accent hover:text-accent-foreground',
      disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
      className
    )}
    {...props}
  />
));
SidebarItem.displayName = 'SidebarItem';

export {
  Sidebar,
  SidebarHeader,
  SidebarTitle,
  SidebarContent,
  SidebarFooter,
  SidebarSection,
  SidebarItem,
  sidebarVariants,
};
