"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { 
  Settings, 
  Shield, 
  Users, 
  Key, 
  Bell, 
  Globe, 
  Database,
  Lock,
  Eye,
  Trash2,
  Plus,
  Edit,
  AlertTriangle
} from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("general")

  // Mock data
  const apiKeys = [
    { id: "1", name: "Production API", key: "pk_live_****1234", created: "2024-01-15", lastUsed: "2024-01-20", status: "active" },
    { id: "2", name: "Development API", key: "pk_test_****5678", created: "2024-01-10", lastUsed: "2024-01-19", status: "active" },
    { id: "3", name: "Analytics API", key: "pk_analytics_****9012", created: "2024-01-05", lastUsed: "Never", status: "inactive" }
  ]

  const userRoles = [
    { id: "1", name: "Admin", users: 3, permissions: ["All"], color: "bg-red-100 text-red-800" },
    { id: "2", name: "Manager", users: 12, permissions: ["Create", "Edit", "View"], color: "bg-blue-100 text-blue-800" },
    { id: "3", name: "Developer", users: 8, permissions: ["Deploy", "View", "Test"], color: "bg-green-100 text-green-800" },
    { id: "4", name: "Viewer", users: 25, permissions: ["View"], color: "bg-gray-100 text-gray-800" }
  ]

  const auditLogs = [
    { id: "1", user: "john.doe@company.com", action: "Created new agent", resource: "CustomerSupport-v2", timestamp: "2024-01-20 14:30", ip: "192.168.1.100" },
    { id: "2", user: "jane.smith@company.com", action: "Updated LLM settings", resource: "Global Configuration", timestamp: "2024-01-20 13:15", ip: "192.168.1.101" },
    { id: "3", user: "mike.wilson@company.com", action: "Deleted integration", resource: "Slack Integration", timestamp: "2024-01-20 12:45", ip: "192.168.1.102" },
    { id: "4", user: "sarah.jones@company.com", action: "Exported data", resource: "Analytics Dashboard", timestamp: "2024-01-20 11:20", ip: "192.168.1.103" }
  ]

  return (
    <div className="flex-1 space-y-8 p-8">
      <div className="flex items-center space-x-2">
        <Settings className="h-8 w-8" />
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Settings & Access Control</h2>
          <p className="text-muted-foreground">Manage platform settings, security, and user access</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="users">Users & Roles</TabsTrigger>
          <TabsTrigger value="api">API Keys</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <div className="grid gap-6">
            {/* Organization Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  Organization Settings
                </CardTitle>
                <CardDescription>Configure your organization details and preferences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Organization Name</label>
                    <Input defaultValue="IHCL AI Platform" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Industry</label>
                    <Select defaultValue="hospitality">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hospitality">Hospitality</SelectItem>
                        <SelectItem value="healthcare">Healthcare</SelectItem>
                        <SelectItem value="finance">Finance</SelectItem>
                        <SelectItem value="retail">Retail</SelectItem>
                        <SelectItem value="technology">Technology</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium">Default Language</label>
                  <Select defaultValue="en">
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="hi">Hindi</SelectItem>
                      <SelectItem value="ta">Tamil</SelectItem>
                      <SelectItem value="te">Telugu</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Time Zone</label>
                  <Select defaultValue="asia/kolkata">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="asia/kolkata">Asia/Kolkata (IST)</SelectItem>
                      <SelectItem value="utc">UTC</SelectItem>
                      <SelectItem value="america/new_york">America/New_York</SelectItem>
                      <SelectItem value="europe/london">Europe/London</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={() => toast.success("Settings saved successfully!")}>Save Changes</Button>
              </CardContent>
            </Card>

            {/* Platform Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Platform Configuration
                </CardTitle>
                <CardDescription>Configure platform-wide settings and defaults</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Auto-scaling</h4>
                    <p className="text-sm text-muted-foreground">Automatically scale resources based on demand</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Advanced Analytics</h4>
                    <p className="text-sm text-muted-foreground">Enable detailed conversation analytics</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Cost Optimization</h4>
                    <p className="text-sm text-muted-foreground">Automatic LLM routing for cost efficiency</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div>
                  <label className="text-sm font-medium">Default Model</label>
                  <Select defaultValue="gpt-4">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt-4">GPT-4</SelectItem>
                      <SelectItem value="claude-3">Claude 3 Sonnet</SelectItem>
                      <SelectItem value="gemini-pro">Gemini Pro</SelectItem>
                      <SelectItem value="llama-2">Llama 2 70B</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <div className="grid gap-6">
            {/* Security Policies */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Security Policies
                </CardTitle>
                <CardDescription>Configure security settings and access policies</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Two-Factor Authentication</h4>
                    <p className="text-sm text-muted-foreground">Require 2FA for all users</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">SSO Integration</h4>
                    <p className="text-sm text-muted-foreground">Enable single sign-on via SAML/OIDC</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">IP Whitelisting</h4>
                    <p className="text-sm text-muted-foreground">Restrict access to specific IP ranges</p>
                  </div>
                  <Switch />
                </div>
                <div>
                  <label className="text-sm font-medium">Session Timeout (minutes)</label>
                  <Input type="number" defaultValue="480" className="w-32" />
                </div>
                <div>
                  <label className="text-sm font-medium">Password Policy</label>
                  <Select defaultValue="strong">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="basic">Basic (8 characters)</SelectItem>
                      <SelectItem value="strong">Strong (12 characters, mixed case, symbols)</SelectItem>
                      <SelectItem value="enterprise">Enterprise (16 characters, all requirements)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Compliance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lock className="h-5 w-5" />
                  Compliance & Privacy
                </CardTitle>
                <CardDescription>Data protection and regulatory compliance settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">GDPR Compliance</h4>
                    <p className="text-sm text-muted-foreground">Enable GDPR data protection features</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">HIPAA Compliance</h4>
                    <p className="text-sm text-muted-foreground">Enable healthcare data protection</p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">PII Detection</h4>
                    <p className="text-sm text-muted-foreground">Automatically detect and protect personal information</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div>
                  <label className="text-sm font-medium">Data Retention Period (days)</label>
                  <Input type="number" defaultValue="365" className="w-32" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="users" className="space-y-6">
          <div className="grid gap-6">
            {/* User Roles */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  User Roles & Permissions
                </CardTitle>
                <CardDescription>Manage user roles and access permissions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button className="mb-4">
                    <Plus className="h-4 w-4 mr-2" />
                    Create New Role
                  </Button>
                  <div className="space-y-3">
                    {userRoles.map((role) => (
                      <div key={role.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-4">
                          <Badge className={role.color}>{role.name}</Badge>
                          <div>
                            <p className="font-medium">{role.users} users</p>
                            <p className="text-sm text-muted-foreground">
                              Permissions: {role.permissions.join(", ")}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Active Users */}
            <Card>
              <CardHeader>
                <CardTitle>Active Users</CardTitle>
                <CardDescription>Currently active users in the system</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">john.doe@ihcl.com</p>
                      <p className="text-sm text-muted-foreground">Admin • Last active: 2 minutes ago</p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Online</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">jane.smith@ihcl.com</p>
                      <p className="text-sm text-muted-foreground">Manager • Last active: 15 minutes ago</p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Online</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">mike.wilson@ihcl.com</p>
                      <p className="text-sm text-muted-foreground">Developer • Last active: 1 hour ago</p>
                    </div>
                    <Badge className="bg-yellow-100 text-yellow-800">Away</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="api" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                API Keys Management
              </CardTitle>
              <CardDescription>Create and manage API keys for external integrations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Generate New API Key
                </Button>
                <div className="space-y-3">
                  {apiKeys.map((apiKey) => (
                    <div key={apiKey.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="space-y-1">
                        <p className="font-medium">{apiKey.name}</p>
                        <p className="text-sm text-muted-foreground font-mono">{apiKey.key}</p>
                        <div className="flex gap-4 text-xs text-muted-foreground">
                          <span>Created: {apiKey.created}</span>
                          <span>Last used: {apiKey.lastUsed}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={apiKey.status === "active" ? "default" : "secondary"}>
                          {apiKey.status}
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Settings
              </CardTitle>
              <CardDescription>Configure alerts and notification preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">System Alerts</h4>
                    <p className="text-sm text-muted-foreground">Critical system events and downtime</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Performance Alerts</h4>
                    <p className="text-sm text-muted-foreground">Agent performance and SLA breaches</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Security Alerts</h4>
                    <p className="text-sm text-muted-foreground">Unauthorized access attempts and security incidents</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Cost Alerts</h4>
                    <p className="text-sm text-muted-foreground">Budget overruns and cost anomalies</p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="font-medium mb-4">Alert Channels</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Switch defaultChecked />
                    <div className="flex-1">
                      <p className="font-medium">Email Notifications</p>
                      <Input type="email" placeholder="admin@ihcl.com" className="mt-1" />
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Switch defaultChecked />
                    <div className="flex-1">
                      <p className="font-medium">Slack Integration</p>
                      <Input placeholder="#alerts" className="mt-1" />
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Switch />
                    <div className="flex-1">
                      <p className="font-medium">PagerDuty</p>
                      <Input placeholder="Integration key" className="mt-1" />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Audit Logs
              </CardTitle>
              <CardDescription>Security and compliance audit trail</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <Select defaultValue="all">
                    <SelectTrigger className="w-48">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Actions</SelectItem>
                      <SelectItem value="create">Create</SelectItem>
                      <SelectItem value="update">Update</SelectItem>
                      <SelectItem value="delete">Delete</SelectItem>
                      <SelectItem value="export">Export</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input placeholder="Search logs..." className="flex-1" />
                  <Button variant="outline">Export Logs</Button>
                </div>

                <div className="space-y-2">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{log.user}</p>
                          <Badge variant="outline">{log.action}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{log.resource}</p>
                        <div className="flex gap-4 text-xs text-muted-foreground">
                          <span>{log.timestamp}</span>
                          <span>IP: {log.ip}</span>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}