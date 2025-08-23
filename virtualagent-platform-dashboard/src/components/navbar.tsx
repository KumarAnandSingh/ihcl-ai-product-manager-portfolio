"use client"

import { UserButton } from "@/components/user-button"
import { MobileSidebar } from "@/components/sidebar"
import { ThemeToggle } from "@/components/theme-toggle"

export const Navbar = () => {
  return ( 
    <div className="flex items-center p-4">
      <MobileSidebar />
      <div className="flex w-full justify-end">
        <div className="flex items-center gap-x-2">
          <ThemeToggle />
          <UserButton />
        </div>
      </div>
    </div>
  )
}