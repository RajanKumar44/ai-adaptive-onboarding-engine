import React, { useState, useEffect } from 'react'
import { Plus, Search, Filter, BookOpen, Users, Clock, TrendingUp } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { useAuth } from '../context/AuthContext'
import { fetchReportingSnapshot } from '../utils/reporting'

export default function Programs() {
  const { user } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [programs, setPrograms] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const loadPrograms = async () => {
      if (!user?.id) return
      setLoading(true)
      setError('')
      try {
        const snapshot = await fetchReportingSnapshot(user)
        const iconPool = ['🐍', '⚛️', '🗄️', '☁️', '🤖', '🔧', '📊', '🧪', '🧠', '⚙️']
        const usersByProgram = {}
        const statsByProgram = {}

        snapshot.allAnalyses.forEach((analysis) => {
          const userId = analysis.user_id
          const skills = Array.isArray(analysis.missing_skills) ? analysis.missing_skills : []
          skills.forEach((skill) => {
            const key = String(skill || '').trim()
            if (!key) return
            if (!usersByProgram[key]) usersByProgram[key] = new Set()
            if (!statsByProgram[key]) {
              statsByProgram[key] = { gapSum: 0, occurrences: 0 }
            }
            usersByProgram[key].add(userId)
            statsByProgram[key].gapSum += Number(analysis.missing_skills_count || 0)
            statsByProgram[key].occurrences += 1
          })
        })

        const generatedPrograms = Object.entries(statsByProgram)
          .sort((a, b) => b[1].occurrences - a[1].occurrences)
          .slice(0, 24)
          .map(([name, values], index) => {
            const enrolledUsers = usersByProgram[name]?.size || 0
            const avgGap = values.occurrences ? values.gapSum / values.occurrences : 0
            const completionRate = Math.max(0, Math.min(100, Math.round(100 - avgGap * 8)))
            const durationWeeks = Math.max(1, Math.round(avgGap / 2))
            const modules = Math.max(3, Math.round(avgGap) + 2)
            const status = enrolledUsers > 0 ? 'active' : 'draft'

            return {
              id: `${name}-${index}`,
              name,
              description: `Skill-development program generated from real analysis gaps for ${name}.`,
              icon: iconPool[index % iconPool.length],
              status,
              enrolledUsers,
              completionRate,
              duration: `${durationWeeks} weeks`,
              modules,
            }
          })

        setPrograms(generatedPrograms)
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load programs from the database')
      } finally {
        setLoading(false)
      }
    }

    loadPrograms()
  }, [user])

  const filteredPrograms = programs.filter(program => {
    const matchesSearch = program.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         program.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === 'all' || program.status === filterStatus
    return matchesSearch && matchesFilter
  })

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'draft': return 'bg-yellow-100 text-yellow-800'
      case 'archived': return 'bg-gray-100 text-gray-800'
      default: return 'bg-blue-100 text-blue-800'
    }
  }

  const getStatusBadge = (status) => {
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getStatusColor(status)}`}>
        {status}
      </span>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Onboarding Programs</h1>
              <p className="text-gray-600 mt-2">Programs generated from real skill-gap data in your database</p>
            </div>

            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {loading && (
              <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm">
                Loading programs...
              </div>
            )}

            {/* Controls */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Search programs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input pl-10 w-full"
                />
              </div>

              {/* Filter */}
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="input px-4 py-2"
              >
                <option value="all">All Programs</option>
                <option value="active">Active</option>
                <option value="draft">Draft</option>
                <option value="archived">Archived</option>
              </select>

              {/* Create Button */}
              <button onClick={() => navigate('/analyze')} className="btn-primary px-6 py-2 inline-flex items-center space-x-2 whitespace-nowrap">
                <Plus size={20} />
                <span>New Program</span>
              </button>
            </div>

            {/* Programs Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredPrograms.map((program) => (
                <div key={program.id} className="card rounded-lg shadow-md hover:shadow-lg transition overflow-hidden group cursor-pointer">
                  {/* Header */}
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 border-b border-gray-200">
                    <div className="flex items-start justify-between">
                      <span className="text-4xl">{program.icon}</span>
                      {getStatusBadge(program.status)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{program.name}</h3>
                    <p className="text-gray-600 text-sm mb-4">{program.description}</p>

                    {/* Stats */}
                    <div className="space-y-3 mb-4">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-2 text-gray-600">
                          <Users size={16} />
                          <span>Enrolled</span>
                        </div>
                        <span className="font-semibold text-gray-900">{program.enrolledUsers}</span>
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-2 text-gray-600">
                          <TrendingUp size={16} />
                          <span>Completion</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 h-2 bg-gray-200 rounded-full">
                            <div
                              className="h-2 bg-green-500 rounded-full"
                              style={{ width: `${program.completionRate}%` }}
                            />
                          </div>
                          <span className="font-semibold text-gray-900">{program.completionRate}%</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-2 text-gray-600">
                          <Clock size={16} />
                          <span>Duration</span>
                        </div>
                        <span className="font-semibold text-gray-900">{program.duration}</span>
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-2 text-gray-600">
                          <BookOpen size={16} />
                          <span>Modules</span>
                        </div>
                        <span className="font-semibold text-gray-900">{program.modules}</span>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-2 pt-4 border-t border-gray-200">
                      <button onClick={() => navigate('/analytics')} className="flex-1 btn-secondary py-2 rounded text-sm font-medium">
                        View
                      </button>
                      <button onClick={() => navigate('/analyze')} className="flex-1 btn-primary py-2 rounded text-sm font-medium">
                        Edit
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Empty State */}
            {filteredPrograms.length === 0 && (
              <div className="text-center py-12">
                <BookOpen className="mx-auto text-gray-400 mb-4" size={48} />
                <p className="text-gray-600 font-medium">No programs found</p>
                <p className="text-gray-500 text-sm">Try adjusting your search or filters</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
