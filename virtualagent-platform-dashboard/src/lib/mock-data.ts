// Mock data for enterprise dashboard demonstration
export interface Agent {
  id: string
  name: string
  status: 'active' | 'inactive' | 'deploying' | 'error'
  type: 'customer_service' | 'sales' | 'support' | 'analytics'
  version: string
  lastUpdated: string
  conversations: number
  successRate: number
  avgResponseTime: number
  cost: number
}

export interface Organization {
  id: string
  name: string
  plan: string
  agents: number
  users: number
  apiCalls: number
  cost: number
}

export interface LLMModel {
  id: string
  name: string
  provider: 'openai' | 'anthropic' | 'google' | 'meta'
  status: 'active' | 'inactive'
  tokensUsed: number
  cost: number
  avgLatency: number
  successRate: number
}

export interface Integration {
  id: string
  name: string
  type: 'CRM' | 'ERP' | 'Database' | 'API' | 'Messaging'
  status: 'connected' | 'disconnected' | 'syncing' | 'error'
  lastSync: string
  dataVolume: number
}

export const mockAgents: Agent[] = [
  {
    id: 'agent-1',
    name: 'Customer Support Agent',
    status: 'active',
    type: 'customer_service',
    version: 'v2.1.0',
    lastUpdated: '2024-01-15T10:30:00Z',
    conversations: 1247,
    successRate: 94.5,
    avgResponseTime: 2.3,
    cost: 245.67
  },
  {
    id: 'agent-2',
    name: 'Sales Assistant',
    status: 'active',
    type: 'sales',
    version: 'v1.8.2',
    lastUpdated: '2024-01-14T16:45:00Z',
    conversations: 892,
    successRate: 91.2,
    avgResponseTime: 1.8,
    cost: 178.34
  },
  {
    id: 'agent-3',
    name: 'Technical Support Bot',
    status: 'deploying',
    type: 'support',
    version: 'v3.0.0-beta',
    lastUpdated: '2024-01-15T12:00:00Z',
    conversations: 0,
    successRate: 0,
    avgResponseTime: 0,
    cost: 0
  },
  {
    id: 'agent-4',
    name: 'Analytics Reporter',
    status: 'active',
    type: 'analytics',
    version: 'v1.5.1',
    lastUpdated: '2024-01-13T09:15:00Z',
    conversations: 456,
    successRate: 98.7,
    avgResponseTime: 3.2,
    cost: 89.23
  },
  {
    id: 'agent-5',
    name: 'Onboarding Assistant',
    status: 'error',
    type: 'customer_service',
    version: 'v2.0.1',
    lastUpdated: '2024-01-12T14:20:00Z',
    conversations: 234,
    successRate: 87.3,
    avgResponseTime: 2.9,
    cost: 67.89
  }
]

export const mockOrganizations: Organization[] = [
  {
    id: 'org-1',
    name: 'Acme Corporation',
    plan: 'Enterprise',
    agents: 12,
    users: 45,
    apiCalls: 125000,
    cost: 2450.00
  },
  {
    id: 'org-2',
    name: 'TechStart Inc',
    plan: 'Professional',
    agents: 5,
    users: 18,
    apiCalls: 45000,
    cost: 890.00
  },
  {
    id: 'org-3',
    name: 'Global Solutions Ltd',
    plan: 'Enterprise',
    agents: 24,
    users: 87,
    apiCalls: 340000,
    cost: 5670.00
  }
]

export const mockLLMModels: LLMModel[] = [
  {
    id: 'gpt-4',
    name: 'GPT-4 Turbo',
    provider: 'openai',
    status: 'active',
    tokensUsed: 2450000,
    cost: 1225.50,
    avgLatency: 1.2,
    successRate: 99.1
  },
  {
    id: 'claude-3',
    name: 'Claude 3 Sonnet',
    provider: 'anthropic',
    status: 'active',
    tokensUsed: 1890000,
    cost: 945.30,
    avgLatency: 1.4,
    successRate: 98.8
  },
  {
    id: 'gemini-pro',
    name: 'Gemini Pro',
    provider: 'google',
    status: 'active',
    tokensUsed: 1234000,
    cost: 617.20,
    avgLatency: 1.1,
    successRate: 97.9
  },
  {
    id: 'llama-2',
    name: 'Llama 2 70B',
    provider: 'meta',
    status: 'inactive',
    tokensUsed: 567000,
    cost: 283.50,
    avgLatency: 2.1,
    successRate: 96.5
  }
]

export const mockIntegrations: Integration[] = [
  {
    id: 'int-1',
    name: 'Salesforce CRM',
    type: 'CRM',
    status: 'connected',
    lastSync: '2024-01-15T11:45:00Z',
    dataVolume: 25000
  },
  {
    id: 'int-2',
    name: 'SAP ERP',
    type: 'ERP',
    status: 'syncing',
    lastSync: '2024-01-15T10:30:00Z',
    dataVolume: 150000
  },
  {
    id: 'int-3',
    name: 'PostgreSQL Database',
    type: 'Database',
    status: 'connected',
    lastSync: '2024-01-15T12:00:00Z',
    dataVolume: 89000
  },
  {
    id: 'int-4',
    name: 'Slack Messaging',
    type: 'Messaging',
    status: 'connected',
    lastSync: '2024-01-15T11:55:00Z',
    dataVolume: 12000
  },
  {
    id: 'int-5',
    name: 'Legacy API Gateway',
    type: 'API',
    status: 'error',
    lastSync: '2024-01-14T08:30:00Z',
    dataVolume: 0
  }
]

export const analyticsData = {
  conversationTrends: [
    { month: 'Jan', conversations: 8500, resolved: 8075 },
    { month: 'Feb', conversations: 9200, resolved: 8740 },
    { month: 'Mar', conversations: 10100, resolved: 9595 },
    { month: 'Apr', conversations: 11500, resolved: 10925 },
    { month: 'May', conversations: 12800, resolved: 12160 },
    { month: 'Jun', conversations: 14200, resolved: 13490 },
  ],
  costBreakdown: [
    { name: 'OpenAI GPT-4', value: 1225.50, color: '#0088FE' },
    { name: 'Anthropic Claude', value: 945.30, color: '#00C49F' },
    { name: 'Google Gemini', value: 617.20, color: '#FFBB28' },
    { name: 'Infrastructure', value: 342.80, color: '#FF8042' },
    { name: 'Data Storage', value: 156.90, color: '#8884D8' },
  ],
  performanceMetrics: [
    { metric: 'Average Response Time', value: 2.1, unit: 's', trend: 'down', change: -0.3 },
    { metric: 'Success Rate', value: 94.2, unit: '%', trend: 'up', change: 1.5 },
    { metric: 'User Satisfaction', value: 4.6, unit: '/5', trend: 'up', change: 0.2 },
    { metric: 'Cost per Conversation', value: 0.42, unit: '$', trend: 'down', change: -0.05 },
  ]
}

export const securityIncidents = [
  {
    id: 'sec-1',
    type: 'Suspicious Login',
    severity: 'Medium',
    timestamp: '2024-01-15T11:30:00Z',
    description: 'Multiple failed login attempts from unknown IP',
    status: 'Investigating'
  },
  {
    id: 'sec-2',
    type: 'API Rate Limit Exceeded',
    severity: 'Low',
    timestamp: '2024-01-15T09:45:00Z',
    description: 'Agent exceeded rate limits during peak hours',
    status: 'Resolved'
  },
  {
    id: 'sec-3',
    type: 'Data Access Anomaly',
    severity: 'High',
    timestamp: '2024-01-14T16:20:00Z',
    description: 'Unusual data access pattern detected',
    status: 'Under Review'
  }
]