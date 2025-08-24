import { NextRequest, NextResponse } from 'next/server'
import { createCanvas, loadImage } from 'canvas'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { type, data } = body

    if (type === 'agent-status') {
      return generateAgentStatusImage(data)
    } else if (type === 'workflow-summary') {
      return generateWorkflowSummaryImage(data)
    } else if (type === 'metrics-dashboard') {
      return generateMetricsDashboardImage(data)
    }

    return NextResponse.json({ error: 'Unknown image type' }, { status: 400 })
  } catch (error) {
    console.error('Image generation error:', error)
    return NextResponse.json({ error: 'Failed to generate image' }, { status: 500 })
  }
}

async function generateAgentStatusImage(data: any) {
  const canvas = createCanvas(800, 400)
  const ctx = canvas.getContext('2d')

  // Background gradient
  const gradient = ctx.createLinearGradient(0, 0, 800, 400)
  gradient.addColorStop(0, '#667eea')
  gradient.addColorStop(1, '#764ba2')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, 800, 400)

  // Title
  ctx.fillStyle = 'white'
  ctx.font = 'bold 32px Arial'
  ctx.fillText(`Agent: ${data.name}`, 50, 60)

  // Status indicator
  const statusColor = data.status === 'active' ? '#10b981' : 
                     data.status === 'error' ? '#ef4444' : '#6b7280'
  ctx.fillStyle = statusColor
  ctx.beginPath()
  ctx.arc(720, 50, 15, 0, Math.PI * 2)
  ctx.fill()

  // Metrics
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
  ctx.font = '18px Arial'
  ctx.fillText(`Conversations: ${data.conversations?.toLocaleString() || '0'}`, 50, 120)
  ctx.fillText(`Success Rate: ${data.successRate || '0'}%`, 50, 150)
  ctx.fillText(`Avg Response: ${data.avgResponseTime || '0'}s`, 50, 180)
  ctx.fillText(`Cost: $${data.cost || '0'}`, 50, 210)

  // Performance chart placeholder
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(50, 280)
  // Simple performance curve
  for (let i = 0; i < 10; i++) {
    const x = 50 + (i * 70)
    const y = 280 - (Math.sin(i * 0.5) * 30 + 30)
    ctx.lineTo(x, y)
  }
  ctx.stroke()

  // Generate timestamp
  ctx.fillStyle = 'rgba(255, 255, 255, 0.7)'
  ctx.font = '12px Arial'
  ctx.fillText(`Generated: ${new Date().toLocaleString()}`, 50, 380)

  const buffer = canvas.toBuffer('image/png')
  
  return new NextResponse(buffer, {
    headers: {
      'Content-Type': 'image/png',
      'Content-Length': buffer.length.toString(),
    },
  })
}

async function generateWorkflowSummaryImage(data: any) {
  const canvas = createCanvas(800, 600)
  const ctx = canvas.getContext('2d')

  // Background
  ctx.fillStyle = '#1f2937'
  ctx.fillRect(0, 0, 800, 600)

  // Title
  ctx.fillStyle = '#f9fafb'
  ctx.font = 'bold 28px Arial'
  ctx.fillText('Agentic Workflow Summary', 50, 50)

  // Workflow steps
  const steps = data.steps || []
  let yOffset = 100

  steps.forEach((step: any, index: number) => {
    const statusColor = step.status === 'completed' ? '#10b981' : 
                       step.status === 'running' ? '#3b82f6' :
                       step.status === 'failed' ? '#ef4444' : '#6b7280'

    // Step indicator
    ctx.fillStyle = statusColor
    ctx.beginPath()
    ctx.arc(70, yOffset + 10, 8, 0, Math.PI * 2)
    ctx.fill()

    // Step text
    ctx.fillStyle = '#f9fafb'
    ctx.font = '16px Arial'
    ctx.fillText(`${index + 1}. ${step.name}`, 100, yOffset + 15)

    // Tools used
    if (step.toolsCalled && step.toolsCalled.length > 0) {
      ctx.fillStyle = '#9ca3af'
      ctx.font = '12px Arial'
      ctx.fillText(`Tools: ${step.toolsCalled.join(', ')}`, 120, yOffset + 35)
    }

    yOffset += 60
  })

  // Business impact
  if (data.businessImpact) {
    ctx.fillStyle = '#10b981'
    ctx.font = 'bold 20px Arial'
    ctx.fillText('Business Impact', 50, yOffset + 50)
    
    ctx.fillStyle = '#f9fafb'
    ctx.font = '16px Arial'
    ctx.fillText(`Cost Saved: ₹${data.businessImpact.costSaved?.toLocaleString() || '0'}`, 50, yOffset + 80)
    ctx.fillText(`Time Reduced: ${data.businessImpact.timeReduced || 'N/A'}`, 50, yOffset + 105)
    ctx.fillText(`Accuracy: ${data.businessImpact.accuracy || 'N/A'}%`, 50, yOffset + 130)
  }

  const buffer = canvas.toBuffer('image/png')
  
  return new NextResponse(buffer, {
    headers: {
      'Content-Type': 'image/png',
      'Content-Length': buffer.length.toString(),
    },
  })
}

async function generateMetricsDashboardImage(data: any) {
  const canvas = createCanvas(1200, 800)
  const ctx = canvas.getContext('2d')

  // Background
  const gradient = ctx.createLinearGradient(0, 0, 1200, 800)
  gradient.addColorStop(0, '#0f172a')
  gradient.addColorStop(1, '#1e293b')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, 1200, 800)

  // Title
  ctx.fillStyle = '#f8fafc'
  ctx.font = 'bold 36px Arial'
  ctx.fillText('Agentic AI Dashboard', 50, 60)

  // Metrics grid
  const metrics = data.metrics || [
    { label: 'Autonomous Decisions', value: '87%', color: '#8b5cf6' },
    { label: 'Tool Executions', value: '2,398', color: '#3b82f6' },
    { label: 'Success Rate', value: '94%', color: '#10b981' },
    { label: 'Cost Savings', value: '₹8.4L', color: '#f59e0b' }
  ]

  let xOffset = 50
  let yOffset = 120

  metrics.forEach((metric: any, index: number) => {
    // Metric card background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.fillRect(xOffset, yOffset, 250, 150)

    // Metric value
    ctx.fillStyle = metric.color
    ctx.font = 'bold 48px Arial'
    ctx.fillText(metric.value, xOffset + 20, yOffset + 70)

    // Metric label
    ctx.fillStyle = '#cbd5e1'
    ctx.font = '16px Arial'
    ctx.fillText(metric.label, xOffset + 20, yOffset + 100)

    xOffset += 280
    if (index === 1) {
      xOffset = 50
      yOffset += 180
    }
  })

  // Performance chart
  ctx.strokeStyle = '#10b981'
  ctx.lineWidth = 3
  ctx.beginPath()
  
  const chartStartX = 50
  const chartStartY = 500
  const chartWidth = 500
  const chartHeight = 200

  // Chart background
  ctx.fillStyle = 'rgba(255, 255, 255, 0.05)'
  ctx.fillRect(chartStartX, chartStartY, chartWidth, chartHeight)

  // Sample data points
  const dataPoints = [20, 35, 45, 60, 75, 85, 90, 94]
  
  ctx.beginPath()
  ctx.moveTo(chartStartX, chartStartY + chartHeight)
  
  dataPoints.forEach((point, index) => {
    const x = chartStartX + (index * (chartWidth / (dataPoints.length - 1)))
    const y = chartStartY + chartHeight - (point / 100 * chartHeight)
    ctx.lineTo(x, y)
  })
  
  ctx.stroke()

  // Chart title
  ctx.fillStyle = '#f8fafc'
  ctx.font = 'bold 18px Arial'
  ctx.fillText('Automation Success Trend', chartStartX, chartStartY - 10)

  const buffer = canvas.toBuffer('image/png')
  
  return new NextResponse(buffer, {
    headers: {
      'Content-Type': 'image/png',
      'Content-Length': buffer.length.toString(),
    },
  })
}