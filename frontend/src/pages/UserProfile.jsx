import React from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { useAuth } from '../context/AuthContext'

export default function UserProfile() {
  const { user } = useAuth()

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
            <div className="card rounded-lg shadow-md p-6 mt-6 space-y-3">
              <p><span className="font-semibold">Name:</span> {user?.name || '-'}</p>
              <p><span className="font-semibold">Email:</span> {user?.email || '-'}</p>
              <p><span className="font-semibold">Role:</span> {user?.role || '-'}</p>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
