import React, { useState } from 'react'
import { Plus, Search, Download, Edit2, Trash2, Eye, UserX, UserCheck } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'

export default function Users() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterRole, setFilterRole] = useState('all')

  const [users] = useState([
    {
      id: 1,
      name: 'Sarah Johnson',
      email: 'sarah@example.com',
      role: 'admin',
      department: 'Engineering',
      status: 'active',
      joinDate: '2024-01-15',
      completionRate: 92,
      avatar: '👩‍💼',
    },
    {
      id: 2,
      name: 'Mike Chen',
      email: 'mike@example.com',
      role: 'manager',
      department: 'Product',
      status: 'active',
      joinDate: '2024-02-20',
      completionRate: 78,
      avatar: '👨‍💼',
    },
    {
      id: 3,
      name: 'Emily Davis',
      email: 'emily@example.com',
      role: 'user',
      department: 'Marketing',
      status: 'active',
      joinDate: '2024-03-10',
      completionRate: 85,
      avatar: '👩‍💻',
    },
    {
      id: 4,
      name: 'James Wilson',
      email: 'james@example.com',
      role: 'user',
      department: 'Sales',
      status: 'inactive',
      joinDate: '2024-01-05',
      completionRate: 45,
      avatar: '👨‍💻',
    },
    {
      id: 5,
      name: 'Lisa Brown',
      email: 'lisa@example.com',
      role: 'manager',
      department: 'Engineering',
      status: 'active',
      joinDate: '2024-02-01',
      completionRate: 88,
      avatar: '👩‍🔬',
    },
    {
      id: 6,
      name: 'David Kumar',
      email: 'david@example.com',
      role: 'user',
      department: 'Engineering',
      status: 'active',
      joinDate: '2024-03-15',
      completionRate: 72,
      avatar: '👨‍🔬',
    },
  ])

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterRole === 'all' || user.role === filterRole
    return matchesSearch && matchesFilter
  })

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800'
      case 'manager': return 'bg-blue-100 text-blue-800'
      case 'user': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status) => {
    return status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
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
              <h1 className="text-3xl font-bold text-gray-900">Users</h1>
              <p className="text-gray-600 mt-2">Manage user accounts and permissions</p>
            </div>

            {/* Controls */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Search users..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input pl-10 w-full"
                />
              </div>

              {/* Filter */}
              <select
                value={filterRole}
                onChange={(e) => setFilterRole(e.target.value)}
                className="input px-4 py-2"
              >
                <option value="all">All Roles</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="user">User</option>
              </select>

              {/* Action Buttons */}
              <button className="btn-secondary px-6 py-2 inline-flex items-center space-x-2 whitespace-nowrap">
                <Download size={20} />
                <span>Export</span>
              </button>
              <button className="btn-primary px-6 py-2 inline-flex items-center space-x-2 whitespace-nowrap">
                <Plus size={20} />
                <span>Add User</span>
              </button>
            </div>

            {/* Table */}
            <div className="card rounded-lg shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200">
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">User</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Email</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Role</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Department</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Completion</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className="border-b border-gray-200 hover:bg-gray-50 transition">
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-3">
                            <span className="text-2xl">{user.avatar}</span>
                            <div>
                              <p className="font-medium text-gray-900">{user.name}</p>
                              <p className="text-sm text-gray-600">{user.joinDate}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-gray-600">{user.email}</td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${getRoleColor(user.role)}`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">{user.department}</td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${getStatusColor(user.status)}`}>
                            {user.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <div className="w-24 h-2 bg-gray-200 rounded-full">
                              <div
                                className="h-2 bg-green-500 rounded-full"
                                style={{ width: `${user.completionRate}%` }}
                              />
                            </div>
                            <span className="text-sm font-semibold text-gray-900">{user.completionRate}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <button className="p-2 text-gray-600 hover:bg-gray-100 rounded transition" title="View">
                              <Eye size={18} />
                            </button>
                            <button className="p-2 text-gray-600 hover:bg-gray-100 rounded transition" title="Edit">
                              <Edit2 size={18} />
                            </button>
                            <button className="p-2 text-gray-600 hover:bg-red-100 hover:text-red-600 rounded transition" title="Delete">
                              <Trash2 size={18} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-gray-600">Showing {filteredUsers.length} of {users.length} users</p>
              <div className="flex space-x-2">
                <button className="btn-secondary px-4 py-2 rounded text-sm">Previous</button>
                <button className="bg-blue-600 text-white px-4 py-2 rounded text-sm">1</button>
                <button className="btn-secondary px-4 py-2 rounded text-sm">2</button>
                <button className="btn-secondary px-4 py-2 rounded text-sm">Next</button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
