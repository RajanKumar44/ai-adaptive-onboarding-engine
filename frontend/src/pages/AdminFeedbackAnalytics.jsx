import React, { useEffect, useMemo, useState } from 'react'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from 'recharts'
import { MessageSquare, TrendingUp, Star, Clock3 } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { adminAPI } from '../api/client'

export default function AdminFeedbackAnalytics() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [summary, setSummary] = useState({
    response_count: 0,
    average_rating: 0,
    weighted_average_rating: 0,
    weighted_satisfaction_percent: 0,
    half_life_days: 45,
  })
  const [trend, setTrend] = useState([])
  const [programAverages, setProgramAverages] = useState([])

  useEffect(() => {
    const loadAnalytics = async () => {
      setLoading(true)
      setError('')

      try {
        const response = await adminAPI.getFeedbackAnalytics({ months: 6 })
        setSummary(response?.data?.summary || {})
        setTrend(response?.data?.trend || [])
        setProgramAverages(response?.data?.per_program_average || [])
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load feedback analytics.')
      } finally {
        setLoading(false)
      }
    }

    loadAnalytics()
  }, [])

  const topPrograms = useMemo(() => programAverages.slice(0, 10), [programAverages])

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900">Feedback Analytics</h1>
            <p className="text-gray-600 mt-2">Track response volume, weighted trend, and per-program satisfaction.</p>

            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {loading && (
              <div className="mt-6 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm">
                Loading feedback analytics...
              </div>
            )}

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              <div className="card rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-600">Responses</p>
                  <MessageSquare className="text-blue-600" size={18} />
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-2">{summary.response_count || 0}</p>
              </div>

              <div className="card rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-600">Weighted Satisfaction</p>
                  <TrendingUp className="text-green-600" size={18} />
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-2">{summary.weighted_satisfaction_percent || 0}%</p>
              </div>

              <div className="card rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-600">Weighted Avg Rating</p>
                  <Star className="text-yellow-500" size={18} />
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-2">{summary.weighted_average_rating || 0}/5</p>
              </div>

              <div className="card rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-600">Recency Half-Life</p>
                  <Clock3 className="text-indigo-600" size={18} />
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-2">{summary.half_life_days || 45} days</p>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 xl:grid-cols-3 gap-6">
              <div className="xl:col-span-2 card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Feedback Trend</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis yAxisId="left" domain={[0, 5]} />
                    <YAxis yAxisId="right" orientation="right" allowDecimals={false} />
                    <Tooltip />
                    <Line yAxisId="left" type="monotone" dataKey="average_rating" name="Avg Rating" stroke="#3b82f6" strokeWidth={2} />
                    <Line yAxisId="left" type="monotone" dataKey="weighted_average_rating" name="Weighted Avg Rating" stroke="#10b981" strokeWidth={2} />
                    <Line yAxisId="right" type="monotone" dataKey="responses" name="Responses" stroke="#f59e0b" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Program Averages</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topPrograms} layout="vertical" margin={{ top: 0, right: 12, left: 36, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis type="category" dataKey="program" width={100} />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Bar dataKey="weighted_satisfaction_percent" name="Weighted Satisfaction" fill="#6366f1" radius={[4, 4, 4, 4]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="mt-6 card rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Per-Program Detail</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 text-left text-gray-600">
                      <th className="py-2 pr-4">Program</th>
                      <th className="py-2 pr-4">Responses</th>
                      <th className="py-2 pr-4">Avg Rating</th>
                      <th className="py-2 pr-4">Weighted Avg</th>
                      <th className="py-2 pr-4">Weighted Satisfaction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {programAverages.length === 0 && (
                      <tr>
                        <td colSpan={5} className="py-4 text-gray-500">No feedback responses available yet.</td>
                      </tr>
                    )}
                    {programAverages.map((item) => (
                      <tr key={item.program} className="border-b border-gray-100">
                        <td className="py-2 pr-4 font-medium text-gray-900">{item.program}</td>
                        <td className="py-2 pr-4 text-gray-700">{item.responses}</td>
                        <td className="py-2 pr-4 text-gray-700">{item.average_rating}/5</td>
                        <td className="py-2 pr-4 text-gray-700">{item.weighted_average_rating}/5</td>
                        <td className="py-2 pr-4 text-gray-700">{item.weighted_satisfaction_percent}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
