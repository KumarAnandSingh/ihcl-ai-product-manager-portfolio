"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Shield, 
  AlertTriangle, 
  Lock, 
  Eye, 
  Users,
  CheckCircle,
  XCircle,
  Clock,
  Activity,
  Key,
  FileText,
  Globe
} from "lucide-react"
import { securityIncidents } from "@/lib/mock-data"
import { toast } from "sonner"

export default function SecurityPage() {
  const [isScanning, setIsScanning] = useState(false)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  
  const highIncidents = securityIncidents.filter(incident => incident.severity === 'High').length
  const mediumIncidents = securityIncidents.filter(incident => incident.severity === 'Medium').length
  const lowIncidents = securityIncidents.filter(incident => incident.severity === 'Low').length
  const resolvedIncidents = securityIncidents.filter(incident => incident.status === 'Resolved').length

  const handleSecurityScan = () => {
    setIsScanning(true)
    toast.loading("Initiating comprehensive security scan...")
    setTimeout(() => {
      toast.success("Security scan completed! 3 issues found.")
      setIsScanning(false)
    }, 3000)
  }

  const handleGenerateReport = () => {
    setIsGeneratingReport(true)
    toast.loading("Generating security compliance report...")
    setTimeout(() => {
      toast.success("Security report generated and downloaded!")
      setIsGeneratingReport(false)
    }, 2500)
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'High': return 'text-red-500'
      case 'Medium': return 'text-yellow-500'
      case 'Low': return 'text-blue-500'
      default: return 'text-gray-500'
    }
  }

  const securityMetrics = [
    { metric: 'Security Score', value: 94, unit: '/100', status: 'good' },
    { metric: 'Encryption Coverage', value: 100, unit: '%', status: 'good' },
    { metric: 'Compliance Rating', value: 98, unit: '%', status: 'good' },
    { metric: 'Vulnerability Score', value: 5, unit: '/100', status: 'good' }
  ]

  const complianceFrameworks = [
    { name: 'SOC 2 Type II', status: 'Compliant', lastAudit: '2024-01-10' },
    { name: 'ISO 27001', status: 'Compliant', lastAudit: '2023-12-15' },
    { name: 'GDPR', status: 'Compliant', lastAudit: '2024-01-05' },
    { name: 'HIPAA', status: 'In Progress', lastAudit: '2024-01-12' },
    { name: 'FedRAMP', status: 'Pending', lastAudit: 'N/A' }
  ]

  const auditLogs = [
    { id: 1, user: 'admin@virtualagent.com', action: 'Created new agent', resource: 'Customer Support Agent', timestamp: '2024-01-15T11:30:00Z' },
    { id: 2, user: 'john.doe@acme.com', action: 'Updated integration', resource: 'Salesforce CRM', timestamp: '2024-01-15T11:15:00Z' },
    { id: 3, user: 'jane.smith@techstart.com', action: 'Accessed sensitive data', resource: 'Customer Database', timestamp: '2024-01-15T10:45:00Z' },
    { id: 4, user: 'system', action: 'Security scan completed', resource: 'Platform Infrastructure', timestamp: '2024-01-15T10:00:00Z' },
    { id: 5, user: 'admin@virtualagent.com', action: 'Updated security policy', resource: 'Access Control Rules', timestamp: '2024-01-15T09:30:00Z' }
  ]

  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Security & Compliance</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={handleSecurityScan} disabled={isScanning}>
            {isScanning ? "Scanning..." : "Security Scan"}
          </Button>
          <Button variant="outline" onClick={handleGenerateReport} disabled={isGeneratingReport}>
            {isGeneratingReport ? "Generating..." : "Generate Report"}
          </Button>
        </div>
      </div>

      {/* Security Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Severity</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{highIncidents}</div>
            <p className="text-xs text-muted-foreground">
              Requires immediate attention
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Medium Severity</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{mediumIncidents}</div>
            <p className="text-xs text-muted-foreground">
              Under investigation
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low Severity</CardTitle>
            <AlertTriangle className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{lowIncidents}</div>
            <p className="text-xs text-muted-foreground">
              Monitoring
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{resolvedIncidents}</div>
            <p className="text-xs text-muted-foreground">
              This month
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="incidents" className="space-y-4">
        <TabsList>
          <TabsTrigger value="incidents">Security Incidents</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
        </TabsList>

        <TabsContent value="incidents">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Security Incidents</CardTitle>
                <CardDescription>
                  Latest security alerts and their current status
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {securityIncidents.map((incident) => (
                    <div key={incident.id} className="flex items-start justify-between p-4 border rounded-lg">
                      <div className="flex items-start space-x-4">
                        <AlertTriangle className={`h-5 w-5 mt-0.5 ${getSeverityColor(incident.severity)}`} />
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h4 className="font-medium">{incident.type}</h4>
                            <Badge 
                              variant={
                                incident.severity === 'High' ? 'destructive' :
                                incident.severity === 'Medium' ? 'secondary' : 'outline'
                              }
                            >
                              {incident.severity}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">
                            {incident.description}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(incident.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">
                          {incident.status}
                        </Badge>
                        <Button size="sm" variant="outline">
                          View Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Security Health Score</CardTitle>
                <CardDescription>
                  Overall security posture and recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="space-y-4">
                    {securityMetrics.map((metric) => (
                      <div key={metric.metric} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{metric.metric}</span>
                          <span className="text-sm font-bold">
                            {metric.value}{metric.unit}
                          </span>
                        </div>
                        <Progress value={metric.value} className="h-2" />
                      </div>
                    ))}
                  </div>
                  <div className="space-y-4">
                    <div className="text-center p-6 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
                      <Shield className="h-12 w-12 mx-auto mb-3 text-green-600" />
                      <h3 className="font-medium text-green-800 dark:text-green-200 mb-2">
                        Excellent Security Posture
                      </h3>
                      <p className="text-sm text-green-600 dark:text-green-300">
                        Your platform maintains strong security standards across all areas.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="compliance">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Compliance Frameworks</CardTitle>
                <CardDescription>
                  Current compliance status across industry standards
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {complianceFrameworks.map((framework) => (
                    <div key={framework.name} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <FileText className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{framework.name}</p>
                          <p className="text-sm text-muted-foreground">
                            Last audit: {framework.lastAudit}
                          </p>
                        </div>
                      </div>
                      <Badge 
                        variant={
                          framework.status === 'Compliant' ? 'default' :
                          framework.status === 'In Progress' ? 'secondary' : 'outline'
                        }
                      >
                        {framework.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Data Protection</CardTitle>
                  <CardDescription>
                    GDPR and privacy compliance measures
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Data Encryption</p>
                      <p className="text-sm text-muted-foreground">AES-256 encryption at rest and in transit</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Right to be Forgotten</p>
                      <p className="text-sm text-muted-foreground">Automated data deletion upon request</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Data Anonymization</p>
                      <p className="text-sm text-muted-foreground">PII scrubbing and anonymization</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Consent Management</p>
                      <p className="text-sm text-muted-foreground">Granular consent tracking and management</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Access Controls</CardTitle>
                  <CardDescription>
                    Identity and access management measures
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Multi-Factor Authentication</p>
                      <p className="text-sm text-muted-foreground">Required for all admin accounts</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Role-Based Access Control</p>
                      <p className="text-sm text-muted-foreground">Granular permission management</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Session Management</p>
                      <p className="text-sm text-muted-foreground">Automatic session timeout and rotation</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">API Key Management</p>
                      <p className="text-sm text-muted-foreground">Secure key generation and rotation</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="audit">
          <Card>
            <CardHeader>
              <CardTitle>Audit Trail</CardTitle>
              <CardDescription>
                Comprehensive activity logging for compliance and security
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {auditLogs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <Activity className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <div className="flex items-center space-x-2">
                          <p className="font-medium">{log.action}</p>
                          <Badge variant="outline" className="text-xs">
                            {log.resource}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-4 mt-1">
                          <p className="text-sm text-muted-foreground">
                            User: {log.user}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(log.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                    <Button size="sm" variant="ghost">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 pt-4 border-t">
                <Button className="w-full" variant="outline">
                  Load More Entries
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monitoring">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Real-time Security Monitoring</CardTitle>
                <CardDescription>
                  Active threat detection and system monitoring
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="text-center p-6 border rounded-lg">
                    <Eye className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                    <h3 className="font-medium">Network Monitoring</h3>
                    <p className="text-2xl font-bold mt-2 text-green-600">Active</p>
                    <p className="text-sm text-muted-foreground">24/7 traffic analysis</p>
                  </div>
                  
                  <div className="text-center p-6 border rounded-lg">
                    <Shield className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    <h3 className="font-medium">Intrusion Detection</h3>
                    <p className="text-2xl font-bold mt-2 text-green-600">Protected</p>
                    <p className="text-sm text-muted-foreground">Advanced threat detection</p>
                  </div>

                  <div className="text-center p-6 border rounded-lg">
                    <Lock className="h-8 w-8 mx-auto mb-2 text-purple-500" />
                    <h3 className="font-medium">Data Loss Prevention</h3>
                    <p className="text-2xl font-bold mt-2 text-green-600">Secure</p>
                    <p className="text-sm text-muted-foreground">No data leakage detected</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Threat Intelligence</CardTitle>
                  <CardDescription>
                    Latest security threats and mitigation status
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                    <div>
                      <p className="font-medium text-green-800 dark:text-green-200">No Active Threats</p>
                      <p className="text-sm text-green-600 dark:text-green-300">System is secure</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Recent Threat Mitigations:</p>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Blocked 1,247 malicious IP addresses</li>
                      <li>• Prevented 23 SQL injection attempts</li>
                      <li>• Quarantined 5 suspicious files</li>
                      <li>• Rate limited 89 aggressive bots</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Global Security Status</CardTitle>
                  <CardDescription>
                    Multi-region security monitoring
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Globe className="h-4 w-4 text-blue-500" />
                      <span className="text-sm">US East (Virginia)</span>
                    </div>
                    <Badge variant="default">Secure</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Globe className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Europe (Frankfurt)</span>
                    </div>
                    <Badge variant="default">Secure</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Globe className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm">Asia Pacific (Singapore)</span>
                    </div>
                    <Badge variant="secondary">Monitoring</Badge>
                  </div>

                  <div className="pt-2 border-t">
                    <Button className="w-full" size="sm" variant="outline">
                      View Regional Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}