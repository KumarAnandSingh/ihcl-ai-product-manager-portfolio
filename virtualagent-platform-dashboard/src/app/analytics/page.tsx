"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  PieChart, 
  Pie, 
  Cell,
  ResponsiveContainer, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Users, 
  Clock,
  DollarSign,
  MessageSquare,
  ThumbsUp,
  Brain,
  Zap,
  Target,
  Shield,
  CheckCircle2
} from "lucide-react"
import { analyticsData } from "@/lib/mock-data"

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export default function AnalyticsPage() {
  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Analytics & Monitoring</h2>
      </div>

      {/* Agentic AI Performance Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Autonomous Decision Rate</CardTitle>
            <Brain className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87%</div>
            <p className="text-xs text-green-600">
              +12% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tool Execution Success</CardTitle>
            <Zap className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94%</div>
            <p className="text-xs text-green-600">
              +8% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Multi-Step Workflows</CardTitle>
            <Target className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">156</div>
            <p className="text-xs text-green-600">
              +23 from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Business Impact Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹8.4L</div>
            <p className="text-xs text-green-600">
              Monthly value generated
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="agentic" className="space-y-4">
        <TabsList>
          <TabsTrigger value="agentic">Agentic AI Metrics</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="costs">Cost Analysis</TabsTrigger>
          <TabsTrigger value="usage">Usage Patterns</TabsTrigger>
        </TabsList>

        <TabsContent value="agentic">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Autonomous Decision Trends</CardTitle>
                <CardDescription>
                  Agent decision-making confidence and success rates over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={[
                    { month: 'Jan', decisions: 1247, success: 89, confidence: 91 },
                    { month: 'Feb', decisions: 1456, success: 91, confidence: 93 },
                    { month: 'Mar', decisions: 1689, success: 94, confidence: 94 },
                    { month: 'Apr', decisions: 1823, success: 87, confidence: 92 },
                    { month: 'May', decisions: 2145, success: 93, confidence: 95 },
                    { month: 'Jun', decisions: 2398, success: 96, confidence: 97 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="decisions" 
                      stroke="#8884d8" 
                      strokeWidth={2}
                      name="Total Decisions"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="success" 
                      stroke="#82ca9d" 
                      strokeWidth={2}
                      name="Success Rate %"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="confidence" 
                      stroke="#ff8042" 
                      strokeWidth={2}
                      name="Confidence %"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tool Integration Performance</CardTitle>
                <CardDescription>
                  Multi-system tool execution success by category
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    { category: 'Access Control', executions: 456, success: 94 },
                    { category: 'Payment Systems', executions: 234, success: 91 },
                    { category: 'Notifications', executions: 789, success: 97 },
                    { category: 'Hotel PMS', executions: 345, success: 89 },
                    { category: 'Security Systems', executions: 123, success: 88 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="executions" fill="#8884d8" name="Total Executions" />
                    <Bar dataKey="success" fill="#82ca9d" name="Success Rate %" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Workflow Complexity Analysis</CardTitle>
                <CardDescription>
                  Multi-step workflow execution patterns
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { steps: '2-3 Steps', workflows: 234, avgTime: '1.2s', success: 97 },
                    { steps: '4-6 Steps', workflows: 156, avgTime: '2.8s', success: 94 },
                    { steps: '7+ Steps', workflows: 89, avgTime: '4.1s', success: 87 }
                  ].map((workflow) => (
                    <div key={workflow.steps} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{workflow.steps}</p>
                        <p className="text-sm text-muted-foreground">
                          {workflow.workflows} workflows • {workflow.avgTime} avg
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-green-600">{workflow.success}%</p>
                        <p className="text-xs text-muted-foreground">Success</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Business Impact Categories</CardTitle>
                <CardDescription>
                  Value generation across operational areas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { category: 'Guest Experience', impact: '₹3.2L', improvement: '+15%' },
                    { category: 'Security & Compliance', impact: '₹2.8L', improvement: '+22%' },
                    { category: 'Operational Efficiency', impact: '₹1.9L', improvement: '+8%' },
                    { category: 'Revenue Optimization', impact: '₹4.1L', improvement: '+18%' }
                  ].map((impact) => (
                    <div key={impact.category} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{impact.category}</p>
                        <p className="text-sm text-muted-foreground">Monthly value</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{impact.impact}</p>
                        <p className="text-xs text-green-600">{impact.improvement}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Escalation Patterns</CardTitle>
                <CardDescription>
                  Human intervention requirements analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Full Automation</span>
                    <Badge variant="secondary">87%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Human Review</span>
                    <Badge variant="outline">8%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Manual Override</span>
                    <Badge variant="destructive">5%</Badge>
                  </div>
                  <div className="pt-2 border-t">
                    <p className="text-xs text-muted-foreground mb-2">Top escalation reasons:</p>
                    <div className="space-y-1 text-xs">
                      <div>• Regulatory compliance review (3%)</div>
                      <div>• Complex guest disputes (1.5%)</div>
                      <div>• System integration failures (0.5%)</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance">
          <div className="grid gap-4 md:grid-cols-1">
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics Over Time</CardTitle>
                <CardDescription>
                  Track key performance indicators across all agents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={analyticsData.conversationTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Bar 
                      yAxisId="left"
                      dataKey="conversations" 
                      fill="#8884d8" 
                      name="Conversations"
                    />
                    <Bar 
                      yAxisId="left"
                      dataKey="resolved" 
                      fill="#82ca9d" 
                      name="Resolved"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Top Performing Agent</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">Customer Support Agent</div>
                <p className="text-xs text-muted-foreground">
                  98.7% success rate
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Handling Time</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">2.1s</div>
                <p className="text-xs text-green-600">
                  -0.3s improvement
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Customer Satisfaction</CardTitle>
                <ThumbsUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">4.6/5</div>
                <p className="text-xs text-green-600">
                  +0.2 from last month
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="costs">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Monthly Cost Trends</CardTitle>
                <CardDescription>
                  Total platform costs over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={[
                    { month: 'Jan', cost: 2800 },
                    { month: 'Feb', cost: 3100 },
                    { month: 'Mar', cost: 2950 },
                    { month: 'Apr', cost: 3400 },
                    { month: 'May', cost: 3150 },
                    { month: 'Jun', cost: 3287 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`$${value}`, 'Cost']} />
                    <Line type="monotone" dataKey="cost" stroke="#ff8042" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cost by Agent Type</CardTitle>
                <CardDescription>
                  Breaking down costs by agent category
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    { type: 'Customer Service', cost: 1225 },
                    { type: 'Sales', cost: 945 },
                    { type: 'Support', cost: 617 },
                    { type: 'Analytics', cost: 500 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`$${value}`, 'Cost']} />
                    <Bar dataKey="cost" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Monthly Cost</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$3,287.70</div>
                <p className="text-xs text-green-600">
                  -8.2% from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Cost per Conversation</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$0.42</div>
                <p className="text-xs text-green-600">
                  -$0.05 improvement
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Projected Monthly</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$3,456.00</div>
                <p className="text-xs text-muted-foreground">
                  Based on current usage
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Cost Savings</CardTitle>
                <DollarSign className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$892.30</div>
                <p className="text-xs text-green-600">
                  Saved this month
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="usage">
          <div className="grid gap-4 md:grid-cols-1">
            <Card>
              <CardHeader>
                <CardTitle>Usage Patterns</CardTitle>
                <CardDescription>
                  Understanding when and how your agents are being used
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    { hour: '00:00', usage: 120 },
                    { hour: '04:00', usage: 80 },
                    { hour: '08:00', usage: 450 },
                    { hour: '12:00', usage: 680 },
                    { hour: '16:00', usage: 520 },
                    { hour: '20:00', usage: 350 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="usage" fill="#82ca9d" name="Conversations" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Top Integration Sources</CardTitle>
                <CardDescription>
                  Which integrations drive the most conversations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { name: 'Website Chat', conversations: 1247, percentage: 45 },
                    { name: 'Slack Integration', conversations: 892, percentage: 32 },
                    { name: 'API Endpoints', conversations: 456, percentage: 16 },
                    { name: 'Mobile App', conversations: 234, percentage: 8 }
                  ].map((source) => (
                    <div key={source.name} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{source.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {source.conversations.toLocaleString()} conversations
                        </p>
                      </div>
                      <Badge variant="outline">{source.percentage}%</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Response Time Distribution</CardTitle>
                <CardDescription>
                  How quickly are conversations being resolved
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { range: '< 1s', count: 456 },
                    { range: '1-2s', count: 789 },
                    { range: '2-5s', count: 234 },
                    { range: '5-10s', count: 123 },
                    { range: '> 10s', count: 45 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="range" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}