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
  Shield,
  AlertTriangle,
  Activity,
  Settings,
  Search,
  Users,
  FileText,
  Lock,
  Eye,
  Zap,
  Play,
  Pause,
  RotateCcw,
  AlertCircle
} from "lucide-react"

const navigationItems = [
  {
    group: "Security Operations",
    items: [
      { icon: Shield, label: "Security Dashboard", href: "/", shortcut: "⌘D" },
      { icon: AlertTriangle, label: "Incident Response", href: "/incidents", shortcut: "⌘I" },
      { icon: Activity, label: "Live Monitoring", href: "/monitoring", shortcut: "⌘M" },
      { icon: Search, label: "Threat Intelligence", href: "/intelligence", shortcut: "⌘T" },
      { icon: Eye, label: "Surveillance", href: "/surveillance", shortcut: "⌘S" },
      { icon: Users, label: "Access Control", href: "/access", shortcut: "⌘A" },
      { icon: FileText, label: "Audit Logs", href: "/audit", shortcut: "⌘L" },
      { icon: Lock, label: "Compliance", href: "/compliance", shortcut: "⌘C" },
      { icon: Settings, label: "Configuration", href: "/settings", shortcut: "⌘," },
    ]
  }
]

const securityActions = [
  { icon: Play, label: "Activate Emergency Protocol", action: "emergency" },
  { icon: AlertCircle, label: "Trigger Security Alert", action: "alert" },
  { icon: Pause, label: "Pause Non-Critical Systems", action: "pause" },
  { icon: RotateCcw, label: "Reset Access Controls", action: "reset-access" },
  { icon: Zap, label: "Deploy Countermeasures", action: "countermeasures" },
  { icon: Shield, label: "Enable Lockdown Mode", action: "lockdown" },
]

export function SecurityCommandPalette() {
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
    console.log(`Executing security action: ${action}`)
    // Here you would implement the actual security action logic
    switch(action) {
      case 'emergency':
        // Implement emergency protocol activation
        break
      case 'alert':
        // Implement security alert trigger
        break
      case 'pause':
        // Implement system pause logic
        break
      case 'reset-access':
        // Implement access control reset
        break
      case 'countermeasures':
        // Implement countermeasures deployment
        break
      case 'lockdown':
        router.push('/incidents')
        break
    }
  }

  return (
    <>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Search security operations, incidents, or execute commands..." />
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
          <CommandGroup heading="Security Actions">
            {securityActions.map((action) => {
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