'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Brain, 
  Zap, 
  Settings, 
  CheckCircle2, 
  AlertCircle,
  Clock,
  Target,
  TrendingUp,
  Activity
} from "lucide-react"
import { WorkflowSummaryImageGenerator, MetricsDashboardImageGenerator } from "@/components/image-generator"

interface WorkflowExecution {
  id: string
  name: string
  status: 'running' | 'completed' | 'failed' | 'paused'
  progress: number
  currentStep: string
  steps: Array<{
    id: string
    name: string
    status: 'completed' | 'running' | 'pending' | 'failed'
    duration: number
    toolsCalled: string[]
    confidence: number
  }>
  businessImpact: {
    costSaved: number
    timeReduced: string
    accuracy: number
  }
}

const mockWorkflows: WorkflowExecution[] = [
  {
    id: 'wf-001',
    name: 'Security Incident Response',
    status: 'running',
    progress: 75,
    currentStep: 'Coordinating notifications across hotel systems',
    steps: [
      {
        id: 'step-1',
        name: 'Risk Assessment & Analysis',
        status: 'completed',
        duration: 0.3,
        toolsCalled: ['RiskAnalyzer', 'PolicyRetriever'],
        confidence: 94
      },
      {
        id: 'step-2', 
        name: 'Autonomous Decision Making',
        status: 'completed',
        duration: 0.5,
        toolsCalled: ['DecisionEngine', 'ComplianceChecker'],
        confidence: 91
      },
      {
        id: 'step-3',
        name: 'Multi-System Tool Execution',
        status: 'completed', 
        duration: 1.2,
        toolsCalled: ['AccessControl', 'PMS', 'NotificationOrchestrator'],
        confidence: 96
      },
      {
        id: 'step-4',
        name: 'Outcome Monitoring & Adaptation',
        status: 'running',
        duration: 0,
        toolsCalled: ['MonitoringSystem'],
        confidence: 88
      }
    ],
    businessImpact: {
      costSaved: 15000,
      timeReduced: '12x faster',
      accuracy: 94
    }
  },
  {
    id: 'wf-002', 
    name: 'Guest Service Escalation',
    status: 'completed',
    progress: 100,
    currentStep: 'Workflow completed successfully',
    steps: [
      {
        id: 'step-1',
        name: 'Issue Classification',
        status: 'completed',
        duration: 0.2,
        toolsCalled: ['NLPClassifier', 'ContextAnalyzer'],
        confidence: 87
      },
      {
        id: 'step-2',
        name: 'Solution Planning',
        status: 'completed', 
        duration: 0.4,
        toolsCalled: ['SolutionEngine', 'ResourceOptimizer'],
        confidence: 92
      },
      {
        id: 'step-3',
        name: 'Cross-System Coordination',
        status: 'completed',
        duration: 0.8,
        toolsCalled: ['CRM', 'BookingSystem', 'StaffScheduler'],
        confidence: 89
      }
    ],
    businessImpact: {
      costSaved: 8500,
      timeReduced: '8x faster', 
      accuracy: 91
    }
  }
]

export default function AgenticWorkflowsPage() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowExecution | null>(mockWorkflows[0])
  const [isSimulating, setIsSimulating] = useState(false)

  const startSimulation = () => {
    setIsSimulating(true)
    // Simulate workflow progression
    setTimeout(() => setIsSimulating(false), 5000)
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Agentic Workflows</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={startSimulation} disabled={isSimulating}>
            <Play className="mr-2 h-4 w-4" />
            {isSimulating ? 'Simulating...' : 'Simulate Workflow'}
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground">
              +2 from yesterday
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.3s</div>
            <p className="text-xs text-muted-foreground">
              40% faster than baseline
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Automation Success</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87%</div>
            <p className="text-xs text-muted-foreground">
              +5% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cost Savings</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹8.4L</div>
            <p className="text-xs text-muted-foreground">
              Monthly per property
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Live Workflow Execution</CardTitle>
            <CardDescription>
              Real-time monitoring of autonomous agent workflows
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedWorkflow && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <h3 className="text-lg font-semibold">{selectedWorkflow.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {selectedWorkflow.currentStep}
                    </p>
                  </div>
                  <Badge 
                    variant={selectedWorkflow.status === 'running' ? 'default' : 
                            selectedWorkflow.status === 'completed' ? 'secondary' : 'destructive'}
                  >
                    {selectedWorkflow.status}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{selectedWorkflow.progress}%</span>
                  </div>
                  <Progress value={selectedWorkflow.progress} />
                </div>

                <div className="space-y-3">
                  {selectedWorkflow.steps.map((step, index) => (
                    <div key={step.id} className="flex items-start space-x-3 p-3 rounded-lg border">
                      <div className="mt-1">
                        {step.status === 'completed' && <CheckCircle2 className="h-4 w-4 text-green-600" />}
                        {step.status === 'running' && <Zap className="h-4 w-4 text-blue-600 animate-pulse" />}
                        {step.status === 'pending' && <Clock className="h-4 w-4 text-gray-400" />}
                        {step.status === 'failed' && <AlertCircle className="h-4 w-4 text-red-600" />}
                      </div>
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium">{step.name}</h4>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-muted-foreground">
                              {step.duration > 0 ? `${step.duration}s` : ''}
                            </span>
                            <Badge variant="outline" className="text-xs">
                              {step.confidence}% confidence
                            </Badge>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {step.toolsCalled.map((tool) => (
                            <Badge key={tool} variant="secondary" className="text-xs">
                              {tool}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Business Impact</CardTitle>
            <CardDescription>
              Real-time ROI and efficiency metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedWorkflow && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Cost Saved</span>
                    <span className="text-sm font-medium">
                      ₹{selectedWorkflow.businessImpact.costSaved.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Time Reduction</span>
                    <span className="text-sm font-medium">
                      {selectedWorkflow.businessImpact.timeReduced}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Accuracy</span>
                    <span className="text-sm font-medium">
                      {selectedWorkflow.businessImpact.accuracy}%
                    </span>
                  </div>
                </div>

                <div className="pt-4 border-t space-y-3">
                  <h4 className="text-sm font-medium">Workflow Controls</h4>
                  <div className="space-y-2">
                    <Button size="sm" className="w-full">
                      <Settings className="mr-2 h-4 w-4" />
                      Configure Workflow
                    </Button>
                    <Button size="sm" variant="outline" className="w-full">
                      <RotateCcw className="mr-2 h-4 w-4" />
                      Restart Workflow
                    </Button>
                    <Button size="sm" variant="outline" className="w-full">
                      <Pause className="mr-2 h-4 w-4" />
                      Pause Execution
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="active" className="space-y-4">
        <TabsList>
          <TabsTrigger value="active">Active Workflows</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>
        
        <TabsContent value="active" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Workflow Instances</CardTitle>
              <CardDescription>
                Currently running autonomous agent workflows
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mockWorkflows.filter(w => w.status === 'running').map((workflow) => (
                  <div 
                    key={workflow.id} 
                    className="flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-muted/50"
                    onClick={() => setSelectedWorkflow(workflow)}
                  >
                    <div className="space-y-1">
                      <h4 className="text-sm font-medium">{workflow.name}</h4>
                      <p className="text-xs text-muted-foreground">{workflow.currentStep}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Progress value={workflow.progress} className="w-20" />
                      <span className="text-xs text-muted-foreground w-10">{workflow.progress}%</span>
                      <Badge variant="default">Running</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="completed" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Completed Workflows</CardTitle>
              <CardDescription>
                Successfully executed autonomous workflows
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mockWorkflows.filter(w => w.status === 'completed').map((workflow) => (
                  <div 
                    key={workflow.id}
                    className="flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-muted/50"
                    onClick={() => setSelectedWorkflow(workflow)}
                  >
                    <div className="space-y-1">
                      <h4 className="text-sm font-medium">{workflow.name}</h4>
                      <p className="text-xs text-muted-foreground">
                        Saved ₹{workflow.businessImpact.costSaved.toLocaleString()} • {workflow.businessImpact.accuracy}% accuracy
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <Badge variant="secondary">Completed</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Templates</CardTitle>
              <CardDescription>
                Pre-built agentic workflow templates for common hotel operations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                {[
                  {
                    name: "Security Incident Response",
                    description: "Autonomous security incident triage and response coordination",
                    tools: ["RiskAnalyzer", "AccessControl", "NotificationOrchestrator"],
                    avgTime: "2.3s"
                },
                {
                    name: "Guest Service Recovery",
                    description: "Automated guest complaint resolution and service recovery",
                    tools: ["SentimentAnalyzer", "CRM", "RewardSystem"],
                    avgTime: "1.8s"
                },
                {
                    name: "Revenue Optimization",
                    description: "Dynamic pricing and inventory management workflows",
                    tools: ["PricingEngine", "DemandForecaster", "InventoryManager"],
                    avgTime: "3.1s"
                },
                {
                    name: "Operational Efficiency",
                    description: "Staff scheduling and resource allocation optimization",
                    tools: ["StaffScheduler", "ResourcePlanner", "EfficiencyTracker"],
                    avgTime: "2.7s"
                }
                ].map((template) => (
                  <div key={template.name} className="p-4 border rounded-lg space-y-3">
                    <div>
                      <h4 className="text-sm font-medium">{template.name}</h4>
                      <p className="text-xs text-muted-foreground">{template.description}</p>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {template.tools.map((tool) => (
                        <Badge key={tool} variant="outline" className="text-xs">
                          {tool}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Avg: {template.avgTime}</span>
                      <Button size="sm" variant="outline">Deploy</Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dynamic Image Generation Section */}
      <div className="grid gap-4 md:grid-cols-2">
        <WorkflowSummaryImageGenerator 
          workflowData={selectedWorkflow}
        />
        <MetricsDashboardImageGenerator 
          metricsData={{
            metrics: [
              { label: 'Autonomous Decisions', value: '87%', color: '#8b5cf6' },
              { label: 'Tool Executions', value: '2,398', color: '#3b82f6' },
              { label: 'Success Rate', value: '94%', color: '#10b981' },
              { label: 'Cost Savings', value: '₹8.4L', color: '#f59e0b' }
            ]
          }}
        />
      </div>
    </div>
  )
}