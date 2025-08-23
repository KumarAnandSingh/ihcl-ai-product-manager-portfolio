"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { 
  Bot, 
  Activity, 
  MessageSquare, 
  TrendingUp, 
  Clock, 
  DollarSign,
  Play,
  Pause,
  Settings,
  Edit,
  Trash2,
  BarChart3,
  Users,
  Zap
} from "lucide-react"
import { toast } from "sonner"

interface Agent {
  id: string
  name: string
  version: string
  status: string
  type: string
  conversations: number
  successRate: number
  avgResponseTime: number
  cost: number
}

interface AgentDetailsModalProps {
  agent: Agent | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AgentDetailsModal({ agent, open, onOpenChange }: AgentDetailsModalProps) {
  const [activeTab, setActiveTab] = useState("overview")

  if (!agent) return null

  const handleAction = (action: string) => {
    toast.success(`${action} action initiated for ${agent.name}`)
  }

  // Mock additional data for the agent details
  const agentDetails = {
    ...agent,
    createdAt: "2024-01-15",
    lastUpdated: "2024-01-20",
    model: agent.type.includes("customer") ? "GPT-4" : agent.type.includes("sales") ? "Claude 3" : "GPT-3.5",
    language: "English",
    deployment: "Production",
    uptime: "99.8%",
    totalRequests: agent.conversations * 1.5,
    avgLatency: agent.avgResponseTime,
    errorRate: (100 - agent.successRate).toFixed(1),
    capabilities: agent.type.includes("customer") 
      ? ["Multi-language Support", "Sentiment Analysis", "CRM Integration", "Email Automation"]
      : agent.type.includes("sales")
      ? ["Lead Qualification", "CRM Integration", "Analytics Reporting", "Follow-up Management"] 
      : ["Custom Logic", "API Integration", "Data Processing", "Workflow Automation"],
    recentActivity: [
      { time: "2 hours ago", action: "Processed 45 conversations", type: "success" },
      { time: "5 hours ago", action: "Model parameters updated", type: "info" },
      { time: "1 day ago", action: "Deployed new version", type: "success" },
      { time: "2 days ago", action: "Performance optimization", type: "info" }
    ]
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <Bot className="h-6 w-6 text-primary" />
            <div>
              <DialogTitle className="text-xl">{agent.name}</DialogTitle>
              <DialogDescription>
                Version {agent.version} • {agentDetails.deployment} Environment
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {/* Quick Actions */}
        <div className="flex items-center gap-2 py-2">
          <Badge 
            variant={agent.status === 'active' ? 'default' : 
                    agent.status === 'error' ? 'destructive' : 'secondary'}
          >
            {agent.status}
          </Badge>
          <Badge variant="outline">{agentDetails.model}</Badge>
          <Badge variant="outline">{agent.type.replace('_', ' ')}</Badge>
          <div className="ml-auto flex gap-2">
            <Button size="sm" variant="outline" onClick={() => handleAction("Edit")}>
              <Edit className="h-4 w-4 mr-1" />
              Edit
            </Button>
            <Button 
              size="sm" 
              variant="outline" 
              onClick={() => handleAction(agent.status === 'active' ? "Pause" : "Start")}
            >
              {agent.status === 'active' ? (
                <><Pause className="h-4 w-4 mr-1" />Pause</>
              ) : (
                <><Play className="h-4 w-4 mr-1" />Start</>
              )}
            </Button>
            <Button size="sm" variant="outline" onClick={() => handleAction("Configure")}>
              <Settings className="h-4 w-4 mr-1" />
              Configure
            </Button>
          </div>
        </div>

        <Separator />

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="configuration">Configuration</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <MessageSquare className="h-6 w-6 mx-auto mb-2 text-blue-500" />
                <div className="text-2xl font-bold">{agent.conversations.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">Conversations</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <TrendingUp className="h-6 w-6 mx-auto mb-2 text-green-500" />
                <div className="text-2xl font-bold">{agent.successRate}%</div>
                <div className="text-sm text-muted-foreground">Success Rate</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <Clock className="h-6 w-6 mx-auto mb-2 text-orange-500" />
                <div className="text-2xl font-bold">{agent.avgResponseTime}s</div>
                <div className="text-sm text-muted-foreground">Avg Response</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <DollarSign className="h-6 w-6 mx-auto mb-2 text-purple-500" />
                <div className="text-2xl font-bold">${agent.cost.toFixed(2)}</div>
                <div className="text-sm text-muted-foreground">Monthly Cost</div>
              </div>
            </div>

            {/* Agent Information */}
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  Agent Information
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Type:</span>
                    <span className="capitalize">{agent.type.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Model:</span>
                    <span>{agentDetails.model}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Language:</span>
                    <span>{agentDetails.language}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Created:</span>
                    <span>{new Date(agentDetails.createdAt).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Last Updated:</span>
                    <span>{new Date(agentDetails.lastUpdated).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <Zap className="h-4 w-4" />
                  Capabilities
                </h3>
                <div className="flex flex-wrap gap-2">
                  {agentDetails.capabilities.map((capability, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {capability}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="font-semibold">Performance Metrics</h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Success Rate</span>
                      <span className="text-sm font-medium">{agent.successRate}%</span>
                    </div>
                    <Progress value={agent.successRate} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Uptime</span>
                      <span className="text-sm font-medium">{agentDetails.uptime}</span>
                    </div>
                    <Progress value={99.8} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Error Rate</span>
                      <span className="text-sm font-medium">{agentDetails.errorRate}%</span>
                    </div>
                    <Progress value={parseFloat(agentDetails.errorRate)} className="h-2 [&>div]:bg-red-500" />
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="font-semibold">System Health</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-2 border rounded">
                    <span className="text-sm">CPU Usage</span>
                    <Badge variant="outline" className="text-green-600">23%</Badge>
                  </div>
                  <div className="flex justify-between items-center p-2 border rounded">
                    <span className="text-sm">Memory Usage</span>
                    <Badge variant="outline" className="text-yellow-600">67%</Badge>
                  </div>
                  <div className="flex justify-between items-center p-2 border rounded">
                    <span className="text-sm">API Latency</span>
                    <Badge variant="outline" className="text-green-600">{agent.avgResponseTime}s</Badge>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="configuration" className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="font-semibold">Model Configuration</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between p-2 border rounded">
                    <span>Model:</span>
                    <span className="font-medium">{agentDetails.model}</span>
                  </div>
                  <div className="flex justify-between p-2 border rounded">
                    <span>Temperature:</span>
                    <span className="font-medium">0.7</span>
                  </div>
                  <div className="flex justify-between p-2 border rounded">
                    <span>Max Tokens:</span>
                    <span className="font-medium">2048</span>
                  </div>
                  <div className="flex justify-between p-2 border rounded">
                    <span>Response Format:</span>
                    <span className="font-medium">JSON</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="font-semibold">Deployment Settings</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between p-2 border rounded">
                    <span>Environment:</span>
                    <Badge variant="default">{agentDetails.deployment}</Badge>
                  </div>
                  <div className="flex justify-between p-2 border rounded">
                    <span>Auto-scaling:</span>
                    <Badge variant="secondary">Enabled</Badge>
                  </div>
                  <div className="flex justify-between p-2 border rounded">
                    <span>Load Balancing:</span>
                    <Badge variant="secondary">Active</Badge>
                  </div>
                  <div className="flex justify-between p-2 border rounded">
                    <span>Monitoring:</span>
                    <Badge variant="default">Real-time</Badge>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="activity" className="space-y-4">
            <div className="space-y-4">
              <h3 className="font-semibold">Recent Activity</h3>
              <div className="space-y-2">
                {agentDetails.recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                    <div className={`w-2 h-2 rounded-full ${
                      activity.type === 'success' ? 'bg-green-500' : 
                      activity.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter className="flex justify-between">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => handleAction("Export Data")}>
              Export Data
            </Button>
            <Button onClick={() => handleAction("Save Changes")}>
              Save Changes
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}