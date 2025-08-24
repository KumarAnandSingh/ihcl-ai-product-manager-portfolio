"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { AgentCreationModal } from "@/components/modals/agent-creation-modal"
import { AgentDetailsModal } from "@/components/modals/agent-details-modal"
import { 
  Bot, 
  Play, 
  Pause, 
  Settings, 
  MoreHorizontal, 
  TrendingUp,
  Clock,
  MessageSquare,
  DollarSign,
  Upload,
  Eye,
  Zap,
  Activity,
  CheckCircle2,
  AlertCircle
} from "lucide-react"
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { mockAgents } from "@/lib/mock-data"
import { toast } from "sonner"

export default function AgentsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState(null)

  const handleDeployAgent = () => {
    setIsCreateModalOpen(true)
  }

  const handleImportTemplate = () => {
    toast.success("Template import feature coming soon!")
  }

  const handleViewDetails = (agentName: string) => {
    const agent = mockAgents.find(a => a.name === agentName)
    if (agent) {
      setSelectedAgent(agent)
      setIsDetailsModalOpen(true)
    }
  }

  const handleToggleAgent = (agentName: string, isActive: boolean) => {
    const action = isActive ? "paused" : "started"
    toast.success(`${agentName} ${action} successfully!`)
  }

  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Agent Management</h2>
        <div className="flex items-center space-x-2">
          <Button 
            onClick={handleDeployAgent}
            className="cursor-pointer hover:bg-primary/90 transition-colors"
          >
            Deploy New Agent
          </Button>
          <Button 
            variant="outline" 
            onClick={handleImportTemplate}
            className="cursor-pointer hover:bg-accent transition-colors"
          >
            <Upload className="h-4 w-4 mr-2" />
            Import Template
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {mockAgents.map((agent) => (
          <Card key={agent.id} className="relative hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="flex items-center space-x-2">
                <Bot className="h-5 w-5" />
                <div>
                  <CardTitle className="text-base">{agent.name}</CardTitle>
                  <CardDescription>{agent.version}</CardDescription>
                </div>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-8 w-8 p-0 cursor-pointer hover:bg-accent transition-colors">
                    <span className="sr-only">Open menu</span>
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Actions</DropdownMenuLabel>
                  <DropdownMenuItem onClick={() => handleViewDetails(agent.name)} className="cursor-pointer">
                    <Eye className="mr-2 h-4 w-4" />
                    View Details
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleToggleAgent(agent.name, agent.status === 'active')} className="cursor-pointer">
                    {agent.status === 'active' ? (
                      <>
                        <Pause className="mr-2 h-4 w-4" />
                        Pause
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Start
                      </>
                    )}
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer">
                    <Settings className="mr-2 h-4 w-4" />
                    Configure
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-red-600 cursor-pointer">
                    Delete agent
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Badge 
                  variant={agent.status === 'active' ? 'default' : 
                          agent.status === 'error' ? 'destructive' : 
                          agent.status === 'deploying' ? 'secondary' : 'outline'}
                >
                  {agent.status}
                </Badge>
                <span className="text-sm text-muted-foreground capitalize">
                  {agent.type.replace('_', ' ')}
                </span>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="h-4 w-4 text-muted-foreground" />
                    <span>Conversations</span>
                  </div>
                  <span className="font-medium">{agent.conversations.toLocaleString()}</span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                      <span>Success Rate</span>
                    </div>
                    <span className="font-medium">{agent.successRate}%</span>
                  </div>
                  <Progress value={agent.successRate} className="h-2" />
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span>Avg Response</span>
                  </div>
                  <span className="font-medium">{agent.avgResponseTime}s</span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                    <span>Cost (30d)</span>
                  </div>
                  <span className="font-medium">${agent.cost.toFixed(2)}</span>
                </div>
              </div>

              <div className="pt-2">
                <Button 
                  className="w-full cursor-pointer" 
                  size="sm"
                  onClick={() => handleViewDetails(agent.name)}
                >
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-purple-600" />
            Agent Execution Monitor
          </CardTitle>
          <CardDescription>
            Real-time monitoring of agentic workflow executions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Live Execution Card */}
            <div className="border rounded-lg p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-purple-600 animate-pulse" />
                  <span className="font-medium text-sm">Security Response Agent</span>
                </div>
                <Badge variant="default" className="animate-pulse">Executing</Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Processing unauthorized access incident - coordinating multi-system response
              </p>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3 text-green-600" />
                  3 tools completed
                </div>
                <div className="flex items-center gap-1">
                  <Activity className="h-3 w-3 text-blue-600" />
                  1 tool running
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  2.1s elapsed
                </div>
              </div>
              <Progress value={75} className="mt-3 h-2" />
            </div>

            {/* Recent Completions */}
            <div className="grid gap-2 md:grid-cols-2">
              <div className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">Guest Service Agent</span>
                  <Badge variant="secondary">Completed</Badge>
                </div>
                <p className="text-xs text-muted-foreground mb-2">
                  Resolved guest complaint autonomously - 91% confidence
                </p>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>₹8,500 cost saved</span>
                  <span>1.8s execution</span>
                </div>
              </div>

              <div className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">Revenue Optimization Agent</span>
                  <Badge variant="secondary">Completed</Badge>
                </div>
                <p className="text-xs text-muted-foreground mb-2">
                  Dynamic pricing adjustment - 94% confidence decision
                </p>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>₹15,000 revenue gain</span>
                  <span>3.1s execution</span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="text-sm text-muted-foreground">
                <span className="font-medium text-green-600">87%</span> automation success rate
              </div>
              <Button variant="outline" size="sm" asChild>
                <a href="/agentic-workflows">View All Workflows →</a>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Agent Creation Wizard</CardTitle>
          <CardDescription>
            Create a new AI agent with our guided setup process
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="border-dashed hover:shadow-md hover:border-solid hover:border-primary/20 transition-all cursor-pointer">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Bot className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Customer Service</h3>
                  <p className="text-sm text-muted-foreground">
                    Handle customer inquiries and support requests
                  </p>
                </div>
                <Button className="w-full cursor-pointer hover:bg-primary/90 transition-colors" onClick={handleDeployAgent}>Create Agent</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed hover:shadow-md hover:border-solid hover:border-primary/20 transition-all cursor-pointer">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Bot className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Sales Assistant</h3>
                  <p className="text-sm text-muted-foreground">
                    Qualify leads and assist with sales processes
                  </p>
                </div>
                <Button className="w-full cursor-pointer hover:bg-primary/90 transition-colors" onClick={handleDeployAgent}>Create Agent</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed hover:shadow-md hover:border-solid hover:border-primary/20 transition-all cursor-pointer">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Bot className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Custom Agent</h3>
                  <p className="text-sm text-muted-foreground">
                    Build a specialized agent for your use case
                  </p>
                </div>
                <Button className="w-full cursor-pointer hover:bg-primary/90 transition-colors" onClick={handleDeployAgent}>Create Agent</Button>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      <AgentCreationModal 
        open={isCreateModalOpen} 
        onOpenChange={setIsCreateModalOpen} 
      />
      
      <AgentDetailsModal 
        agent={selectedAgent}
        open={isDetailsModalOpen} 
        onOpenChange={setIsDetailsModalOpen} 
      />
    </div>
  )
}