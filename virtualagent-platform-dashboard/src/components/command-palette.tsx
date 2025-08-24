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
  Zap
} from "lucide-react"

const navigationItems = [
  {
    group: "Navigation",
    items: [
      { icon: BarChart3, label: "Dashboard", href: "/", shortcut: "⌘D" },
      { icon: Bot, label: "Agent Management", href: "/agents", shortcut: "⌘A" },
      { icon: Activity, label: "Agentic Workflows", href: "/agentic-workflows", shortcut: "⌘W" },
      { icon: BarChart3, label: "Analytics", href: "/analytics", shortcut: "⌘L" },
      { icon: Brain, label: "LLM Orchestration", href: "/llm-orchestration", shortcut: "⌘O" },
      { icon: Plug, label: "Integrations", href: "/integrations", shortcut: "⌘I" },
      { icon: Building2, label: "Organizations", href: "/organizations", shortcut: "⌘G" },
      { icon: Users, label: "Access Control", href: "/access-control", shortcut: "⌘U" },
      { icon: Shield, label: "Security", href: "/security", shortcut: "⌘S" },
      { icon: Settings, label: "Settings", href: "/settings", shortcut: "⌘," },
    ]
  }
]

const agentActions = [
  { icon: Play, label: "Start All Agents", action: "start-all" },
  { icon: Pause, label: "Pause All Agents", action: "pause-all" },
  { icon: RotateCcw, label: "Restart Failed Agents", action: "restart-failed" },
  { icon: Zap, label: "Deploy New Agent", action: "deploy-agent" },
  { icon: Activity, label: "View Agent Metrics", action: "view-metrics" },
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
    console.log(`Executing action: ${action}`)
    // Here you would implement the actual action logic
    switch(action) {
      case 'start-all':
        // Implement start all agents logic
        break
      case 'pause-all':
        // Implement pause all agents logic
        break
      case 'restart-failed':
        // Implement restart failed agents logic
        break
      case 'deploy-agent':
        router.push('/agents')
        break
      case 'view-metrics':
        router.push('/analytics')
        break
    }
  }

  return (
    <>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Type a command or search..." />
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
          <CommandGroup heading="Agent Actions">
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