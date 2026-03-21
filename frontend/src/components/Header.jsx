import React, { useState } from 'react'
import { Bell, Search, User, ChevronDown } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Header() {
  const [showNotifications, setShowNotifications] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    setShowProfile(false)
    navigate('/login')
  }

  return (
    <header className="bg-white border-b border-gray-200 px-4 sm:px-6 md:px-8 py-4">
      <div className="flex items-center justify-between">
        {/* Left Side - Search */}
        <div className="flex-1 max-w-md mr-4">
          <div className="relative hidden sm:block">
            <Search className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search..."
              className="input pl-10 w-full"
            />
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
            >
              <Bell size={22} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-xl z-50">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900">Notifications</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {[
                    { id: 1, message: 'New user Sarah Johnson joined', time: '5 min ago' },
                    { id: 2, message: 'Program "React Development" updated', time: '1 hour ago' },
                    { id: 3, message: 'Completion rate reached 78%', time: '3 hours ago' },
                  ].map((notif) => (
                    <div key={notif.id} className="px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer">
                      <p className="text-sm text-gray-900">{notif.message}</p>
                      <p className="text-xs text-gray-500 mt-1">{notif.time}</p>
                    </div>
                  ))}
                </div>
                <div className="p-3 border-t border-gray-200 text-center">
                  <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">View All</button>
                </div>
              </div>
            )}
          </div>

          {/* Profile Menu */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition"
            >
              <span className="text-2xl">👤</span>
              <div className="hidden sm:block text-left">
                <p className="text-sm font-medium text-gray-900">{user?.first_name || 'User'}</p>
                <p className="text-xs text-gray-500">Admin</p>
              </div>
              <ChevronDown size={18} className="text-gray-600" />
            </button>

            {showProfile && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-xl z-50">
                <div className="p-4 border-b border-gray-200">
                  <p className="text-sm font-semibold text-gray-900">{user?.first_name || 'User'}</p>
                  <p className="text-xs text-gray-600">{user?.email}</p>
                </div>
                <div className="py-2">
                  <a href="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    Profile Settings
                  </a>
                  <a href="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    Preferences
                  </a>
                </div>
                <div className="px-4 py-3 border-t border-gray-200">
                  <button
                    onClick={handleLogout}
                    className="w-full text-sm text-red-600 hover:text-red-700 font-medium text-left"
                  >
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
