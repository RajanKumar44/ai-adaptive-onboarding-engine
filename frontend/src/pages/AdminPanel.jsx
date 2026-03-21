import React from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'

export default function AdminPanel() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
            <p className="text-gray-600 mt-2">Administrative controls and user management are available here.</p>
          </div>
        </main>
      </div>
    </div>
  )
}
