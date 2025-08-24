"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import {
  BarChart3,
  Bot,
  Brain,
  Building2,
  Plug,
  Settings,
  Shield,
  Users,
  Activity,
  Play,
  Pause,
  RotateCcw,
  Zap,
  Phone,
  Wifi,
  Signal
} from "lucide-react"

const navigationItems = [
  {
    group: "Navigation",
    items: [
      { icon: BarChart3, label: "Dashboard", href: "/", shortcut: "⌘D" },
      { icon: Phone, label: "Customer Service", href: "/customer-service", shortcut: "⌘C" },
      { icon: Wifi, label: "Network Operations", href: "/network-operations", shortcut: "⌘N" },
      { icon: Signal, label: "Service Quality", href: "/service-quality", shortcut: "⌘Q" },
      { icon: Bot, label: "AI Agents", href: "/ai-agents", shortcut: "⌘A" },
      { icon: Activity, label: "Real-time Analytics", href: "/analytics", shortcut: "⌘L" },
      { icon: Brain, label: "AI Orchestration", href: "/ai-orchestration", shortcut: "⌘O" },
      { icon: Plug, label: "System Integrations", href: "/integrations", shortcut: "⌘I" },
      { icon: Users, label: "User Management", href: "/users", shortcut: "⌘U" },
      { icon: Shield, label: "Security & Compliance", href: "/security", shortcut: "⌘S" },
      { icon: Settings, label: "Platform Settings", href: "/settings", shortcut: "⌘," },
    ]
  }
]

const agentActions = [
  { icon: Play, label: "Start All AI Agents", action: "start-all" },
  { icon: Pause, label: "Pause Customer Service Agents", action: "pause-cs" },
  { icon: RotateCcw, label: "Restart Network Monitoring", action: "restart-network" },
  { icon: Zap, label: "Deploy Emergency Response", action: "deploy-emergency" },
  { icon: Activity, label: "View Live Performance", action: "view-performance" },
]

export function CommandPalette() {
  const [open, setOpen] = React.useState(false)
  const router = useRouter()

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  const handleSelect = (callback: () => void) => {
    setOpen(false)
    callback()
  }

  const handleAction = (action: string) => {
    console.log(`Executing telecom action: ${action}`)
    // Here you would implement the actual telecom-specific action logic
    switch(action) {
      case 'start-all':
        // Implement start all AI agents logic
        break
      case 'pause-cs':
        // Implement pause customer service agents logic
        break
      case 'restart-network':
        // Implement restart network monitoring logic
        break
      case 'deploy-emergency':
        // Implement emergency response deployment logic
        break
      case 'view-performance':
        router.push('/analytics')
        break
    }
  }

  return (
    <>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Search telecom operations, AI agents, or network tools..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          {navigationItems.map((group) => (
            <CommandGroup key={group.group} heading={group.group}>
              {group.items.map((item) => {
                const Icon = item.icon
                return (
                  <CommandItem
                    key={item.href}
                    value={item.label}
                    onSelect={() => handleSelect(() => router.push(item.href))}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    <span>{item.label}</span>
                    <span className="ml-auto text-xs text-muted-foreground">
                      {item.shortcut}
                    </span>
                  </CommandItem>
                )
              })}
            </CommandGroup>
          ))}
          <CommandSeparator />
          <CommandGroup heading="Telecom AI Actions">
            {agentActions.map((action) => {
              const Icon = action.icon
              return (
                <CommandItem
                  key={action.action}
                  value={action.label}
                  onSelect={() => handleSelect(() => handleAction(action.action))}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  <span>{action.label}</span>
                </CommandItem>
              )
            })}
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  )
}