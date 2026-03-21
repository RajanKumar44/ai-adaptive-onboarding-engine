import React, { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Download, Filter } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import StatCard from '../components/StatCard'
import { useAuth } from '../context/AuthContext'
import { fetchReportingSnapshot } from '../utils/reporting'

export default function Analytics() {
  const { user } = useAuth()
  const [dateRange, setDateRange] = useState('30days')
  const [metricsStatus, setMetricsStatus] = useState('healthy')
  const [error, setError] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [scopeLabel, setScopeLabel] = useState('your')
  const [engagementData, setEngagementData] = useState([])
  const [performanceData, setPerformanceData] = useState([])
  const [progressData, setProgressData] = useState([])
  const [topPerformers, setTopPerformers] = useState([])
  const [completionStatus, setCompletionStatus] = useState([
    { label: 'Completed', value: 0, color: 'bg-green-500' },
    { label: 'In Progress', value: 0, color: 'bg-yellow-500' },
    { label: 'Not Started', value: 100, color: 'bg-gray-400' },
  ])

  useEffect(() => {
    const loadMetrics = async () => {
      if (!user?.id) return
      setLoading(true)
      setError('')
      try {
        const snapshot = await fetchReportingSnapshot(user)
        setMetricsStatus('healthy')
        setScopeLabel(snapshot.scopeLabel)
        setSummary(snapshot.stats)
        setEngagementData(snapshot.engagementData)
        setPerformanceData(snapshot.performanceData)
        setProgressData(snapshot.progressData)
        setTopPerformers(snapshot.topPerformers)
        setCompletionStatus(snapshot.completionStatus)
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to fetch analytics metrics')
      } finally {
        setLoading(false)
      }
    }

    loadMetrics()
  }, [dateRange, user])

  const exportReport = () => {
    const report = {
      generatedAt: new Date().toISOString(),
      dateRange,
      scopeLabel,
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
                  <p className="text-gray-600 mt-2">Comprehensive insights from {scopeLabel} real onboarding data</p>
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

              {loading && (
                <div className="mb-4 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm">
                  Loading latest analytics from the database...
                </div>
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
                value={summary?.totalUsers ?? 0}
                icon={<span className="text-2xl">👥</span>}
                change={12}
                trend="up"
              />
              <StatCard
                title="Avg. Score"
                value={summary?.avgMatchPercentage ?? 0}
                icon={<span className="text-2xl">⭐</span>}
                change={5}
                trend="up"
              />
              <StatCard
                title="Completion Rate"
                value={`${summary?.completionRate ?? 0}%`}
                icon={<span className="text-2xl">✅</span>}
                change={8}
                trend="up"
              />
              <StatCard
                title="Avg. Time/Course"
                value={`${summary?.avgTimeHours ?? 0}h`}
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
                  {topPerformers.length === 0 && (
                    <div className="p-3 border border-gray-200 rounded-lg text-sm text-gray-600">
                      No performer data available yet.
                    </div>
                  )}
                  {topPerformers.map((user) => (
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
                  {completionStatus.map((status, index) => (
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
