"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface AnimatedCardProps {
  children: React.ReactNode
  className?: string
  delay?: number
  variant?: "slide" | "fade" | "scale" | "bounce"
  hover?: boolean
  onClick?: () => void
}

const variants = {
  slide: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  },
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 }
  },
  scale: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 }
  },
  bounce: {
    initial: { opacity: 0, scale: 0.8, y: 20 },
    animate: { 
      opacity: 1, 
      scale: 1, 
      y: 0,
      transition: {
        type: "spring",
        damping: 10,
        stiffness: 100
      }
    },
    exit: { opacity: 0, scale: 0.8, y: 20 }
  }
}

const hoverVariants = {
  initial: { scale: 1, boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" },
  hover: { 
    scale: 1.02, 
    boxShadow: "0 25px 50px -12px rgb(0 0 0 / 0.25)",
    transition: { duration: 0.2 }
  }
}

export function AnimatedCard({ 
  children, 
  className, 
  delay = 0, 
  variant = "slide", 
  hover = true,
  onClick 
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={variants[variant].initial}
      animate={variants[variant].animate}
      exit={variants[variant].exit}
      variants={hover ? hoverVariants : undefined}
      whileHover={hover ? "hover" : undefined}
      transition={{ 
        duration: 0.3, 
        delay: delay,
        ease: "easeOut"
      }}
      className={cn("cursor-pointer", onClick && "cursor-pointer", className)}
      onClick={onClick}
    >
      <Card className="h-full border-0 bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 backdrop-blur-sm">
        {children}
      </Card>
    </motion.div>
  )
}

interface AnimatedMetricCardProps {
  title: string
  value: string | number
  description?: string
  icon?: React.ComponentType<{ className?: string }>
  trend?: "up" | "down" | "neutral"
  trendValue?: string
  delay?: number
  className?: string
}

export function AnimatedMetricCard({
  title,
  value,
  description,
  icon: Icon,
  trend = "neutral",
  trendValue,
  delay = 0,
  className
}: AnimatedMetricCardProps) {
  const trendColors = {
    up: "text-green-600",
    down: "text-red-600", 
    neutral: "text-muted-foreground"
  }

  return (
    <AnimatedCard delay={delay} className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {Icon && (
          <motion.div
            initial={{ rotate: 0 }}
            animate={{ rotate: 360 }}
            transition={{ duration: 2, delay: delay + 0.5, ease: "easeInOut" }}
          >
            <Icon className="h-4 w-4 text-muted-foreground" />
          </motion.div>
        )}
      </CardHeader>
      <CardContent>
        <motion.div 
          className="text-2xl font-bold"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ 
            type: "spring",
            stiffness: 100,
            delay: delay + 0.2
          }}
        >
          {value}
        </motion.div>
        {(description || trendValue) && (
          <motion.p 
            className={cn("text-xs", trendColors[trend])}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: delay + 0.4 }}
          >
            {trendValue && (
              <span className={trendColors[trend]}>
                {trend === "up" ? "+" : trend === "down" ? "-" : ""}{trendValue}
              </span>
            )}
            {description && <span className="text-muted-foreground"> {description}</span>}
          </motion.p>
        )}
      </CardContent>
    </AnimatedCard>
  )
}