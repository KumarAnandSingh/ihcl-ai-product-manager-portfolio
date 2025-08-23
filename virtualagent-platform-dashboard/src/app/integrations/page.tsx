"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { 
  Plug, 
  Database, 
  MessageSquare, 
  Cloud, 
  Settings, 
  Play, 
  Pause,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock
} from "lucide-react"
import { mockIntegrations } from "@/lib/mock-data"
import { toast } from "sonner"

export default function IntegrationsPage() {
  const [isAddingIntegration, setIsAddingIntegration] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  
  const connectedIntegrations = mockIntegrations.filter(int => int.status === 'connected').length
  const totalDataVolume = mockIntegrations.reduce((sum, int) => sum + int.dataVolume, 0)
  const syncingIntegrations = mockIntegrations.filter(int => int.status === 'syncing').length
  const errorIntegrations = mockIntegrations.filter(int => int.status === 'error').length

  const handleAddIntegration = () => {
    setIsAddingIntegration(true)
    toast.loading("Opening integration marketplace...")
    setTimeout(() => {
      toast.success("Integration marketplace opened!")
      setIsAddingIntegration(false)
    }, 1500)
  }

  const handleSyncAll = () => {
    setIsSyncing(true)
    toast.loading("Syncing all integrations...")
    setTimeout(() => {
      toast.success("All integrations synced successfully!")
      setIsSyncing(false)
    }, 2000)
  }

  const handleSyncSingle = (name: string) => {
    toast.loading(`Syncing ${name}...`)
    setTimeout(() => {
      toast.success(`${name} synced successfully!`)
    }, 1500)
  }

  const handleConnect = (name: string) => {
    toast.loading(`Connecting to ${name}...`)
    setTimeout(() => {
      toast.success(`Successfully connected to ${name}!`)
    }, 2000)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'syncing': return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
      case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'CRM': return <Database className="h-5 w-5 text-blue-500" />
      case 'ERP': return <Database className="h-5 w-5 text-purple-500" />
      case 'Database': return <Database className="h-5 w-5 text-green-500" />
      case 'Messaging': return <MessageSquare className="h-5 w-5 text-orange-500" />
      case 'API': return <Cloud className="h-5 w-5 text-cyan-500" />
      default: return <Plug className="h-5 w-5 text-gray-500" />
    }
  }

  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Integration Hub</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={handleAddIntegration} disabled={isAddingIntegration}>
            {isAddingIntegration ? "Adding..." : "Add Integration"}
          </Button>
          <Button variant="outline" onClick={handleSyncAll} disabled={isSyncing}>
            {isSyncing ? "Syncing..." : "Sync All"}
          </Button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Connected</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{connectedIntegrations}</div>
            <p className="text-xs text-muted-foreground">
              Active integrations
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Volume</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(totalDataVolume / 1000).toFixed(0)}K</div>
            <p className="text-xs text-muted-foreground">
              Records synced
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Syncing</CardTitle>
            <RefreshCw className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{syncingIntegrations}</div>
            <p className="text-xs text-muted-foreground">
              Currently syncing
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Issues</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{errorIntegrations}</div>
            <p className="text-xs text-muted-foreground">
              Needs attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Active Integrations */}
      <Card>
        <CardHeader>
          <CardTitle>Active Integrations</CardTitle>
          <CardDescription>
            Manage your connected systems and data sources
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {mockIntegrations.map((integration) => (
              <Card key={integration.id} className="relative">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="flex items-center space-x-2">
                    {getTypeIcon(integration.type)}
                    <div>
                      <CardTitle className="text-base">{integration.name}</CardTitle>
                      <CardDescription>{integration.type}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(integration.status)}
                    <Button variant="ghost" size="icon">
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Badge 
                      variant={integration.status === 'connected' ? 'default' : 
                              integration.status === 'error' ? 'destructive' : 
                              integration.status === 'syncing' ? 'secondary' : 'outline'}
                    >
                      {integration.status}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {integration.dataVolume.toLocaleString()} records
                    </span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Data Volume</span>
                      <span className="font-medium">
                        {((integration.dataVolume / totalDataVolume) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={(integration.dataVolume / totalDataVolume) * 100} 
                      className="h-2" 
                    />
                  </div>

                  <div className="text-sm text-muted-foreground">
                    Last sync: {new Date(integration.lastSync).toLocaleDateString()}
                  </div>

                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline" className="flex-1" onClick={() => handleSyncSingle(integration.name)}>
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Sync
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => toast.success(`Opening ${integration.name} settings...`)}>
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Available Integrations */}
      <Card>
        <CardHeader>
          <CardTitle>Available Integrations</CardTitle>
          <CardDescription>
            Connect additional systems to expand your AI agent capabilities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Database className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Microsoft Dynamics</h3>
                  <p className="text-sm text-muted-foreground">
                    CRM and ERP integration
                  </p>
                </div>
                <Button className="w-full" onClick={() => handleConnect("Microsoft Dynamics")}>Connect</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <MessageSquare className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Microsoft Teams</h3>
                  <p className="text-sm text-muted-foreground">
                    Team messaging platform
                  </p>
                </div>
                <Button className="w-full" onClick={() => handleConnect("Microsoft Teams")}>Connect</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Database className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">HubSpot</h3>
                  <p className="text-sm text-muted-foreground">
                    Marketing and sales CRM
                  </p>
                </div>
                <Button className="w-full" onClick={() => handleConnect("HubSpot")}>Connect</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Cloud className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">AWS Services</h3>
                  <p className="text-sm text-muted-foreground">
                    Cloud infrastructure
                  </p>
                </div>
                <Button className="w-full" onClick={() => handleConnect("AWS Services")}>Connect</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Database className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Oracle Database</h3>
                  <p className="text-sm text-muted-foreground">
                    Enterprise database
                  </p>
                </div>
                <Button className="w-full" onClick={() => handleConnect("Oracle Database")}>Connect</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <MessageSquare className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Discord</h3>
                  <p className="text-sm text-muted-foreground">
                    Community platform
                  </p>
                </div>
                <Button className="w-full" onClick={() => handleConnect("Discord")}>Connect</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Database className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Zendesk</h3>
                  <p className="text-sm text-muted-foreground">
                    Customer support platform
                  </p>
                </div>
                <Button className="w-full" onClick={() => handleConnect("Zendesk")}>Connect</Button>
              </CardContent>
            </Card>

            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center space-y-4 p-6">
                <Cloud className="h-12 w-12 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="font-medium">Custom API</h3>
                  <p className="text-sm text-muted-foreground">
                    Connect any REST API
                  </p>
                </div>
                <Button className="w-full" onClick={() => handleConnect("Custom API")}>Connect</Button>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      {/* Integration Analytics */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Sync Performance</CardTitle>
            <CardDescription>
              Monitor data synchronization health
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Salesforce CRM</p>
                  <p className="text-xs text-muted-foreground">Last sync: 2 minutes ago</p>
                </div>
                <div className="text-right">
                  <Badge variant="default">100%</Badge>
                  <p className="text-xs text-muted-foreground">Success rate</p>
                </div>
              </div>
              <Progress value={100} className="h-2" />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">SAP ERP</p>
                  <p className="text-xs text-muted-foreground">Last sync: 5 minutes ago</p>
                </div>
                <div className="text-right">
                  <Badge variant="secondary">85%</Badge>
                  <p className="text-xs text-muted-foreground">Success rate</p>
                </div>
              </div>
              <Progress value={85} className="h-2" />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">PostgreSQL Database</p>
                  <p className="text-xs text-muted-foreground">Last sync: 1 minute ago</p>
                </div>
                <div className="text-right">
                  <Badge variant="default">98%</Badge>
                  <p className="text-xs text-muted-foreground">Success rate</p>
                </div>
              </div>
              <Progress value={98} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Data Flow</CardTitle>
            <CardDescription>
              Real-time data movement across integrations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm">Salesforce → VirtualAgent</span>
                </div>
                <span className="text-sm text-muted-foreground">125 records/min</span>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="h-3 w-3 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-sm">SAP ERP → VirtualAgent</span>
                </div>
                <span className="text-sm text-muted-foreground">89 records/min</span>
              </div>

              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="h-3 w-3 bg-purple-500 rounded-full animate-pulse"></div>
                  <span className="text-sm">PostgreSQL → VirtualAgent</span>
                </div>
                <span className="text-sm text-muted-foreground">234 records/min</span>
              </div>

              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="h-3 w-3 bg-orange-500 rounded-full animate-pulse"></div>
                  <span className="text-sm">Slack → VirtualAgent</span>
                </div>
                <span className="text-sm text-muted-foreground">56 messages/min</span>
              </div>

              <div className="pt-4 border-t">
                <div className="text-center">
                  <p className="text-2xl font-bold">504</p>
                  <p className="text-sm text-muted-foreground">Total records/min</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}