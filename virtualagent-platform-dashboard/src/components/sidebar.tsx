"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import {
  BarChart3,
  Bot,
  Brain,
  Building2,
  Menu,
  Plug,
  Settings,
  Shield,
  Users,
  Zap,
  Activity,
} from "lucide-react"

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()

  const routes = [
    {
      label: "Dashboard",
      icon: BarChart3,
      href: "/",
      color: "text-sky-500"
    },
    {
      label: "Agent Management",
      icon: Bot,
      href: "/agents",
      color: "text-violet-500",
    },
    {
      label: "Agentic Workflows",
      icon: Activity,
      href: "/agentic-workflows",
      color: "text-purple-600",
    },
    {
      label: "Analytics",
      icon: BarChart3,
      href: "/analytics",
      color: "text-pink-700",
    },
    {
      label: "LLM Orchestration",
      icon: Brain,
      href: "/llm-orchestration",
      color: "text-orange-700",
    },
    {
      label: "Integrations",
      icon: Plug,
      href: "/integrations",
      color: "text-green-700",
    },
    {
      label: "Organizations",
      icon: Building2,
      href: "/organizations",
      color: "text-blue-700",
    },
    {
      label: "Access Control",
      icon: Users,
      href: "/access-control",
      color: "text-indigo-700",
    },
    {
      label: "Security",
      icon: Shield,
      href: "/security",
      color: "text-red-700",
    },
    {
      label: "Settings",
      icon: Settings,
      href: "/settings",
      color: "text-gray-700",
    },
  ]

  return (
    <div className={cn("pb-12", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <div className="space-y-1">
            <div className="flex items-center pl-3 mb-14">
              <div className="relative h-8 w-8 mr-4">
                <Zap className="h-8 w-8 text-blue-600" />
              </div>
              <h1 className="text-2xl font-bold">VirtualAgent Platform</h1>
            </div>
            {routes.map((route) => (
              <Link
                key={route.href}
                href={route.href}
                className={cn(
                  "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:text-primary hover:bg-primary/10 rounded-lg transition",
                  pathname === route.href ? "text-primary bg-primary/10" : "text-muted-foreground"
                )}
              >
                <div className="flex items-center flex-1">
                  <route.icon className={cn("h-5 w-5 mr-3", route.color)} />
                  {route.label}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export function MobileSidebar() {
  const pathname = usePathname()

  const routes = [
    {
      label: "Dashboard",
      icon: BarChart3,
      href: "/",
      color: "text-sky-500"
    },
    {
      label: "Agent Management",
      icon: Bot,
      href: "/agents",
      color: "text-violet-500",
    },
    {
      label: "Agentic Workflows",
      icon: Activity,
      href: "/agentic-workflows",
      color: "text-purple-600",
    },
    {
      label: "Analytics",
      icon: BarChart3,
      href: "/analytics",
      color: "text-pink-700",
    },
    {
      label: "LLM Orchestration",
      icon: Brain,
      href: "/llm-orchestration",
      color: "text-orange-700",
    },
    {
      label: "Integrations",
      icon: Plug,
      href: "/integrations",
      color: "text-green-700",
    },
    {
      label: "Organizations",
      icon: Building2,
      href: "/organizations",
      color: "text-blue-700",
    },
    {
      label: "Access Control",
      icon: Users,
      href: "/access-control",
      color: "text-indigo-700",
    },
    {
      label: "Security",
      icon: Shield,
      href: "/security",
      color: "text-red-700",
    },
    {
      label: "Settings",
      icon: Settings,
      href: "/settings",
      color: "text-gray-700",
    },
  ]

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="p-0">
        <div className="space-y-4 py-4">
          <div className="px-3 py-2">
            <div className="space-y-1">
              <div className="flex items-center pl-3 mb-14">
                <div className="relative h-8 w-8 mr-4">
                  <Zap className="h-8 w-8 text-blue-600" />
                </div>
                <h1 className="text-2xl font-bold">VirtualAgent</h1>
              </div>
              {routes.map((route) => (
                <Link
                  key={route.href}
                  href={route.href}
                  className={cn(
                    "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:text-primary hover:bg-primary/10 rounded-lg transition",
                    pathname === route.href ? "text-primary bg-primary/10" : "text-muted-foreground"
                  )}
                >
                  <div className="flex items-center flex-1">
                    <route.icon className={cn("h-5 w-5 mr-3", route.color)} />
                    {route.label}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}