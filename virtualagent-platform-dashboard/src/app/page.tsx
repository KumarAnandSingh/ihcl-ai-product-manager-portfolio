"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AnimatedCard, AnimatedMetricCard } from "@/components/animated-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Activity, 
  AlertTriangle, 
  BarChart3, 
  Bot, 
  Brain, 
  DollarSign, 
  Plug, 
  Shield, 
  TrendingDown, 
  TrendingUp, 
  Users, 
  Zap 
} from "lucide-react"
import { 
  mockAgents, 
  mockOrganizations, 
  mockLLMModels, 
  mockIntegrations, 
  analyticsData,
  securityIncidents 
} from "@/lib/mock-data"
import { OverviewCharts } from "@/components/overview-charts"
import { AgentDetailsModal } from "@/components/modals/agent-details-modal"
import { toast } from "sonner"

export default function DashboardPage() {
  const router = useRouter()
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState(null)
  
  const handleCreateAgent = () => {
    router.push("/agents")
    toast.success("Navigating to Agent Management...")
  }

  const handleViewAgentDetails = (agent: any) => {
    setSelectedAgent(agent)
    setIsDetailsModalOpen(true)
  }
  const activeAgents = mockAgents.filter(agent => agent.status === 'active').length
  const totalConversations = mockAgents.reduce((sum, agent) => sum + agent.conversations, 0)
  const avgSuccessRate = mockAgents.reduce((sum, agent) => sum + agent.successRate, 0) / mockAgents.length
  const totalCost = mockAgents.reduce((sum, agent) => sum + agent.cost, 0)
  const totalOrganizations = mockOrganizations.length
  const totalIntegrations = mockIntegrations.filter(int => int.status === 'connected').length
  const criticalIncidents = securityIncidents.filter(inc => inc.severity === 'High').length

  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Enterprise Dashboard</h2>
        <div className="flex items-center space-x-2">
          <Button 
            onClick={handleCreateAgent}
            className="cursor-pointer hover:bg-primary/90 transition-colors"
          >
            Create Agent
          </Button>
        </div>
      </div>

      {/* Enhanced Agentic AI Metrics with Animations */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div onClick={() => router.push("/agentic-workflows")}>
          <AnimatedMetricCard
            title="Autonomous Workflows"
            value="23"
            description="87% success rate, 2.3s avg response"
            icon={Zap}
            trend="up"
            trendValue="5"
            delay={0}
          />
        </div>
        <AnimatedMetricCard
          title="Conversations"
          value={totalConversations.toLocaleString()}
          description="from last month"
          icon={Activity}
          trend="up"
          trendValue="15.2%"
          delay={0.1}
        />
        <AnimatedMetricCard
          title="Success Rate"
          value={`${avgSuccessRate.toFixed(1)}%`}
          description="from last month"
          icon={TrendingUp}
          trend="up"
          trendValue="1.5%"
          delay={0.2}
        />
        <AnimatedMetricCard
          title="Total Cost"
          value={`$${totalCost.toFixed(2)}`}
          description="from last month"
          icon={DollarSign}
          trend="down"
          trendValue="8.2%"
          delay={0.3}
        />
      </div>

      {/* Charts and Analytics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Analytics Overview</CardTitle>
          </CardHeader>
          <CardContent className="pl-2">
            <OverviewCharts />
          </CardContent>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>System Health</CardTitle>
            <CardDescription>Real-time platform status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="flex items-center space-x-2">
                  <Zap className="h-4 w-4 text-green-500" />
                  <span className="text-sm">API Gateway</span>
                </div>
                <div className="ml-auto">
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    Operational
                  </Badge>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex items-center space-x-2">
                  <Brain className="h-4 w-4 text-green-500" />
                  <span className="text-sm">LLM Services</span>
                </div>
                <div className="ml-auto">
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    Operational
                  </Badge>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex items-center space-x-2">
                  <Plug className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm">Integrations</span>
                </div>
                <div className="ml-auto">
                  <Badge variant="outline" className="text-yellow-600 border-yellow-600">
                    Degraded
                  </Badge>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex items-center space-x-2">
                  <Shield className="h-4 w-4 text-red-500" />
                  <span className="text-sm">Security</span>
                </div>
                <div className="ml-auto">
                  <Badge variant="outline" className="text-red-600 border-red-600">
                    {criticalIncidents} Alert{criticalIncidents !== 1 ? 's' : ''}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Views */}
      <Tabs defaultValue="agents" className="space-y-4">
        <TabsList>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="organizations">Organizations</TabsTrigger>
          <TabsTrigger value="models">LLM Models</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value="agents">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>Agent Management</CardTitle>
              <CardDescription>Overview of all deployed AI agents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAgents.map((agent) => (
                  <div 
                    key={agent.id} 
                    className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-accent/50 hover:shadow-md transition-all"
                    onClick={() => handleViewAgentDetails(agent)}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <Bot className="h-5 w-5" />
                        <div>
                          <p className="font-medium">{agent.name}</p>
                          <p className="text-sm text-muted-foreground">{agent.version}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="text-sm font-medium">{agent.conversations} conversations</p>
                        <p className="text-sm text-muted-foreground">{agent.successRate}% success rate</p>
                      </div>
                      <Badge 
                        variant={agent.status === 'active' ? 'default' : 
                                agent.status === 'error' ? 'destructive' : 
                                agent.status === 'deploying' ? 'secondary' : 'outline'}
                      >
                        {agent.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="organizations">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>Organization Management</CardTitle>
              <CardDescription>Multi-tenant organization overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockOrganizations.map((org) => (
                  <div key={org.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <Users className="h-5 w-5" />
                      <div>
                        <p className="font-medium">{org.name}</p>
                        <p className="text-sm text-muted-foreground">{org.plan} Plan</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-6">
                      <div className="text-right">
                        <p className="text-sm">{org.agents} agents</p>
                        <p className="text-sm text-muted-foreground">{org.users} users</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">${org.cost}</p>
                        <p className="text-sm text-muted-foreground">{org.apiCalls.toLocaleString()} calls</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="models">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>LLM Model Performance</CardTitle>
              <CardDescription>Multi-model orchestration and cost optimization</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockLLMModels.map((model) => (
                  <div key={model.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <Brain className="h-5 w-5" />
                      <div>
                        <p className="font-medium">{model.name}</p>
                        <p className="text-sm text-muted-foreground capitalize">{model.provider}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-6">
                      <div className="text-right">
                        <p className="text-sm">{model.tokensUsed.toLocaleString()} tokens</p>
                        <p className="text-sm text-muted-foreground">{model.avgLatency}s avg latency</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">${model.cost}</p>
                        <p className="text-sm text-muted-foreground">{model.successRate}% success</p>
                      </div>
                      <Badge 
                        variant={model.status === 'active' ? 'default' : 'secondary'}
                      >
                        {model.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>System Integrations</CardTitle>
              <CardDescription>Connected external systems and data sources</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockIntegrations.map((integration) => (
                  <div key={integration.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <Plug className="h-5 w-5" />
                      <div>
                        <p className="font-medium">{integration.name}</p>
                        <p className="text-sm text-muted-foreground">{integration.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-6">
                      <div className="text-right">
                        <p className="text-sm">{integration.dataVolume.toLocaleString()} records</p>
                        <p className="text-sm text-muted-foreground">
                          Last sync: {new Date(integration.lastSync).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge 
                        variant={integration.status === 'connected' ? 'default' : 
                                integration.status === 'error' ? 'destructive' : 
                                integration.status === 'syncing' ? 'secondary' : 'outline'}
                      >
                        {integration.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>Security & Compliance</CardTitle>
              <CardDescription>Recent security incidents and system health</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {securityIncidents.map((incident) => (
                  <div key={incident.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <AlertTriangle className={`h-5 w-5 ${
                        incident.severity === 'High' ? 'text-red-500' :
                        incident.severity === 'Medium' ? 'text-yellow-500' : 'text-blue-500'
                      }`} />
                      <div>
                        <p className="font-medium">{incident.type}</p>
                        <p className="text-sm text-muted-foreground">{incident.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="text-sm">{new Date(incident.timestamp).toLocaleString()}</p>
                        <Badge 
                          variant={
                            incident.severity === 'High' ? 'destructive' :
                            incident.severity === 'Medium' ? 'secondary' : 'outline'
                          }
                        >
                          {incident.severity}
                        </Badge>
                      </div>
                      <Badge variant="outline">
                        {incident.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      <AgentDetailsModal 
        agent={selectedAgent}
        open={isDetailsModalOpen} 
        onOpenChange={setIsDetailsModalOpen} 
      />
    </div>
  )
}
