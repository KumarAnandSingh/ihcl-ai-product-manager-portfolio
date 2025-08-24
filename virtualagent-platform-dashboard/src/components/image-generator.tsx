"use client"

import React, { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Download, Image as ImageIcon, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

interface ImageGeneratorProps {
  type: 'agent-status' | 'workflow-summary' | 'metrics-dashboard'
  data: any
  title?: string
  className?: string
}

export function ImageGenerator({ 
  type, 
  data, 
  title = "Generate Report Image",
  className 
}: ImageGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImage, setGeneratedImage] = useState<string | null>(null)

  const generateImage = useCallback(async () => {
    setIsGenerating(true)
    
    try {
      const response = await fetch('/api/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type, data }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate image')
      }

      const blob = await response.blob()
      const imageUrl = URL.createObjectURL(blob)
      setGeneratedImage(imageUrl)
      toast.success('Image generated successfully!')
    } catch (error) {
      console.error('Image generation failed:', error)
      toast.error('Failed to generate image')
    } finally {
      setIsGenerating(false)
    }
  }, [type, data])

  const downloadImage = useCallback(() => {
    if (!generatedImage) return

    const link = document.createElement('a')
    link.href = generatedImage
    link.download = `${type}-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success('Image downloaded!')
  }, [generatedImage, type])

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ImageIcon className="h-5 w-5" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Button 
            onClick={generateImage} 
            disabled={isGenerating}
            className="flex-1"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <ImageIcon className="h-4 w-4 mr-2" />
                Generate Image
              </>
            )}
          </Button>
          
          {generatedImage && (
            <Button 
              onClick={downloadImage}
              variant="outline"
              size="icon"
            >
              <Download className="h-4 w-4" />
            </Button>
          )}
        </div>

        {generatedImage && (
          <div className="space-y-2">
            <img 
              src={generatedImage} 
              alt="Generated report" 
              className="w-full rounded-lg border shadow-sm"
            />
            <p className="text-xs text-muted-foreground">
              Generated report image ready for download or sharing
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Specific generators for different use cases
export function AgentStatusImageGenerator({ agentData, className }: { 
  agentData: any
  className?: string 
}) {
  return (
    <ImageGenerator
      type="agent-status"
      data={agentData}
      title="Agent Status Report"
      className={className}
    />
  )
}

export function WorkflowSummaryImageGenerator({ workflowData, className }: { 
  workflowData: any
  className?: string 
}) {
  return (
    <ImageGenerator
      type="workflow-summary"
      data={workflowData}
      title="Workflow Summary Report"
      className={className}
    />
  )
}

export function MetricsDashboardImageGenerator({ metricsData, className }: { 
  metricsData: any
  className?: string 
}) {
  return (
    <ImageGenerator
      type="metrics-dashboard"
      data={metricsData}
      title="Dashboard Metrics Report"
      className={className}
    />
  )
}