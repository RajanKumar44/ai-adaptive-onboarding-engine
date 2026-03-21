import React, { useState } from 'react'
import { Plus, Search, Filter, BookOpen, Users, Clock, TrendingUp } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'

export default function Programs() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const navigate = useNavigate()

  const [programs] = useState([
    {
      id: 1,
      name: 'Python Basics',
      description: 'Learn Python fundamentals for beginners',
      icon: '🐍',
      status: 'active',
      enrolledUsers: 245,
      completionRate: 78,
      duration: '4 weeks',
      modules: 8,
    },
    {
      id: 2,
      name: 'React Development',
      description: 'Master React and modern JavaScript frameworks',
      icon: '⚛️',
      status: 'active',
      enrolledUsers: 189,
      completionRate: 65,
      duration: '6 weeks',
      modules: 12,
    },
    {
      id: 3,
      name: 'Database Design',
      description: 'SQL and database architecture fundamentals',
      icon: '🗄️',
      status: 'active',
      enrolledUsers: 156,
      completionRate: 82,
      duration: '3 weeks',
      modules: 6,
    },
    {
      id: 4,
      name: 'Cloud Computing',
      description: 'AWS and cloud infrastructure essentials',
      icon: '☁️',
      status: 'draft',
      enrolledUsers: 0,
      completionRate: 0,
      duration: '5 weeks',
      modules: 10,
    },
    {
      id: 5,
      name: 'Machine Learning',
      description: 'Introduction to ML and AI concepts',
      icon: '🤖',
      status: 'active',
      enrolledUsers: 98,
      completionRate: 45,
      duration: '8 weeks',
      modules: 15,
    },
    {
      id: 6,
      name: 'DevOps Essentials',
      description: 'CI/CD pipelines and deployment strategies',
      icon: '🔧',
      status: 'archived',
      enrolledUsers: 67,
      completionRate: 100,
      duration: '4 weeks',
      modules: 7,
    },
  ])

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
              <p className="text-gray-600 mt-2">Create and manage onboarding programs for your organization</p>
            </div>

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
