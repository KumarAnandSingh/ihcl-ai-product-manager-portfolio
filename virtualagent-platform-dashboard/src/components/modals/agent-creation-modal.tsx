"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Bot, Brain, Users, MessageSquare, Zap, CheckCircle } from "lucide-react"
import { toast } from "sonner"

interface AgentCreationModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AgentCreationModal({ open, onOpenChange }: AgentCreationModalProps) {
  const [isCreating, setIsCreating] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    type: "",
    model: "gpt-4",
    language: "en",
    personality: "professional",
    capabilities: [] as string[]
  })

  const agentTypes = [
    {
      id: "customer-service",
      name: "Customer Service Agent",
      description: "Handle customer inquiries, support tickets, and service requests",
      icon: Users,
      color: "bg-blue-100 text-blue-800"
    },
    {
      id: "concierge",
      name: "Hotel Concierge Agent",
      description: "Provide guest services, recommendations, and booking assistance",
      icon: MessageSquare,
      color: "bg-purple-100 text-purple-800"
    },
    {
      id: "sales-assistant",
      name: "Sales Assistant Agent",
      description: "Support sales processes, lead qualification, and customer engagement",
      icon: Zap,
      color: "bg-green-100 text-green-800"
    },
    {
      id: "technical-support",
      name: "Technical Support Agent",
      description: "Troubleshoot technical issues and provide IT support",
      icon: Bot,
      color: "bg-orange-100 text-orange-800"
    }
  ]

  const capabilities = [
    "Multi-language Support",
    "Voice Recognition",
    "Sentiment Analysis",
    "Knowledge Base Integration",
    "CRM Integration",
    "Email Automation",
    "Booking Management",
    "Payment Processing",
    "Analytics Reporting",
    "Escalation Management"
  ]

  const handleCreate = async () => {
    setIsCreating(true)
    toast.loading("Creating your AI agent...")

    // Simulate agent creation process
    setTimeout(() => {
      toast.success(`${formData.name} agent created successfully!`)
      setIsCreating(false)
      onOpenChange(false)
      setCurrentStep(1)
      setFormData({
        name: "",
        description: "",
        type: "",
        model: "gpt-4",
        language: "en",
        personality: "professional",
        capabilities: []
      })
    }, 2000)
  }

  const nextStep = () => {
    if (currentStep < 3) setCurrentStep(currentStep + 1)
  }

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1)
  }

  const toggleCapability = (capability: string) => {
    setFormData(prev => ({
      ...prev,
      capabilities: prev.capabilities.includes(capability)
        ? prev.capabilities.filter(c => c !== capability)
        : [...prev.capabilities, capability]
    }))
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Agent Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Hotel Concierge Assistant"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe what this agent will do..."
                rows={3}
              />
            </div>
            <div>
              <Label>Agent Type</Label>
              <div className="grid grid-cols-2 gap-3 mt-2">
                {agentTypes.map((type) => {
                  const IconComponent = type.icon
                  return (
                    <div
                      key={type.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-all ${
                        formData.type === type.id
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                      onClick={() => setFormData(prev => ({ ...prev, type: type.id }))}
                    >
                      <div className="flex items-center gap-2">
                        <IconComponent className="h-4 w-4" />
                        <span className="font-medium text-sm">{type.name}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{type.description}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )
      case 2:
        return (
          <div className="space-y-4">
            <div>
              <Label>AI Model</Label>
              <Select value={formData.model} onValueChange={(value) => setFormData(prev => ({ ...prev, model: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4 (Recommended)</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="claude-3">Claude 3 Sonnet</SelectItem>
                  <SelectItem value="gemini-pro">Gemini Pro</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Primary Language</Label>
              <Select value={formData.language} onValueChange={(value) => setFormData(prev => ({ ...prev, language: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="hi">Hindi</SelectItem>
                  <SelectItem value="es">Spanish</SelectItem>
                  <SelectItem value="fr">French</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Personality</Label>
              <Select value={formData.personality} onValueChange={(value) => setFormData(prev => ({ ...prev, personality: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="professional">Professional & Formal</SelectItem>
                  <SelectItem value="friendly">Friendly & Casual</SelectItem>
                  <SelectItem value="helpful">Helpful & Supportive</SelectItem>
                  <SelectItem value="concise">Concise & Direct</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )
      case 3:
        return (
          <div className="space-y-4">
            <div>
              <Label>Agent Capabilities</Label>
              <p className="text-sm text-gray-500 mb-3">Select the capabilities your agent should have:</p>
              <div className="grid grid-cols-2 gap-2">
                {capabilities.map((capability) => (
                  <div
                    key={capability}
                    className={`p-2 border rounded cursor-pointer text-sm transition-all ${
                      formData.capabilities.includes(capability)
                        ? "border-blue-500 bg-blue-50 text-blue-700"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                    onClick={() => toggleCapability(capability)}
                  >
                    {capability}
                  </div>
                ))}
              </div>
            </div>
            <Separator />
            <div>
              <Label>Configuration Summary</Label>
              <div className="mt-2 p-3 bg-gray-50 rounded-lg space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Name:</span>
                  <span className="text-sm">{formData.name || "Not specified"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Type:</span>
                  <span className="text-sm">{agentTypes.find(t => t.id === formData.type)?.name || "Not selected"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Model:</span>
                  <span className="text-sm">{formData.model}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Capabilities:</span>
                  <span className="text-sm">{formData.capabilities.length} selected</span>
                </div>
              </div>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Create New AI Agent
          </DialogTitle>
          <DialogDescription>
            Step {currentStep} of 3 - {currentStep === 1 ? "Basic Information" : currentStep === 2 ? "Configuration" : "Capabilities & Review"}
          </DialogDescription>
        </DialogHeader>

        <div className="flex justify-center mb-4">
          <div className="flex items-center space-x-2">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                    step <= currentStep
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {step < currentStep ? <CheckCircle className="h-4 w-4" /> : step}
                </div>
                {step < 3 && (
                  <div className={`w-12 h-1 ${step < currentStep ? "bg-blue-500" : "bg-gray-200"}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="min-h-[300px]">
          {renderStep()}
        </div>

        <DialogFooter className="flex justify-between">
          <div>
            {currentStep > 1 && (
              <Button variant="outline" onClick={prevStep}>
                Previous
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            {currentStep < 3 ? (
              <Button 
                onClick={nextStep}
                disabled={currentStep === 1 && (!formData.name || !formData.type)}
              >
                Next
              </Button>
            ) : (
              <Button onClick={handleCreate} disabled={isCreating}>
                {isCreating ? "Creating..." : "Create Agent"}
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}