import React, { useState, useEffect } from 'react'
import { Plus, Search, Download, Edit2, Trash2, Eye } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { adminAPI } from '../api/client'

export default function Users() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterRole, setFilterRole] = useState('all')
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState({})
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true)
      setError('')
      try {
        const params = {
          limit: 100,
          ...(searchQuery ? { search: searchQuery } : {}),
          ...(filterRole !== 'all' ? { filter_role: filterRole } : {}),
        }
        const response = await adminAPI.listUsers(params)
        setUsers(response.data?.data || [])
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load users. Admin access may be required.')
      } finally {
        setLoading(false)
      }
    }

    const timeout = setTimeout(fetchUsers, 300)
    return () => clearTimeout(timeout)
  }, [searchQuery, filterRole])

  const filteredUsers = users

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800'
      case 'user': return 'bg-gray-100 text-gray-800'
      case 'guest': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status) => {
    return status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
  }

  const getAvatar = (name = '') => {
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join('') || 'U'
  }

  const exportUsers = () => {
    const header = ['id', 'name', 'email', 'role', 'status', 'created_at']
    const rows = filteredUsers.map((user) => [
      user.id,
      user.name || '',
      user.email || '',
      user.role || '',
      user.is_active ? 'active' : 'inactive',
      user.created_at || '',
    ])
    const csv = [header, ...rows]
      .map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(','))
      .join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'users-export.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const withActionLoading = async (userId, action) => {
    setActionLoading((prev) => ({ ...prev, [userId]: true }))
    setError('')
    try {
      await action()
      const response = await adminAPI.listUsers({ limit: 100 })
      setUsers(response.data?.data || [])
    } catch (err) {
      setError(err?.response?.data?.detail || 'Action failed')
    } finally {
      setActionLoading((prev) => ({ ...prev, [userId]: false }))
    }
  }

  const handleRoleToggle = async (user) => {
    const nextRole = user.role === 'admin' ? 'user' : 'admin'
    await withActionLoading(user.id, () => adminAPI.updateUserRole(user.id, nextRole))
  }

  const handleStatusToggle = async (user) => {
    if (user.is_active) {
      await withActionLoading(user.id, () => adminAPI.deactivateUser(user.id))
      return
    }
    await withActionLoading(user.id, () => adminAPI.activateUser(user.id))
  }

  const handleDelete = async (user) => {
    const confirmed = window.confirm(`Delete user ${user.email}? This cannot be undone.`)
    if (!confirmed) {
      return
    }
    await withActionLoading(user.id, () => adminAPI.deleteUser(user.id))
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
                <option value="user">User</option>
                <option value="guest">Guest</option>
              </select>

              {/* Action Buttons */}
              <button onClick={exportUsers} className="btn-secondary px-6 py-2 inline-flex items-center space-x-2 whitespace-nowrap">
                <Download size={20} />
                <span>Export</span>
              </button>
              <button onClick={() => navigate('/register')} className="btn-primary px-6 py-2 inline-flex items-center space-x-2 whitespace-nowrap">
                <Plus size={20} />
                <span>Add User</span>
              </button>
            </div>

            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

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
                            <span className="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-semibold">
                              {getAvatar(user.name)}
                            </span>
                            <div>
                              <p className="font-medium text-gray-900">{user.name || 'Unnamed User'}</p>
                              <p className="text-sm text-gray-600">{(user.created_at || '').slice(0, 10)}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-gray-600">{user.email}</td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${getRoleColor(user.role)}`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">-</td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${getStatusColor(user.is_active ? 'active' : 'inactive')}`}>
                            {user.is_active ? 'active' : 'inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <div className="w-24 h-2 bg-gray-200 rounded-full">
                              <div
                                className="h-2 bg-green-500 rounded-full"
                                style={{ width: `${Math.min((user.analyses_count || 0) * 10, 100)}%` }}
                              />
                            </div>
                            <span className="text-sm font-semibold text-gray-900">{Math.min((user.analyses_count || 0) * 10, 100)}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => window.alert(`User: ${user.name || 'Unnamed'}\nEmail: ${user.email}\nRole: ${user.role}\nAnalyses: ${user.analyses_count || 0}`)}
                              className="p-2 text-gray-600 hover:bg-gray-100 rounded transition"
                              title="View"
                              disabled={actionLoading[user.id]}
                            >
                              <Eye size={18} />
                            </button>
                            <button
                              onClick={() => handleRoleToggle(user)}
                              className="p-2 text-gray-600 hover:bg-gray-100 rounded transition"
                              title="Toggle Admin/User"
                              disabled={actionLoading[user.id]}
                            >
                              <Edit2 size={18} />
                            </button>
                            <button
                              onClick={() => (user.role === 'admin' ? handleStatusToggle(user) : handleDelete(user))}
                              className="p-2 text-gray-600 hover:bg-red-100 hover:text-red-600 rounded transition"
                              title={user.role === 'admin' ? (user.is_active ? 'Deactivate' : 'Activate') : 'Delete'}
                              disabled={actionLoading[user.id]}
                            >
                              <Trash2 size={18} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {loading && (
                <div className="px-6 py-5 text-sm text-gray-600 border-t border-gray-200">Loading users...</div>
              )}
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
