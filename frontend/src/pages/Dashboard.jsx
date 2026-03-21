import React, { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, Users, Award, Zap, Activity, ArrowUpRight, ArrowDownLeft } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import StatCard from '../components/StatCard'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    activeUsers: 1250,
    completedOnboardings: 892,
    avgCompletionTime: '4.5 hours',
    satisfactionScore: 92,
  })

  const [chartData, setChartData] = useState([
    { month: 'Jan', users: 400, completions: 240 },
    { month: 'Feb', users: 500, completions: 321 },
    { month: 'Mar', users: 600, completions: 429 },
    { month: 'Apr', users: 750, completions: 580 },
    { month: 'May', users: 900, completions: 720 },
    { month: 'Jun', users: 1250, completions: 892 },
  ])

  const [skillsData] = useState([
    { name: 'Python', value: 28, color: '#3b82f6' },
    { name: 'JavaScript', value: 24, color: '#10b981' },
    { name: 'React', value: 22, color: '#f59e0b' },
    { name: 'SQL', value: 15, color: '#ef4444' },
    { name: 'Others', value: 11, color: '#8b5cf6' },
  ])

  const [recentActivities] = useState([
    { id: 1, user: 'Sarah Johnson', action: 'Completed React Module', time: '2 hours ago', type: 'completion' },
    { id: 2, user: 'Mike Chen', action: 'Started Python Course', time: '4 hours ago', type: 'start' },
    { id: 3, user: 'Emily Davis', action: 'Achieved 95% Score', time: '6 hours ago', type: 'achievement' },
    { id: 4, user: 'James Wilson', action: 'Completed Full Onboarding', time: '1 day ago', type: 'completion' },
  ])

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            {/* Welcome Section */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.first_name || 'User'}!</h1>
              <p className="text-gray-600 mt-2">Here's what's happening with your onboarding program today</p>
            </div>

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
                      label={({ name, value }) => `${name}: ${value}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {skillsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Bottom Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Activities */}
              <div className="lg:col-span-2 card rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activities</h2>
                <div className="space-y-4">
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
                  <button onClick={() => navigate('/users')} className="w-full btn-secondary py-3 rounded-lg text-center font-semibold">
                    Manage Users
                  </button>
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
