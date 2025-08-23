"use client"

import { Bar, BarChart, Line, LineChart, ResponsiveContainer, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts'
import { analyticsData } from '@/lib/mock-data'

export function OverviewCharts() {
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={analyticsData.conversationTrends}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <XAxis 
            dataKey="month" 
            stroke="#888888"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#888888"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => `${value}`}
          />
          <Tooltip 
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="rounded-lg border bg-background p-3 shadow-lg">
                    <div className="font-medium mb-2">{label}</div>
                    <div className="space-y-1">
                      {payload.map((entry, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: entry.color }}
                          />
                          <span className="text-sm">
                            {entry.dataKey === 'conversations' ? 'Total Conversations' : 'Resolved'}:
                          </span>
                          <span className="font-bold">
                            {entry.value?.toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              }
              return null
            }}
          />
          <Line
            type="monotone"
            dataKey="conversations"
            stroke="hsl(221.2 83.2% 53.3%)"
            strokeWidth={3}
            dot={{ r: 4, fill: "hsl(221.2 83.2% 53.3%)" }}
            activeDot={{
              r: 6,
              fill: "hsl(221.2 83.2% 53.3%)",
              stroke: "hsl(221.2 83.2% 53.3%)"
            }}
          />
          <Line
            type="monotone"
            dataKey="resolved"
            stroke="hsl(142 76% 36%)"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 3, fill: "hsl(142 76% 36%)" }}
            activeDot={{
              r: 5,
              fill: "hsl(142 76% 36%)",
              stroke: "hsl(142 76% 36%)"
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}