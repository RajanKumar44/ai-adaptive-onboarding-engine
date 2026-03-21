import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { adminAPI, metricsAPI } from '../api/client'

export default function AdminPanel() {
  const [users, setUsers] = useState([])
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const loadData = async () => {
      setError('')
      try {
        const [usersResponse, healthResponse] = await Promise.all([
          adminAPI.listUsers({ limit: 5 }),
          metricsAPI.getHealth(),
        ])
        setUsers(usersResponse?.data?.data || [])
        setStatus(healthResponse?.data?.status || 'unknown')
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load admin data. Ensure you are logged in as admin.')
      }
    }

    loadData()
  }, [])

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
            <p className="text-gray-600 mt-2">Administrative controls and user management are available here.</p>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">System Status</h2>
                <p className="text-sm text-gray-600 mb-4">Backend health endpoint</p>
                <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-50 text-blue-700 capitalize">
                  {status || 'unavailable'}
                </div>
                <div className="mt-4">
                  <button onClick={() => navigate('/analytics')} className="btn-secondary px-4 py-2 text-sm">View Full Metrics</button>
                </div>
              </div>

              <div className="card rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Recent Users</h2>
                <div className="space-y-3">
                  {users.length === 0 && <p className="text-sm text-gray-500">No users available.</p>}
                  {users.map((user) => (
                    <div key={user.id} className="flex items-center justify-between border border-gray-200 rounded-lg px-3 py-2">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{user.name || user.email}</p>
                        <p className="text-xs text-gray-600">{user.email}</p>
                      </div>
                      <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700 capitalize">{user.role}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-4">
                  <button onClick={() => navigate('/users')} className="btn-primary px-4 py-2 text-sm">Manage Users</button>
                </div>
              </div>
            </div>

            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
