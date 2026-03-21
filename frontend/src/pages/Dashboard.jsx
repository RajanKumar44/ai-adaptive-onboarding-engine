import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Users, Award, Zap, Activity } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import StatCard from '../components/StatCard'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { fetchReportingSnapshot } from '../utils/reporting'

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [scopeLabel, setScopeLabel] = useState('your')
  const [stats, setStats] = useState({
    activeUsers: 0,
    completedOnboardings: 0,
    avgCompletionTime: '0h',
    satisfactionScore: 0,
  })

  const [chartData, setChartData] = useState([])

  const [skillsData, setSkillsData] = useState([{ name: 'No Data', value: 100, color: '#94a3b8' }])
  const [recentActivities, setRecentActivities] = useState([])

  useEffect(() => {
    const loadDashboard = async () => {
      if (!user?.id) return
      setLoading(true)
      setError('')

      try {
        const snapshot = await fetchReportingSnapshot(user)
        setScopeLabel(snapshot.scopeLabel)
        setStats({
          activeUsers: snapshot.stats.activeUsers,
          completedOnboardings: snapshot.stats.completions,
          avgCompletionTime: `${snapshot.stats.avgTimeHours}h`,
          satisfactionScore: snapshot.stats.satisfactionScore,
        })
        setChartData(snapshot.monthlyTrend)
        setSkillsData(snapshot.skillsDistribution)
        setRecentActivities(snapshot.recentActivities)
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load dashboard data from the database')
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()
  }, [user])

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            {/* Welcome Section */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.name || user?.email?.split('@')[0] || 'User'}!</h1>
              <p className="text-gray-600 mt-2">Here is what is happening with {scopeLabel} onboarding data from the database</p>
            </div>

            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {loading && (
              <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm">
                Loading latest data...
              </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Active Users"
                value={stats.activeUsers}
                icon={<Users className="text-blue-600" />}
                change={12}
                trend="up"
              />
              <StatCard
                title="Completions"
                value={stats.completedOnboardings}
                icon={<Award className="text-green-600" />}
                change={8}
                trend="up"
              />
              <StatCard
                title="Avg. Time"
                value={stats.avgCompletionTime}
                icon={<Zap className="text-yellow-600" />}
                change={-5}
                trend="down"
              />
              <StatCard
                title="Satisfaction"
                value={`${stats.satisfactionScore}%`}
                icon={<Activity className="text-purple-600" />}
                change={2}
                trend="up"
              />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              {/* Line Chart */}
              <div className="lg:col-span-2 card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Activity Trend</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="users" stroke="#3b82f6" name="Active Users" />
                    <Line type="monotone" dataKey="completions" stroke="#10b981" name="Completions" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Pie Chart */}
              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Skills Distribution</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={skillsData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {skillsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {skillsData.map((skill, index) => (
                    <div key={`${skill.name}-${index}`} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2 text-gray-700">
                        <span className="w-3 h-3 rounded-full" style={{ backgroundColor: skill.color }} />
                        <span>{skill.name}</span>
                      </div>
                      <span className="font-semibold text-gray-900">{skill.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Activities */}
              <div className="lg:col-span-2 card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activities</h2>
                <div className="space-y-4">
                  {recentActivities.length === 0 && (
                    <div className="p-4 border border-gray-200 rounded-lg text-sm text-gray-600">
                      No recent activity found in the database yet.
                    </div>
                  )}
                  {recentActivities.map((activity) => (
                    <div key={activity.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
                      <div className="flex items-center space-x-4">
                        <div className={`w-2 h-2 rounded-full ${
                          activity.type === 'completion' ? 'bg-green-500' :
                          activity.type === 'achievement' ? 'bg-blue-500' :
                          'bg-yellow-500'
                        }`} />
                        <div>
                          <p className="font-medium text-gray-900">{activity.user}</p>
                          <p className="text-sm text-gray-600">{activity.action}</p>
                        </div>
                      </div>
                      <span className="text-sm text-gray-500">{activity.time}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
                <div className="space-y-3">
                  <button onClick={() => navigate('/analyze')} className="w-full btn-primary py-3 rounded-lg text-center font-semibold">
                    Start New Program
                  </button>
                  <button onClick={() => navigate('/analytics')} className="w-full btn-secondary py-3 rounded-lg text-center font-semibold">
                    View Reports
                  </button>
                  {user?.role === 'admin' && (
                    <button onClick={() => navigate('/users')} className="w-full btn-secondary py-3 rounded-lg text-center font-semibold">
                      Manage Users
                    </button>
                  )}
                  <button onClick={() => navigate('/settings')} className="w-full btn-secondary py-3 rounded-lg text-center font-semibold">
                    Settings
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
