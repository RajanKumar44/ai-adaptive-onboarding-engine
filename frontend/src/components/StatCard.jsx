import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function StatCard({ title, value, icon, change, trend }) {
  const isPositive = trend === 'up'

  return (
    <div className="card bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gray-100">
          {icon}
        </div>
        <div className={`flex items-center space-x-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
          {isPositive ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
          <span className="text-sm font-semibold">{Math.abs(change)}%</span>
        </div>
      </div>

      <div className="mb-2">
        <p className="text-gray-600 text-sm font-medium">{title}</p>
        <p className="text-3xl font-bold text-gray-900">{value.toLocaleString ? value.toLocaleString() : value}</p>
      </div>

      <p className={`text-xs ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? '↑' : '↓'} {Math.abs(change)}% from last month
      </p>
    </div>
  )
}
