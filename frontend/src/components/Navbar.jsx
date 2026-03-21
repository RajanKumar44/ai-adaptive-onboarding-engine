import React from 'react'
import { Menu, LogOut, Home, FileText, User, BarChart3, MessageSquare } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = React.useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <span className="hidden sm:inline font-bold text-lg text-gray-900">Onboarding</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 transition-colors">
              <Home size={20} />
              <span>Dashboard</span>
            </Link>
            <Link to="/analyze" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 transition-colors">
              <FileText size={20} />
              <span>Analyze</span>
            </Link>
            {user?.role === 'admin' && (
              <Link to="/admin" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 transition-colors">
                <BarChart3 size={20} />
                <span>Admin</span>
              </Link>
            )}
            {user?.role === 'admin' && (
              <Link to="/admin/feedback" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 transition-colors">
                <MessageSquare size={20} />
                <span>Feedback</span>
              </Link>
            )}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <Link to="/profile" className="hidden sm:flex items-center space-x-2 text-gray-700 hover:text-blue-600 px-3 py-2 rounded-lg hover:bg-gray-100 transition-all">
              <User size={20} />
              <span className="text-sm font-medium">{user?.email?.split('@')[0]}</span>
            </Link>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-red-600 hover:bg-red-50 px-3 py-2 rounded-lg transition-all"
            >
              <LogOut size={20} />
              <span className="hidden sm:inline text-sm font-medium">Logout</span>
            </button>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden p-2"
            >
              <Menu size={24} />
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden pb-4 space-y-2 border-t">
            <Link to="/" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              Dashboard
            </Link>
            <Link to="/analyze" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              Analyze
            </Link>
            {user?.role === 'admin' && (
              <Link to="/admin" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                Admin
              </Link>
            )}
            {user?.role === 'admin' && (
              <Link to="/admin/feedback" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                Feedback Analytics
              </Link>
            )}
            <Link to="/profile" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              Profile
            </Link>
          </div>
        )}
      </div>
    </nav>
  )
}
