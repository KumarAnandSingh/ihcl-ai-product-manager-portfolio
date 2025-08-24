"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { AnimatedCard, AnimatedMetricCard } from "@/components/animated-card";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  Brain, 
  Zap, 
  BarChart3, 
  Globe, 
  Lock,
  Eye,
  Users,
  FileText,
  Play,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  Command
} from "lucide-react";

interface IncidentScenario {
  type: string;
  description: string;
  location: string;
  priority: "low" | "medium" | "high" | "critical";
}

interface AgentExecution {
  step: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  duration?: number;
  result?: string;
}

interface SecurityAction {
  action_type: string;
  description: string;
  tool: string;
  result: string;
  execution_time: string;
}

interface SecurityNotification {
  recipient: string;
  channel: string;
  status: string;
}

interface IncidentResult {
  incident_id: string;
  response_status: string;
  autonomous_actions_taken: number;
  human_intervention_required: boolean;
  response_time_seconds: number;
  automation_success_rate: number;
  business_impact: {
    potential_loss_prevented: number;
    operational_efficiency_gain: string;
    guest_satisfaction_maintained: string;
    compliance_status: string;
  };
  actions_summary: {
    planned: number;
    completed: SecurityAction[];
    failed: any[];
  };
  notifications_sent: SecurityNotification[];
  reasoning_log: string[];
  performance_metrics: {
    decision_confidence: number;
    system_integrations: number;
    escalation_level: number;
  };
}

interface SecurityMetrics {
  totalIncidents: number;
  avgResponseTime: number;
  resolutionRate: number;
  automationRate: number;
  costSaved: number;
}

const incidentScenarios: Record<string, IncidentScenario> = {
  "Unauthorized Room Access": {
    type: "unauthorized_access",
    description: "Guest attempting to access Room 315 after checkout, keycard still active",
    location: "Room 315, Floor 3",
    priority: "high"
  },
  "Payment Fraud Detection": {
    type: "payment_fraud", 
    description: "Multiple failed payment attempts detected for booking ID BK-7891, suspicious IP address",
    location: "Front Desk, Payment Terminal 2",
    priority: "critical"
  },
  "Data Privacy Breach": {
    type: "data_breach",
    description: "Potential PII exposure detected in guest services system logs",
    location: "IT Server Room, Database Cluster", 
    priority: "critical"
  },
  "Physical Security Alert": {
    type: "physical_security",
    description: "Motion detected in restricted spa area during closed hours",
    location: "Spa Wellness Center, Floor 2",
    priority: "medium"
  }
};

const priorityColors = {
  low: "bg-green-500",
  medium: "bg-yellow-500", 
  high: "bg-orange-500",
  critical: "bg-red-500"
};

export function SecurityOperationsDashboard() {
  const [selectedScenario, setSelectedScenario] = useState("Unauthorized Room Access");
  const [incident, setIncident] = useState(incidentScenarios[selectedScenario]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionSteps, setExecutionSteps] = useState<AgentExecution[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [executionProgress, setExecutionProgress] = useState(0);
  const [incidentResult, setIncidentResult] = useState<IncidentResult | null>(null);
  const [metrics, setMetrics] = useState<SecurityMetrics>({
    totalIncidents: 47,
    avgResponseTime: 2.3,
    resolutionRate: 94,
    automationRate: 87,
    costSaved: 125000
  });

  const executeSecurityResponse = async () => {
    setIsExecuting(true);
    setCurrentStep(0);
    setExecutionProgress(0);
    setIncidentResult(null);

    const steps: AgentExecution[] = [
      { step: "🧠 Analyzing threat severity and risk assessment", status: "pending" },
      { step: "⚖️ Making autonomous decisions (96% confidence)", status: "pending" },
      { step: "🛡️ Activating security protocols and countermeasures", status: "pending" },
      { step: "🔧 Executing multi-system coordination", status: "pending" },
      { step: "📢 Notifying stakeholders and emergency contacts", status: "pending" },
      { step: "✅ Monitoring outcomes and completing response", status: "pending" }
    ];

    setExecutionSteps(steps);

    for (let i = 0; i < steps.length; i++) {
      // Mark current step as in progress
      setCurrentStep(i);
      setExecutionSteps(prev => prev.map((step, idx) => 
        idx === i ? { ...step, status: "in_progress" } : step
      ));
      setExecutionProgress((i / steps.length) * 100);

      // Simulate execution time
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

      // Mark step as completed
      setExecutionSteps(prev => prev.map((step, idx) => 
        idx === i ? { 
          ...step, 
          status: "completed",
          duration: Math.random() * 2 + 0.5,
          result: getStepResult(i, incident.type)
        } : step
      ));
    }

    setExecutionProgress(100);
    setIsExecuting(false);

    // Generate complete incident result
    const actions = getActionsForIncidentType(incident.type);
    const notifications = getNotificationsForIncidentType(incident.type);
    const incidentId = `INC-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.floor(Math.random() * 10000)}`;
    
    const result: IncidentResult = {
      incident_id: incidentId,
      response_status: "completed",
      autonomous_actions_taken: actions.length,
      human_intervention_required: false,
      response_time_seconds: 2.3,
      automation_success_rate: 1.0,
      business_impact: {
        potential_loss_prevented: getBusinessImpact(incident.type),
        operational_efficiency_gain: "85%",
        guest_satisfaction_maintained: "98%",
        compliance_status: "Fully compliant"
      },
      actions_summary: {
        planned: actions.length,
        completed: actions,
        failed: []
      },
      notifications_sent: notifications,
      reasoning_log: getReasoningLog(incident.type, actions.length),
      performance_metrics: {
        decision_confidence: 0.96,
        system_integrations: actions.length,
        escalation_level: 0
      }
    };

    setIncidentResult(result);

    // Update metrics
    setMetrics(prev => ({
      ...prev,
      totalIncidents: prev.totalIncidents + 1,
      avgResponseTime: (prev.avgResponseTime * prev.totalIncidents + 2.3) / (prev.totalIncidents + 1),
    }));
  };

  const getStepResult = (stepIndex: number, incidentType: string): string => {
    const results = {
      unauthorized_access: [
        "Threat classified as HIGH priority - unauthorized access attempt",
        "Decision: Immediate keycard deactivation + security dispatch",
        "Keycard revoked, door locked, security alerted",
        "PMS updated, guest contacted, incident logged",
        "Security team dispatched, management notified",
        "Incident contained - ₹15,000 potential loss prevented"
      ],
      payment_fraud: [
        "Fraud pattern detected with 92% confidence score",
        "Decision: Block transaction + freeze account + verify identity",  
        "Payment blocked, account secured, fraud team alerted",
        "Banking systems coordinated, compliance protocols activated",
        "Risk team notified, guest verification initiated",
        "Fraud prevented - ₹45,000 potential loss avoided"
      ],
      data_breach: [
        "PII exposure detected in 247 records - CRITICAL severity",
        "Decision: Isolate systems + initiate breach protocol",
        "Database isolated, access restricted, forensics started", 
        "Legal team engaged, compliance reporting prepared",
        "Regulatory bodies notified, affected parties identified",
        "Breach contained - DPDP compliance maintained"
      ],
      physical_security: [
        "Motion detected in restricted area - investigating",
        "Decision: Activate cameras + dispatch security patrol",
        "CCTV activated, motion sensors armed, area secured",
        "Security patrol dispatched, facility manager alerted",
        "Spa manager notified, incident documentation started", 
        "Area secured - ₹8,000 potential damage prevented"
      ]
    };

    return results[incidentType as keyof typeof results]?.[stepIndex] || "Operation completed successfully";
  };

  const getActionsForIncidentType = (incidentType: string): SecurityAction[] => {
    const actionsMap = {
      "unauthorized_access": [
        {
          action_type: "access_control",
          description: "Revoked keycard access for Room 315",
          tool: "Access Control System",
          result: "Success - Card ID GUEST_315_789 deactivated",
          execution_time: "0.3s"
        },
        {
          action_type: "room_management", 
          description: "Updated room status to Security Hold",
          tool: "Property Management System",
          result: "Success - Room 315 marked for investigation",
          execution_time: "0.5s"
        },
        {
          action_type: "guest_notification",
          description: "Contacted guest regarding checkout procedure",
          tool: "Notification Orchestrator",
          result: "Success - SMS sent to guest mobile",
          execution_time: "0.8s"
        }
      ],
      "payment_fraud": [
        {
          action_type: "fraud_analysis",
          description: "Analyzed payment pattern and IP geolocation",
          tool: "Fraud Detection System",
          result: "Success - 92% fraud probability confirmed",
          execution_time: "1.2s"
        },
        {
          action_type: "payment_block",
          description: "Blocked suspicious payment methods",
          tool: "Payment Gateway",
          result: "Success - 3 cards flagged and blocked",
          execution_time: "0.6s"
        },
        {
          action_type: "guest_verification",
          description: "Initiated identity verification process",
          tool: "Guest Services System",
          result: "Success - Verification link sent to guest",
          execution_time: "0.4s"
        }
      ],
      "data_breach": [
        {
          action_type: "breach_containment",
          description: "Isolated affected database cluster",
          tool: "Database Management System",
          result: "Success - Cluster DB-03 isolated",
          execution_time: "0.7s"
        },
        {
          action_type: "data_audit",
          description: "Scanned for PII exposure patterns",
          tool: "Data Privacy Scanner",
          result: "Success - 247 records flagged for review",
          execution_time: "2.1s"
        },
        {
          action_type: "regulatory_notification",
          description: "Prepared DPDP compliance notification",
          tool: "Compliance Management",
          result: "Success - 72-hour notice prepared",
          execution_time: "0.5s"
        }
      ],
      "physical_security": [
        {
          action_type: "area_assessment",
          description: "Activated motion sensors and cameras",
          tool: "Security Monitoring System",
          result: "Success - Live feed enabled for Spa area",
          execution_time: "0.4s"
        },
        {
          action_type: "access_restriction",
          description: "Temporary lockdown of spa wellness center",
          tool: "Access Control System", 
          result: "Success - Area secured for 30 minutes",
          execution_time: "0.6s"
        }
      ]
    };
    
    return actionsMap[incidentType as keyof typeof actionsMap] || [];
  };

  const getNotificationsForIncidentType = (incidentType: string): SecurityNotification[] => {
    const notificationsMap = {
      "unauthorized_access": [
        {recipient: "Security Manager", channel: "SMS", status: "Delivered"},
        {recipient: "Housekeeping Supervisor", channel: "Slack", status: "Read"},
        {recipient: "Guest Relations", channel: "Email", status: "Delivered"}
      ],
      "payment_fraud": [
        {recipient: "Finance Manager", channel: "Phone Call", status: "Answered"},
        {recipient: "General Manager", channel: "SMS", status: "Delivered"},
        {recipient: "Compliance Officer", channel: "Email", status: "Delivered"}
      ],
      "data_breach": [
        {recipient: "Chief Security Officer", channel: "Phone Call", status: "Answered"},
        {recipient: "Legal Counsel", channel: "Email", status: "Delivered"},
        {recipient: "Data Protection Officer", channel: "SMS", status: "Delivered"}
      ],
      "physical_security": [
        {recipient: "Security Officer Kumar", channel: "Mobile App", status: "Acknowledged"},
        {recipient: "Spa Manager", channel: "WhatsApp", status: "Read"}
      ]
    };
    
    return notificationsMap[incidentType as keyof typeof notificationsMap] || [];
  };

  const getBusinessImpact = (incidentType: string): number => {
    const impactMap = {
      "unauthorized_access": 15000,
      "payment_fraud": 45000,
      "data_breach": 125000,
      "physical_security": 8000
    };
    return impactMap[incidentType as keyof typeof impactMap] || 10000;
  };

  const getReasoningLog = (incidentType: string, actionsCount: number): string[] => {
    const priorityLevel = incidentScenarios[selectedScenario]?.priority || "medium";
    const businessImpact = getBusinessImpact(incidentType);
    
    return [
      `Incident classified as ${priorityLevel.toUpperCase()} priority ${incidentType.replace('_', ' ')}`,
      `Multi-criteria risk assessment completed in 0.3s`,
      `Decision confidence: 96% - proceeding with autonomous response`,
      `Executed ${actionsCount} coordinated actions across hotel systems`,
      `All system integrations successful - no human intervention required`,
      `Business impact: ₹${businessImpact.toLocaleString()} potential loss prevented`
    ];
  };

  useEffect(() => {
    setIncident(incidentScenarios[selectedScenario]);
  }, [selectedScenario]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <div className="max-w-7xl mx-auto bg-white shadow-2xl flex flex-col" style={{ minHeight: '100vh' }}>
        {/* Header */}
        <motion.div 
          className="bg-gradient-to-r from-red-600 via-orange-600 to-yellow-600 text-white p-6 text-center relative overflow-hidden flex-shrink-0"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-center gap-3 mb-2">
              <motion.div
                initial={{ rotate: 0 }}
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              >
                <Shield className="h-8 w-8" />
              </motion.div>
              <h1 className="text-3xl font-bold">Agentic Security Operations Center</h1>
              <Tooltip>
                <TooltipTrigger>
                  <Command className="h-5 w-5 opacity-70 hover:opacity-100" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Press ⌘K for quick security actions</p>
                </TooltipContent>
              </Tooltip>
            </div>
            <p className="text-lg opacity-90 mb-1">Advanced Autonomous Hotel Security Intelligence</p>
            <p className="text-sm opacity-80">AI-powered incident response with real-time decision making</p>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="p-6 bg-slate-50 flex-1 overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            {/* Security Incident Simulator */}
            <div className="lg:col-span-2 flex flex-col">
              <AnimatedCard delay={0.1}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    Security Incident Simulator
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Incident Scenario</label>
                    <Select value={selectedScenario} onValueChange={setSelectedScenario}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.keys(incidentScenarios).map((scenario) => (
                          <SelectItem key={scenario} value={scenario}>
                            {scenario}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Description</label>
                    <Textarea 
                      value={incident.description}
                      onChange={(e) => setIncident(prev => ({ ...prev, description: e.target.value }))}
                      className="min-h-[80px]"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Location</label>
                      <input 
                        type="text" 
                        value={incident.location}
                        onChange={(e) => setIncident(prev => ({ ...prev, location: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Priority</label>
                      <Select 
                        value={incident.priority} 
                        onValueChange={(value) => setIncident(prev => ({ ...prev, priority: value as any }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="critical">Critical</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge className={`${priorityColors[incident.priority]} text-white`}>
                      {incident.priority.toUpperCase()} PRIORITY
                    </Badge>
                    <Badge variant="outline">
                      {incident.type.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>

                  <Button 
                    onClick={executeSecurityResponse}
                    disabled={isExecuting}
                    className="w-full bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600"
                    size="lg"
                  >
                    {isExecuting ? (
                      <>
                        <Activity className="h-5 w-5 mr-2 animate-spin" />
                        Autonomous Response Active...
                      </>
                    ) : (
                      <>
                        <Shield className="h-5 w-5 mr-2" />
                        🚀 Launch Autonomous Response
                      </>
                    )}
                  </Button>
                </CardContent>
              </AnimatedCard>

              {/* Execution Progress */}
              <AnimatePresence>
                {(isExecuting || executionSteps.length > 0) && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="mt-4"
                  >
                    <AnimatedCard delay={0.3}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Brain className="h-5 w-5" />
                          Autonomous Agent Execution
                        </CardTitle>
                        <div className="space-y-2">
                          <Progress value={executionProgress} className="w-full" />
                          <div className="text-sm text-muted-foreground">
                            Progress: {Math.round(executionProgress)}% Complete
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        {executionSteps.map((step, index) => (
                          <motion.div
                            key={index}
                            className="flex items-start gap-3 p-3 rounded-lg border"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            {step.status === "completed" && <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />}
                            {step.status === "in_progress" && <Activity className="h-5 w-5 text-blue-500 animate-spin mt-0.5" />}
                            {step.status === "pending" && <Clock className="h-5 w-5 text-gray-400 mt-0.5" />}
                            {step.status === "failed" && <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />}
                            
                            <div className="flex-1">
                              <div className="font-medium">{step.step}</div>
                              {step.result && (
                                <div className="text-sm text-muted-foreground mt-1">{step.result}</div>
                              )}
                              {step.duration && (
                                <div className="text-xs text-green-600 mt-1">
                                  Completed in {step.duration.toFixed(1)}s
                                </div>
                              )}
                            </div>
                          </motion.div>
                        ))}
                      </CardContent>
                    </AnimatedCard>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Detailed Results Section */}
              <AnimatePresence>
                {incidentResult && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="mt-4 space-y-4"
                  >
                    {/* Success Summary */}
                    <AnimatedCard delay={0.1}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-green-600">
                          <CheckCircle className="h-6 w-6" />
                          Incident {incidentResult.incident_id} Resolved Autonomously
                        </CardTitle>
                        <div className="text-sm text-muted-foreground">
                          Response completed in {incidentResult.response_time_seconds}s with {Math.round(incidentResult.automation_success_rate * 100)}% success rate
                        </div>
                      </CardHeader>
                    </AnimatedCard>

                    {/* Execution Metrics */}
                    <AnimatedCard delay={0.2}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <BarChart3 className="h-5 w-5" />
                          📊 Execution Metrics
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                          <div className="text-center p-3 bg-blue-50 rounded-lg">
                            <div className="text-2xl font-bold text-blue-600">
                              {incidentResult.response_time_seconds}s
                            </div>
                            <div className="text-sm text-blue-700">Response Time</div>
                            <div className="text-xs text-green-600">🚀 Real-time</div>
                          </div>
                          <div className="text-center p-3 bg-green-50 rounded-lg">
                            <div className="text-2xl font-bold text-green-600">
                              {incidentResult.autonomous_actions_taken}
                            </div>
                            <div className="text-sm text-green-700">Actions Taken</div>
                            <div className="text-xs text-green-600">🤖 Autonomous</div>
                          </div>
                          <div className="text-center p-3 bg-purple-50 rounded-lg">
                            <div className="text-2xl font-bold text-purple-600">
                              {Math.round(incidentResult.automation_success_rate * 100)}%
                            </div>
                            <div className="text-sm text-purple-700">Success Rate</div>
                            <div className="text-xs text-green-600">✅ Perfect</div>
                          </div>
                          <div className="text-center p-3 bg-orange-50 rounded-lg">
                            <div className="text-2xl font-bold text-orange-600">
                              ₹{incidentResult.business_impact.potential_loss_prevented.toLocaleString()}
                            </div>
                            <div className="text-sm text-orange-700">Business Impact</div>
                            <div className="text-xs text-green-600">💰 Prevented</div>
                          </div>
                        </div>
                      </CardContent>
                    </AnimatedCard>

                    {/* Autonomous Actions Executed */}
                    <AnimatedCard delay={0.3}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Zap className="h-5 w-5" />
                          🔧 Autonomous Actions Executed
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        {incidentResult.actions_summary.completed.map((action, index) => (
                          <motion.div
                            key={index}
                            className="border border-gray-200 rounded-lg p-4 bg-gradient-to-r from-green-50 to-blue-50"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 + index * 0.1 }}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="font-semibold text-gray-900 mb-2">
                                  Action {index + 1}: {action.description}
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                                  <div>
                                    <span className="font-medium text-gray-700">Tool Used:</span>
                                    <div className="text-gray-600">{action.tool}</div>
                                  </div>
                                  <div>
                                    <span className="font-medium text-gray-700">Result:</span>
                                    <div className="text-gray-600">{action.result}</div>
                                  </div>
                                </div>
                              </div>
                              <div className="ml-4 text-right">
                                <div className="text-sm font-medium text-green-600">{action.execution_time}</div>
                                <Badge className="bg-green-500 text-white mt-1">
                                  ✅ Completed
                                </Badge>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </CardContent>
                    </AnimatedCard>

                    {/* Notifications Coordinated */}
                    <AnimatedCard delay={0.4}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Users className="h-5 w-5" />
                          📢 Notifications Coordinated
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {incidentResult.notifications_sent.map((notification, index) => (
                            <motion.div
                              key={index}
                              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                              initial={{ opacity: 0, x: 20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.5 + index * 0.1 }}
                            >
                              <div className="flex items-center gap-3">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span className="font-medium">{notification.recipient}</span>
                                <span className="text-sm text-gray-600">via {notification.channel}</span>
                              </div>
                              <Badge variant={notification.status === "Answered" || notification.status === "Read" || notification.status === "Acknowledged" ? "default" : "secondary"}>
                                {notification.status}
                              </Badge>
                            </motion.div>
                          ))}
                        </div>
                      </CardContent>
                    </AnimatedCard>

                    {/* Agent Reasoning Log */}
                    <AnimatedCard delay={0.5}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Brain className="h-5 w-5" />
                          🧠 Agent Reasoning Log
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {incidentResult.reasoning_log.map((reasoning, index) => (
                            <motion.div
                              key={index}
                              className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg"
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: 0.6 + index * 0.1 }}
                            >
                              <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
                                {index + 1}
                              </div>
                              <div className="text-sm text-gray-700">{reasoning}</div>
                            </motion.div>
                          ))}
                        </div>
                      </CardContent>
                    </AnimatedCard>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Metrics Sidebar */}
            <div className="space-y-6">
              {/* Real-time Metrics */}
              <AnimatedCard delay={0.2}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Security Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 gap-4">
                    <AnimatedMetricCard
                      title="Total Incidents"
                      value={metrics.totalIncidents}
                      icon={AlertTriangle}
                      delay={0.3}
                    />
                    <AnimatedMetricCard
                      title="Avg Response"
                      value={`${metrics.avgResponseTime}s`}
                      trend="up"
                      trendValue="40% faster"
                      icon={Zap}
                      delay={0.4}
                    />
                    <AnimatedMetricCard
                      title="Resolution Rate"
                      value={`${metrics.resolutionRate}%`}
                      trend="up"
                      trendValue="Enterprise grade"
                      icon={CheckCircle}
                      delay={0.5}
                    />
                    <AnimatedMetricCard
                      title="Cost Saved"
                      value={`₹${metrics.costSaved.toLocaleString()}`}
                      trend="up"
                      trendValue="This month"
                      icon={TrendingUp}
                      delay={0.6}
                    />
                  </div>
                </CardContent>
              </AnimatedCard>

              {/* System Status */}
              <AnimatedCard delay={0.4}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    System Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { system: "Access Control", status: "online", icon: Lock },
                    { system: "CCTV Monitoring", status: "online", icon: Eye },
                    { system: "Fraud Detection", status: "online", icon: Shield },
                    { system: "Emergency Protocol", status: "standby", icon: AlertTriangle }
                  ].map((item, index) => (
                    <motion.div
                      key={item.system}
                      className="flex items-center justify-between p-2 rounded-lg bg-gray-50"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                    >
                      <div className="flex items-center gap-2">
                        <item.icon className="h-4 w-4" />
                        <span className="text-sm font-medium">{item.system}</span>
                      </div>
                      <Badge 
                        variant={item.status === "online" ? "default" : "secondary"}
                        className={item.status === "online" ? "bg-green-500" : ""}
                      >
                        {item.status}
                      </Badge>
                    </motion.div>
                  ))}
                </CardContent>
              </AnimatedCard>
            </div>
          </div>
        </div>

        {/* Feature Highlights */}
        <AnimatedCard delay={0.7} className="m-6 mt-0">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Advanced Agentic Security Capabilities
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { icon: Brain, text: "Multi-step autonomous reasoning with 96% decision confidence", color: "text-purple-600" },
                { icon: Zap, text: "Real-time threat assessment and automated countermeasure deployment", color: "text-blue-600" },
                { icon: Shield, text: "Coordinated multi-system response across hotel security infrastructure", color: "text-green-600" },
                { icon: Globe, text: "Predictive threat intelligence with behavioral pattern analysis", color: "text-orange-600" },
                { icon: Users, text: "Intelligent stakeholder notification with priority-based escalation", color: "text-pink-600" },
                { icon: FileText, text: "Automated compliance reporting with audit trail generation", color: "text-red-600" },
              ].map((feature, index) => {
                const IconComponent = feature.icon;
                return (
                  <motion.div 
                    key={index}
                    className="flex items-start gap-3 p-4 bg-gradient-to-br from-white to-gray-50/50 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 + index * 0.1 }}
                    whileHover={{ scale: 1.02 }}
                  >
                    <motion.div
                      initial={{ rotate: 0 }}
                      animate={{ rotate: 360 }}
                      transition={{ duration: 4, delay: 1.0 + index * 0.3, repeat: Infinity, ease: "linear" }}
                    >
                      <IconComponent className={`h-5 w-5 ${feature.color} flex-shrink-0 mt-0.5`} />
                    </motion.div>
                    <span className="text-sm text-slate-700 font-medium">{feature.text}</span>
                  </motion.div>
                );
              })}
            </div>
          </CardContent>
        </AnimatedCard>
      </div>
    </div>
  );
}