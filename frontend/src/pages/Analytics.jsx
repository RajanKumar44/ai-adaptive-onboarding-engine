import React, { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Download, Calendar, Filter } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import StatCard from '../components/StatCard'
import { metricsAPI } from '../api/client'

export default function Analytics() {
  const [dateRange, setDateRange] = useState('30days')
  const [metricsStatus, setMetricsStatus] = useState('')
  const [error, setError] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [summary, setSummary] = useState(null)

  const engagementData = [
    { day: 'Mon', engagement: 65, sessions: 120 },
    { day: 'Tue', engagement: 72, sessions: 145 },
    { day: 'Wed', engagement: 78, sessions: 165 },
    { day: 'Thu', engagement: 68, sessions: 135 },
    { day: 'Fri', engagement: 82, sessions: 180 },
    { day: 'Sat', engagement: 55, sessions: 95 },
    { day: 'Sun', engagement: 48, sessions: 75 },
  ]

  const performanceData = [
    { program: 'Python', score: 85, target: 80 },
    { program: 'React', score: 78, target: 80 },
    { program: 'SQL', score: 92, target: 80 },
    { program: 'Cloud', score: 68, target: 80 },
    { program: 'ML', score: 75, target: 80 },
    { program: 'DevOps', score: 88, target: 80 },
  ]

  const progressData = [
    { name: 'Sarah', started: 45, completed: 92 },
    { name: 'Mike', started: 38, completed: 75 },
    { name: 'Emily', started: 52, completed: 88 },
    { name: 'James', started: 41, completed: 79 },
    { name: 'Lisa', started: 48, completed: 85 },
    { name: 'David', started: 35, completed: 68 },
  ]

  useEffect(() => {
    const loadMetrics = async () => {
      setError('')
      try {
        const [health, status] = await Promise.all([
          metricsAPI.getHealth(),
          metricsAPI.getPerformance().catch(() => null),
        ])
        setMetricsStatus(health?.data?.status || 'unknown')
        setSummary(status?.data || null)
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to fetch analytics metrics')
      }
    }

    loadMetrics()
  }, [dateRange])

  const exportReport = () => {
    const report = {
      generatedAt: new Date().toISOString(),
      dateRange,
      healthStatus: metricsStatus || 'unknown',
      engagementData,
      performanceData,
      progressData,
      backendSummary: summary,
    }
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `analytics-report-${dateRange}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            {/* Header with Controls */}
            <div className="mb-8">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
                  <p className="text-gray-600 mt-2">Comprehensive insights into your onboarding programs</p>
                </div>
                <button onClick={exportReport} className="mt-4 sm:mt-0 btn-secondary px-6 py-2 inline-flex items-center space-x-2">
                  <Download size={20} />
                  <span>Export Report</span>
                </button>
              </div>

              {metricsStatus && (
                <p className="text-sm text-gray-600 mb-4">
                  Backend metrics status: <span className="font-semibold capitalize">{metricsStatus}</span>
                </p>
              )}

              {error && (
                <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-4">
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="input px-4 py-2 flex-1 sm:flex-none"
                >
                  <option value="7days">Last 7 Days</option>
                  <option value="30days">Last 30 Days</option>
                  <option value="90days">Last 90 Days</option>
                  <option value="12months">Last 12 Months</option>
                </select>
                <button onClick={() => setShowFilters((prev) => !prev)} className="btn-secondary px-4 py-2 inline-flex items-center space-x-2">
                  <Filter size={20} />
                  <span>{showFilters ? 'Hide Filters' : 'More Filters'}</span>
                </button>
              </div>

              {showFilters && (
                <div className="mt-4 p-4 border border-gray-200 rounded-lg bg-white text-sm text-gray-700">
                  Additional filter controls can be expanded here for departments, roles, and program types.
                </div>
              )}
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Users"
                value={1250}
                icon={<span className="text-2xl">👥</span>}
                change={12}
                trend="up"
              />
              <StatCard
                title="Avg. Score"
                value={81}
                icon={<span className="text-2xl">⭐</span>}
                change={5}
                trend="up"
              />
              <StatCard
                title="Completion Rate"
                value="78%"
                icon={<span className="text-2xl">✅</span>}
                change={8}
                trend="up"
              />
              <StatCard
                title="Avg. Time/Course"
                value="4.2h"
                icon={<span className="text-2xl">⏱️</span>}
                change={-3}
                trend="down"
              />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Engagement Chart */}
              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Weekly Engagement</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={engagementData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="engagement" fill="#3b82f6" name="Engagement Score" />
                    <Bar dataKey="sessions" fill="#10b981" name="Active Sessions" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Performance Chart */}
              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Program Performance</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="program" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="score" fill="#3b82f6" name="Avg Score" />
                    <Bar dataKey="target" fill="#10b981" name="Target" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Progress Comparison */}
            <div className="card rounded-lg shadow-md p-6 mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-6">User Progress</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={progressData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="started" stroke="#f59e0b" name="Modules Started" />
                  <Line type="monotone" dataKey="completed" stroke="#10b981" name="Modules Completed" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Top Performers */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Top Performers</h2>
                <div className="space-y-4">
                  {[
                    { rank: 1, name: 'Sarah Johnson', score: 95, completed: 12 },
                    { rank: 2, name: 'Mike Chen', score: 92, completed: 10 },
                    { rank: 3, name: 'Emily Davis', score: 88, completed: 9 },
                    { rank: 4, name: 'James Wilson', score: 85, completed: 8 },
                    { rank: 5, name: 'Lisa Brown', score: 82, completed: 8 },
                  ].map((user) => (
                    <div key={user.rank} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-600">
                          #{user.rank}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{user.name}</p>
                          <p className="text-sm text-gray-600">{user.completed} modules completed</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-gray-900">{user.score}%</p>
                        <p className="text-xs text-green-600">+5%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Completion Status */}
              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Completion Status</h2>
                <div className="space-y-4">
                  {[
                    { label: 'Completed', value: 78, color: 'bg-green-500' },
                    { label: 'In Progress', value: 18, color: 'bg-yellow-500' },
                    { label: 'Not Started', value: 4, color: 'bg-gray-400' },
                  ].map((status, index) => (
                    <div key={index}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-700">{status.label}</span>
                        <span className="font-bold text-gray-900">{status.value}%</span>
                      </div>
                      <div className="w-full h-3 bg-gray-200 rounded-full">
                        <div
                          className={`h-3 rounded-full ${status.color}`}
                          style={{ width: `${status.value}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
