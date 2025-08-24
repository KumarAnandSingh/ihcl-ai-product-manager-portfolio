"use client"

import { UserButton } from "@/components/user-button"
import { MobileSidebar } from "@/components/sidebar"
import { ThemeToggle } from "@/components/theme-toggle"
import { Badge } from "@/components/ui/badge"
import { Search } from "lucide-react"

export const Navbar = () => {
  return ( 
    <div className="flex items-center p-4">
      <MobileSidebar />
      <div className="flex w-full justify-between items-center">
        <div className="flex items-center gap-x-3 ml-4">
          <div className="flex items-center gap-x-2 text-sm text-muted-foreground">
            <Search className="h-4 w-4" />
            <span>Press</span>
            <Badge variant="outline" className="px-1.5 py-0.5 text-xs">
              ⌘K
            </Badge>
            <span>to search</span>
          </div>
        </div>
        <div className="flex items-center gap-x-2">
          <ThemeToggle />
          <UserButton />
        </div>
      </div>
    </div>
  )
}