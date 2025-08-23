"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Brain, 
  Zap, 
  DollarSign, 
  Clock, 
  TrendingUp, 
  Settings,
  BarChart3,
  Cpu
} from "lucide-react"
import { 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  ResponsiveContainer, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts'
import { mockLLMModels } from "@/lib/mock-data"
import { toast } from "sonner"

export default function LLMOrchestrationPage() {
  const [isAddingModel, setIsAddingModel] = useState(false)
  const [isConfiguringRouting, setIsConfiguringRouting] = useState(false)
  
  const totalTokensUsed = mockLLMModels.reduce((sum, model) => sum + model.tokensUsed, 0)
  const totalCost = mockLLMModels.reduce((sum, model) => sum + model.cost, 0)
  const avgLatency = mockLLMModels.reduce((sum, model) => sum + model.avgLatency, 0) / mockLLMModels.length
  const avgSuccessRate = mockLLMModels.reduce((sum, model) => sum + model.successRate, 0) / mockLLMModels.length

  const handleAddModel = () => {
    setIsAddingModel(true)
    toast.loading("Opening model configuration...")
    setTimeout(() => {
      toast.success("Model configuration modal opened!")
      setIsAddingModel(false)
    }, 1500)
  }

  const handleConfigureRouting = () => {
    setIsConfiguringRouting(true)
    toast.loading("Loading routing configuration...")
    setTimeout(() => {
      toast.success("Routing configuration ready!")
      setIsConfiguringRouting(false)
    }, 1500)
  }

  const costComparison = [
    { model: 'GPT-4', costPerToken: 0.0005, throughput: 2000, reliability: 99.1 },
    { model: 'Claude 3', costPerToken: 0.0005, throughput: 1800, reliability: 98.8 },
    { model: 'Gemini Pro', costPerToken: 0.0005, throughput: 2200, reliability: 97.9 },
    { model: 'Llama 2', costPerToken: 0.0005, throughput: 1200, reliability: 96.5 }
  ]

  const usageTrends = [
    { month: 'Jan', 'GPT-4': 2100000, 'Claude 3': 1600000, 'Gemini Pro': 900000, 'Llama 2': 400000 },
    { month: 'Feb', 'GPT-4': 2300000, 'Claude 3': 1750000, 'Gemini Pro': 1050000, 'Llama 2': 450000 },
    { month: 'Mar', 'GPT-4': 2450000, 'Claude 3': 1890000, 'Gemini Pro': 1234000, 'Llama 2': 567000 }
  ]

  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">LLM Orchestration</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={handleAddModel} disabled={isAddingModel}>
            {isAddingModel ? "Adding..." : "Add Model"}
          </Button>
          <Button variant="outline" onClick={handleConfigureRouting} disabled={isConfiguringRouting}>
            {isConfiguringRouting ? "Configuring..." : "Configure Routing"}
          </Button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(totalTokensUsed / 1000000).toFixed(1)}M</div>
            <p className="text-xs text-muted-foreground">
              +12.5% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalCost.toFixed(2)}</div>
            <p className="text-xs text-green-600">
              -8.2% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgLatency.toFixed(1)}s</div>
            <p className="text-xs text-green-600">
              -0.2s improvement
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgSuccessRate.toFixed(1)}%</div>
            <p className="text-xs text-green-600">
              +1.3% from last month
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="models" className="space-y-4">
        <TabsList>
          <TabsTrigger value="models">Model Management</TabsTrigger>
          <TabsTrigger value="routing">Smart Routing</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="cost-optimization">Cost Optimization</TabsTrigger>
        </TabsList>

        <TabsContent value="models">
          <div className="grid gap-6">
            {mockLLMModels.map((model) => (
              <Card key={model.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Brain className="h-8 w-8 text-primary" />
                      <div>
                        <CardTitle className="text-xl">{model.name}</CardTitle>
                        <CardDescription className="capitalize">
                          {model.provider} • {model.status}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant={model.status === 'active' ? 'default' : 'secondary'}
                      >
                        {model.status}
                      </Badge>
                      <Button variant="ghost" size="icon">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <BarChart3 className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Tokens Used</span>
                      </div>
                      <p className="text-2xl font-bold">
                        {(model.tokensUsed / 1000000).toFixed(1)}M
                      </p>
                      <Progress 
                        value={(model.tokensUsed / totalTokensUsed) * 100} 
                        className="h-2" 
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Cost</span>
                      </div>
                      <p className="text-2xl font-bold">${model.cost.toFixed(2)}</p>
                      <p className="text-sm text-muted-foreground">
                        {((model.cost / totalCost) * 100).toFixed(1)}% of total
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Avg Latency</span>
                      </div>
                      <p className="text-2xl font-bold">{model.avgLatency}s</p>
                      <p className="text-sm text-muted-foreground">
                        Response time
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Success Rate</span>
                      </div>
                      <p className="text-2xl font-bold">{model.successRate}%</p>
                      <Progress value={model.successRate} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="routing">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Smart Routing Rules</CardTitle>
                <CardDescription>
                  Automatically route requests to optimal models
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">Cost-Optimized Routing</p>
                    <p className="text-sm text-muted-foreground">Route to cheapest available model</p>
                  </div>
                  <Badge variant="default">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">Latency-Optimized Routing</p>
                    <p className="text-sm text-muted-foreground">Route to fastest available model</p>
                  </div>
                  <Badge variant="secondary">Inactive</Badge>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">Load Balancing</p>
                    <p className="text-sm text-muted-foreground">Distribute load evenly across models</p>
                  </div>
                  <Badge variant="default">Active</Badge>
                </div>
                <Button className="w-full" onClick={handleConfigureRouting} disabled={isConfiguringRouting}>
                  {isConfiguringRouting ? "Configuring..." : "Configure Routing Rules"}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Fallback Configuration</CardTitle>
                <CardDescription>
                  Define fallback models for high availability
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Primary Model</label>
                  <div className="p-2 border rounded bg-muted">GPT-4 Turbo</div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Secondary Model</label>
                  <div className="p-2 border rounded bg-muted">Claude 3 Sonnet</div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tertiary Model</label>
                  <div className="p-2 border rounded bg-muted">Gemini Pro</div>
                </div>
                <Button className="w-full" variant="outline" onClick={() => toast.success("Fallback configuration updated!")}>
                  Update Fallbacks
                </Button>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Request Distribution</CardTitle>
              <CardDescription>
                How requests are distributed across different models
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={usageTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${(value / 1000000).toFixed(1)}M`, 'Tokens']} />
                  <Legend />
                  <Bar dataKey="GPT-4" fill="#8884d8" name="GPT-4" />
                  <Bar dataKey="Claude 3" fill="#82ca9d" name="Claude 3" />
                  <Bar dataKey="Gemini Pro" fill="#ffc658" name="Gemini Pro" />
                  <Bar dataKey="Llama 2" fill="#ff7c7c" name="Llama 2" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Latency Comparison</CardTitle>
                <CardDescription>
                  Average response times across models
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={mockLLMModels.map(model => ({
                    name: model.name,
                    latency: model.avgLatency
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value}s`, 'Latency']} />
                    <Bar dataKey="latency" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Success Rate Trends</CardTitle>
                <CardDescription>
                  Model reliability over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={[
                    { month: 'Jan', 'GPT-4': 98.9, 'Claude 3': 98.5, 'Gemini Pro': 97.2, 'Llama 2': 95.8 },
                    { month: 'Feb', 'GPT-4': 99.0, 'Claude 3': 98.7, 'Gemini Pro': 97.6, 'Llama 2': 96.2 },
                    { month: 'Mar', 'GPT-4': 99.1, 'Claude 3': 98.8, 'Gemini Pro': 97.9, 'Llama 2': 96.5 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis domain={[95, 100]} />
                    <Tooltip formatter={(value) => [`${value}%`, 'Success Rate']} />
                    <Legend />
                    <Line type="monotone" dataKey="GPT-4" stroke="#8884d8" />
                    <Line type="monotone" dataKey="Claude 3" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="Gemini Pro" stroke="#ffc658" />
                    <Line type="monotone" dataKey="Llama 2" stroke="#ff7c7c" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Best Latency</CardTitle>
                <Zap className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">Gemini Pro</div>
                <p className="text-xs text-muted-foreground">
                  1.1s average response
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Highest Reliability</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">GPT-4 Turbo</div>
                <p className="text-xs text-muted-foreground">
                  99.1% success rate
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Most Used</CardTitle>
                <Cpu className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">GPT-4 Turbo</div>
                <p className="text-xs text-muted-foreground">
                  2.45M tokens this month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Best Value</CardTitle>
                <DollarSign className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">Claude 3</div>
                <p className="text-xs text-muted-foreground">
                  $0.50 per 1K tokens
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="cost-optimization">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Cost Optimization Recommendations</CardTitle>
                <CardDescription>
                  AI-powered suggestions to reduce your LLM costs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-4 p-4 border rounded-lg bg-green-50 dark:bg-green-950">
                  <DollarSign className="h-5 w-5 text-green-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-green-800 dark:text-green-200">
                      Switch to Claude 3 for simple queries
                    </p>
                    <p className="text-sm text-green-600 dark:text-green-300">
                      Estimated savings: $234/month • 23% of simple queries could use Claude 3 instead of GPT-4
                    </p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => toast.success("Cost optimization rule applied!")}>
                    Apply
                  </Button>
                </div>

                <div className="flex items-start space-x-4 p-4 border rounded-lg bg-blue-50 dark:bg-blue-950">
                  <Cpu className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-blue-800 dark:text-blue-200">
                      Implement response caching
                    </p>
                    <p className="text-sm text-blue-600 dark:text-blue-300">
                      Estimated savings: $156/month • 18% of requests are similar enough to cache
                    </p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => toast.success("Response caching configured!")}>
                    Configure
                  </Button>
                </div>

                <div className="flex items-start space-x-4 p-4 border rounded-lg bg-orange-50 dark:bg-orange-950">
                  <Clock className="h-5 w-5 text-orange-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-orange-800 dark:text-orange-200">
                      Optimize prompt length
                    </p>
                    <p className="text-sm text-orange-600 dark:text-orange-300">
                      Estimated savings: $89/month • Average prompt could be 15% shorter without losing context
                    </p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => toast.success("Prompt optimization review started!")}>
                    Review
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Monthly Cost Breakdown</CardTitle>
                <CardDescription>
                  Detailed cost analysis by model and usage type
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={costComparison.map(model => ({
                    name: model.model,
                    cost: mockLLMModels.find(m => m.name.includes(model.model))?.cost || 0,
                    tokens: mockLLMModels.find(m => m.name.includes(model.model))?.tokensUsed || 0
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Bar yAxisId="left" dataKey="cost" fill="#8884d8" name="Cost ($)" />
                    <Line yAxisId="right" type="monotone" dataKey="tokens" stroke="#82ca9d" name="Tokens (M)" />
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