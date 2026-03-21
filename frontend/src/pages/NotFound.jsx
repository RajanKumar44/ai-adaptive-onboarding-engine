import React from 'react'
import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-gray-900">404</h1>
        <p className="text-gray-600 mt-2">The page you requested could not be found.</p>
        <Link to="/" className="inline-block mt-6 btn-primary px-5 py-2 rounded-lg">
          Go to Dashboard
        </Link>
      </div>
    </div>
  )
}
