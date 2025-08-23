"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Shield, 
  Users, 
  Lock, 
  Key, 
  Plus, 
  Edit, 
  Trash2, 
  Eye,
  UserCheck,
  UserX,
  Settings,
  AlertTriangle,
  CheckCircle,
  XCircle
} from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

export default function AccessControlPage() {
  const [selectedTab, setSelectedTab] = useState("users")
  const [isAddingUser, setIsAddingUser] = useState(false)
  const [isBulkActionActive, setIsBulkActionActive] = useState(false)

  const handleAddUser = () => {
    setIsAddingUser(true)
    toast.loading("Opening user creation form...")
    setTimeout(() => {
      toast.success("User creation form opened!")
      setIsAddingUser(false)
    }, 1500)
  }

  const handleBulkActions = () => {
    setIsBulkActionActive(true)
    toast.loading("Preparing bulk user actions...")
    setTimeout(() => {
      toast.success("Bulk actions panel ready!")
      setIsBulkActionActive(false)
    }, 1500)
  }

  // Mock data for users
  const users = [
    { 
      id: "1", 
      name: "John Doe", 
      email: "john.doe@ihcl.com", 
      role: "Admin", 
      status: "active", 
      lastLogin: "2024-01-20 14:30",
      permissions: ["All Access"],
      department: "IT Operations"
    },
    { 
      id: "2", 
      name: "Jane Smith", 
      email: "jane.smith@ihcl.com", 
      role: "Hotel Manager", 
      status: "active", 
      lastLogin: "2024-01-20 13:45",
      permissions: ["Hotel Management", "Guest Services", "Analytics"],
      department: "Operations"
    },
    { 
      id: "3", 
      name: "Mike Wilson", 
      email: "mike.wilson@ihcl.com", 
      role: "Developer", 
      status: "active", 
      lastLogin: "2024-01-20 12:15",
      permissions: ["Agent Development", "Deployment", "Testing"],
      department: "Technology"
    },
    { 
      id: "4", 
      name: "Sarah Jones", 
      email: "sarah.jones@ihcl.com", 
      role: "Guest Service Agent", 
      status: "inactive", 
      lastLogin: "2024-01-18 16:20",
      permissions: ["Guest Interaction", "Basic Analytics"],
      department: "Guest Services"
    }
  ]

  // Mock data for roles
  const roles = [
    {
      id: "1",
      name: "Super Admin",
      description: "Full platform access with all permissions",
      users: 2,
      permissions: [
        "User Management", "System Configuration", "Security Settings", 
        "Audit Logs", "API Management", "Billing", "All Hotel Operations"
      ],
      color: "bg-red-100 text-red-800"
    },
    {
      id: "2", 
      name: "Hotel Manager",
      description: "Manage specific hotel properties and operations",
      users: 15,
      permissions: [
        "Hotel Operations", "Guest Services", "Staff Management",
        "Analytics Dashboard", "Agent Configuration", "Integrations"
      ],
      color: "bg-blue-100 text-blue-800"
    },
    {
      id: "3",
      name: "Developer", 
      description: "Technical development and deployment access",
      users: 8,
      permissions: [
        "Agent Development", "Code Deployment", "Testing Environment",
        "API Access", "Performance Monitoring", "Debug Logs"
      ],
      color: "bg-green-100 text-green-800"
    },
    {
      id: "4",
      name: "Guest Service Agent",
      description: "Front-line staff with guest interaction permissions",
      users: 45,
      permissions: [
        "Guest Interaction", "Basic Dashboard", "Incident Reporting",
        "Knowledge Base", "Chat History", "Basic Analytics"
      ],
      color: "bg-purple-100 text-purple-800"
    },
    {
      id: "5",
      name: "Analytics Viewer",
      description: "Read-only access to analytics and reports", 
      users: 12,
      permissions: [
        "View Dashboards", "Generate Reports", "Export Data",
        "Performance Metrics", "Cost Analytics"
      ],
      color: "bg-gray-100 text-gray-800"
    }
  ]

  // Mock data for permissions
  const permissionCategories = [
    {
      category: "User Management",
      permissions: [
        { name: "Create Users", description: "Add new users to the platform" },
        { name: "Edit Users", description: "Modify user profiles and settings" },
        { name: "Delete Users", description: "Remove users from the platform" },
        { name: "Assign Roles", description: "Assign and modify user roles" }
      ]
    },
    {
      category: "Agent Management", 
      permissions: [
        { name: "Create Agents", description: "Build and configure new AI agents" },
        { name: "Deploy Agents", description: "Deploy agents to production" },
        { name: "Edit Agents", description: "Modify agent configurations" },
        { name: "Delete Agents", description: "Remove agents from the platform" }
      ]
    },
    {
      category: "Hotel Operations",
      permissions: [
        { name: "Property Management", description: "Manage hotel property settings" },
        { name: "Guest Services", description: "Handle guest interactions and services" },
        { name: "Staff Coordination", description: "Coordinate with hotel staff" },
        { name: "Revenue Management", description: "Access revenue and pricing data" }
      ]
    },
    {
      category: "Analytics & Reporting",
      permissions: [
        { name: "View Dashboards", description: "Access performance dashboards" },
        { name: "Generate Reports", description: "Create custom reports" },
        { name: "Export Data", description: "Export data for external analysis" },
        { name: "Cost Analytics", description: "View cost and usage analytics" }
      ]
    }
  ]

  const getStatusBadge = (status: string) => {
    return status === "active" ? (
      <Badge className="bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3 mr-1" />
        Active
      </Badge>
    ) : (
      <Badge className="bg-gray-100 text-gray-800">
        <XCircle className="h-3 w-3 mr-1" />
        Inactive
      </Badge>
    )
  }

  return (
    <div className="flex-1 space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Shield className="h-8 w-8" />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Access Control</h2>
            <p className="text-muted-foreground">Manage users, roles, and permissions across your organization</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleAddUser} disabled={isAddingUser}>
            <Plus className="h-4 w-4 mr-2" />
            {isAddingUser ? "Adding..." : "Add User"}
          </Button>
          <Button variant="outline" onClick={handleBulkActions} disabled={isBulkActionActive}>
            <Settings className="h-4 w-4 mr-2" />
            {isBulkActionActive ? "Loading..." : "Bulk Actions"}
          </Button>
        </div>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
          <TabsTrigger value="security">Security Policies</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                User Management
              </CardTitle>
              <CardDescription>Manage user accounts, roles, and access permissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-4 items-center">
                  <Input placeholder="Search users..." className="flex-1" />
                  <Select defaultValue="all">
                    <SelectTrigger className="w-48">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Users</SelectItem>
                      <SelectItem value="active">Active Only</SelectItem>
                      <SelectItem value="inactive">Inactive Only</SelectItem>
                      <SelectItem value="admin">Admins</SelectItem>
                      <SelectItem value="manager">Managers</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline">Filter</Button>
                </div>

                <div className="space-y-3">
                  {users.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium">
                          {user.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{user.name}</p>
                            {getStatusBadge(user.status)}
                          </div>
                          <p className="text-sm text-muted-foreground">{user.email}</p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span>Role: {user.role}</span>
                            <span>Dept: {user.department}</span>
                            <span>Last Login: {user.lastLogin}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{user.role}</Badge>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
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

          <Card>
            <CardHeader>
              <CardTitle>Active Sessions</CardTitle>
              <CardDescription>Currently active user sessions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <div>
                      <p className="font-medium">john.doe@ihcl.com</p>
                      <p className="text-sm text-muted-foreground">Admin • Session started 2 hours ago</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">Terminate</Button>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <div>
                      <p className="font-medium">jane.smith@ihcl.com</p>
                      <p className="text-sm text-muted-foreground">Hotel Manager • Session started 45 minutes ago</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">Terminate</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roles" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCheck className="h-5 w-5" />
                Role Management
              </CardTitle>
              <CardDescription>Define and manage user roles with specific permission sets</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create New Role
                </Button>
                
                <div className="grid gap-4">
                  {roles.map((role) => (
                    <Card key={role.id} className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center gap-3">
                            <Badge className={role.color}>{role.name}</Badge>
                            <span className="text-sm text-muted-foreground">{role.users} users</span>
                          </div>
                          <p className="text-sm text-muted-foreground">{role.description}</p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {role.permissions.slice(0, 3).map((permission, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {permission}
                              </Badge>
                            ))}
                            {role.permissions.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{role.permissions.length - 3} more
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="permissions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5" />
                Permission Management
              </CardTitle>
              <CardDescription>Configure granular permissions for different system resources</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {permissionCategories.map((category, categoryIndex) => (
                  <div key={categoryIndex} className="space-y-4">
                    <h3 className="font-semibold text-lg border-b pb-2">{category.category}</h3>
                    <div className="grid gap-3">
                      {category.permissions.map((permission, permissionIndex) => (
                        <div key={permissionIndex} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{permission.name}</p>
                            <p className="text-sm text-muted-foreground">{permission.description}</p>
                          </div>
                          <div className="flex items-center gap-4">
                            <Switch defaultChecked />
                            <Button variant="outline" size="sm">
                              <Settings className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Security Policies
              </CardTitle>
              <CardDescription>Configure security settings and access policies</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Multi-Factor Authentication</h4>
                    <p className="text-sm text-muted-foreground">Require MFA for all users</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Password Complexity</h4>
                    <p className="text-sm text-muted-foreground">Enforce strong password requirements</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Session Timeout</h4>
                    <p className="text-sm text-muted-foreground">Automatic logout after inactivity</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">IP Whitelisting</h4>
                    <p className="text-sm text-muted-foreground">Restrict access to approved IP addresses</p>
                  </div>
                  <Switch />
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">Access Policies</h3>
                <div className="grid gap-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">API Rate Limiting</p>
                        <p className="text-sm text-muted-foreground">1000 requests per hour per user</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Active</Badge>
                    </div>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Concurrent Sessions</p>
                        <p className="text-sm text-muted-foreground">Maximum 3 active sessions per user</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Active</Badge>
                    </div>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Failed Login Attempts</p>
                        <p className="text-sm text-muted-foreground">Lock account after 5 failed attempts</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Active</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}