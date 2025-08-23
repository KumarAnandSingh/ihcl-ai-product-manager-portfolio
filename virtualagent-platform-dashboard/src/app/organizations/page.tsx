"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Building2, 
  Users, 
  Bot, 
  DollarSign, 
  BarChart3,
  Settings,
  Crown,
  Zap,
  Shield
} from "lucide-react"
import { mockOrganizations } from "@/lib/mock-data"
import { toast } from "sonner"

export default function OrganizationsPage() {
  const [isAddingOrg, setIsAddingOrg] = useState(false)
  const [isBulkActionActive, setIsBulkActionActive] = useState(false)
  
  const totalOrgs = mockOrganizations.length
  const totalRevenue = mockOrganizations.reduce((sum, org) => sum + org.cost, 0)
  const totalUsers = mockOrganizations.reduce((sum, org) => sum + org.users, 0)
  const totalAgents = mockOrganizations.reduce((sum, org) => sum + org.agents, 0)

  const handleAddOrganization = () => {
    setIsAddingOrg(true)
    toast.loading("Opening organization creation wizard...")
    setTimeout(() => {
      toast.success("Organization wizard opened!")
      setIsAddingOrg(false)
    }, 1500)
  }

  const handleBulkActions = () => {
    setIsBulkActionActive(true)
    toast.loading("Preparing bulk actions...")
    setTimeout(() => {
      toast.success("Bulk actions panel ready!")
      setIsBulkActionActive(false)
    }, 1500)
  }

  const handleViewDetails = (orgName: string) => {
    toast.success(`Opening ${orgName} details...`)
  }

  const handleManageUsers = (orgName: string) => {
    toast.success(`Opening user management for ${orgName}...`)
  }

  const handleBilling = (orgName: string) => {
    toast.success(`Opening billing dashboard for ${orgName}...`)
  }

  const getPlanIcon = (plan: string) => {
    switch (plan) {
      case 'Enterprise': return <Crown className="h-4 w-4 text-yellow-500" />
      case 'Professional': return <Zap className="h-4 w-4 text-blue-500" />
      case 'Basic': return <Shield className="h-4 w-4 text-green-500" />
      default: return <Building2 className="h-4 w-4 text-gray-500" />
    }
  }

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'Enterprise': return 'bg-gradient-to-r from-yellow-100 to-yellow-50 dark:from-yellow-950 dark:to-yellow-900 border-yellow-200 dark:border-yellow-800'
      case 'Professional': return 'bg-gradient-to-r from-blue-100 to-blue-50 dark:from-blue-950 dark:to-blue-900 border-blue-200 dark:border-blue-800'
      case 'Basic': return 'bg-gradient-to-r from-green-100 to-green-50 dark:from-green-950 dark:to-green-900 border-green-200 dark:border-green-800'
      default: return ''
    }
  }

  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Organization Management</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={handleAddOrganization} disabled={isAddingOrg}>
            {isAddingOrg ? "Adding..." : "Add Organization"}
          </Button>
          <Button variant="outline" onClick={handleBulkActions} disabled={isBulkActionActive}>
            {isBulkActionActive ? "Loading..." : "Bulk Actions"}
          </Button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Organizations</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalOrgs}</div>
            <p className="text-xs text-muted-foreground">
              Active tenants
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalRevenue.toFixed(2)}</div>
            <p className="text-xs text-green-600">
              +18.2% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              Across all organizations
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalAgents}</div>
            <p className="text-xs text-muted-foreground">
              Deployed across organizations
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Organization Overview</TabsTrigger>
          <TabsTrigger value="billing">Billing & Plans</TabsTrigger>
          <TabsTrigger value="usage">Usage Analytics</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid gap-6">
            {mockOrganizations.map((org) => (
              <Card key={org.id} className={`relative ${getPlanColor(org.plan)}`}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Building2 className="h-8 w-8 text-primary" />
                      <div>
                        <CardTitle className="text-xl">{org.name}</CardTitle>
                        <CardDescription className="flex items-center space-x-2">
                          {getPlanIcon(org.plan)}
                          <span>{org.plan} Plan</span>
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="font-medium">
                        ${org.cost}/month
                      </Badge>
                      <Button variant="ghost" size="icon">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div className="flex items-center space-x-3">
                      <Bot className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium">Agents</p>
                        <p className="text-2xl font-bold">{org.agents}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <Users className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="text-sm font-medium">Users</p>
                        <p className="text-2xl font-bold">{org.users}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <BarChart3 className="h-5 w-5 text-purple-600" />
                      <div>
                        <p className="text-sm font-medium">API Calls</p>
                        <p className="text-2xl font-bold">{(org.apiCalls / 1000).toFixed(0)}K</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <DollarSign className="h-5 w-5 text-orange-600" />
                      <div>
                        <p className="text-sm font-medium">Monthly Cost</p>
                        <p className="text-2xl font-bold">${org.cost}</p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">API Usage</span>
                      <span className="text-sm text-muted-foreground">
                        {org.apiCalls.toLocaleString()} / {org.plan === 'Enterprise' ? '∞' : org.plan === 'Professional' ? '100K' : '10K'}
                      </span>
                    </div>
                    <Progress 
                      value={org.plan === 'Enterprise' ? 35 : (org.apiCalls / (org.plan === 'Professional' ? 100000 : 10000)) * 100} 
                      className="h-2" 
                    />
                  </div>

                  <div className="mt-4 flex space-x-2">
                    <Button size="sm" variant="outline" className="flex-1" onClick={() => handleViewDetails(org.name)}>
                      View Details
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1" onClick={() => handleManageUsers(org.name)}>
                      Manage Users
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1" onClick={() => handleBilling(org.name)}>
                      Billing
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="billing">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Revenue Analytics</CardTitle>
                <CardDescription>
                  Track revenue and billing across all organizations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="text-center p-6 border rounded-lg">
                    <Crown className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
                    <h3 className="font-medium">Enterprise</h3>
                    <p className="text-2xl font-bold mt-2">
                      ${mockOrganizations.filter(org => org.plan === 'Enterprise').reduce((sum, org) => sum + org.cost, 0).toFixed(2)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {mockOrganizations.filter(org => org.plan === 'Enterprise').length} organizations
                    </p>
                  </div>
                  
                  <div className="text-center p-6 border rounded-lg">
                    <Zap className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                    <h3 className="font-medium">Professional</h3>
                    <p className="text-2xl font-bold mt-2">
                      ${mockOrganizations.filter(org => org.plan === 'Professional').reduce((sum, org) => sum + org.cost, 0).toFixed(2)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {mockOrganizations.filter(org => org.plan === 'Professional').length} organizations
                    </p>
                  </div>

                  <div className="text-center p-6 border rounded-lg">
                    <Shield className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    <h3 className="font-medium">Basic</h3>
                    <p className="text-2xl font-bold mt-2">
                      ${mockOrganizations.filter(org => org.plan === 'Basic').reduce((sum, org) => sum + org.cost, 0).toFixed(2)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {mockOrganizations.filter(org => org.plan === 'Basic').length} organizations
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Billing Overview</CardTitle>
                <CardDescription>
                  Recent billing activities and upcoming charges
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Building2 className="h-5 w-5" />
                      <div>
                        <p className="font-medium">Acme Corporation</p>
                        <p className="text-sm text-muted-foreground">Enterprise Plan • Next billing: Jan 15, 2024</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">$2,450.00</p>
                      <Badge variant="default">Paid</Badge>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Building2 className="h-5 w-5" />
                      <div>
                        <p className="font-medium">TechStart Inc</p>
                        <p className="text-sm text-muted-foreground">Professional Plan • Next billing: Jan 20, 2024</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">$890.00</p>
                      <Badge variant="secondary">Pending</Badge>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Building2 className="h-5 w-5" />
                      <div>
                        <p className="font-medium">Global Solutions Ltd</p>
                        <p className="text-sm text-muted-foreground">Enterprise Plan • Next billing: Jan 12, 2024</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">$5,670.00</p>
                      <Badge variant="default">Paid</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="usage">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Usage Patterns</CardTitle>
                <CardDescription>
                  Understanding how organizations use the platform
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {mockOrganizations.map((org) => (
                    <div key={org.id} className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">{org.name}</h4>
                        <Badge variant="outline">{org.plan}</Badge>
                      </div>
                      
                      <div className="grid gap-3 md:grid-cols-3">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>API Usage</span>
                            <span>{org.apiCalls.toLocaleString()}</span>
                          </div>
                          <Progress 
                            value={org.plan === 'Enterprise' ? 35 : (org.apiCalls / (org.plan === 'Professional' ? 100000 : 10000)) * 100} 
                            className="h-2" 
                          />
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Active Agents</span>
                            <span>{org.agents}</span>
                          </div>
                          <Progress 
                            value={(org.agents / (org.plan === 'Enterprise' ? 50 : org.plan === 'Professional' ? 20 : 5)) * 100} 
                            className="h-2" 
                          />
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Users</span>
                            <span>{org.users}</span>
                          </div>
                          <Progress 
                            value={(org.users / (org.plan === 'Enterprise' ? 200 : org.plan === 'Professional' ? 50 : 10)) * 100} 
                            className="h-2" 
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="settings">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Global Settings</CardTitle>
                <CardDescription>
                  Platform-wide configuration options
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Auto-scaling</p>
                    <p className="text-sm text-muted-foreground">Automatically scale resources based on usage</p>
                  </div>
                  <Badge variant="default">Enabled</Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Multi-region deployment</p>
                    <p className="text-sm text-muted-foreground">Deploy agents across multiple regions</p>
                  </div>
                  <Badge variant="default">Enabled</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Usage monitoring</p>
                    <p className="text-sm text-muted-foreground">Track and alert on usage patterns</p>
                  </div>
                  <Badge variant="default">Enabled</Badge>
                </div>

                <Button className="w-full" onClick={() => toast.success("Global settings updated!")}>
                  Update Settings
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compliance & Security</CardTitle>
                <CardDescription>
                  Organization-level security configurations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Data encryption</p>
                    <p className="text-sm text-muted-foreground">End-to-end encryption for all data</p>
                  </div>
                  <Badge variant="default">Enabled</Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Audit logging</p>
                    <p className="text-sm text-muted-foreground">Comprehensive activity logging</p>
                  </div>
                  <Badge variant="default">Enabled</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">GDPR compliance</p>
                    <p className="text-sm text-muted-foreground">Automated data protection compliance</p>
                  </div>
                  <Badge variant="default">Enabled</Badge>
                </div>

                <Button className="w-full" onClick={() => toast.success("Security settings updated!")}>
                  Security Settings
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}