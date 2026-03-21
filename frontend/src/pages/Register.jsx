import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState(0)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const passwordChecks = {
    minLength: formData.password.length >= 8,
    hasUpper: /[A-Z]/.test(formData.password),
    hasLower: /[a-z]/.test(formData.password),
    hasNumber: /\d/.test(formData.password),
    hasSpecial: /[!@#$%^&*]/.test(formData.password),
  }

  const calculatePasswordStrength = (password) => {
    let strength = 0
    if (password.length >= 8) strength++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[!@#$%^&*]/.test(password)) strength++
    return strength
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (name === 'password') {
      setPasswordStrength(calculatePasswordStrength(value))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirm_password,
        first_name: formData.first_name,
        last_name: formData.last_name,
      })
      navigate('/')
    } catch (err) {
      const detail = err?.detail
      if (Array.isArray(detail)) {
        const readable = detail
          .map((item) => item?.msg || item?.message || 'Validation error')
          .join(', ')
        setError(readable)
      } else if (typeof detail === 'string' && detail) {
        setError(detail)
      } else if (detail && typeof detail === 'object') {
        setError(detail.message || 'Registration failed')
      } else {
        setError(err?.message || 'Registration failed')
      }
    } finally {
      setLoading(false)
    }
  }

  const getPasswordStrengthColor = (strength) => {
    const colors = ['bg-gray-300', 'bg-red-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500']
    return colors[strength] || colors[0]
  }

  const getPasswordStrengthText = (strength) => {
    const texts = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
    return texts[strength] || 'Very Weak'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-600 to-green-800 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4">
            <span className="text-3xl font-bold bg-gradient-to-br from-green-600 to-green-800 bg-clip-text text-transparent">AI</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
          <p className="text-green-100">Join the AI Adaptive Onboarding Engine</p>
        </div>

        {/* Form Card */}
        <form onSubmit={handleSubmit} className="card bg-white rounded-2xl shadow-2xl p-8 space-y-5">
          {error && (
            <div className="flex items-center space-x-3 bg-red-50 border border-red-200 rounded-lg p-4">
              <AlertCircle className="text-red-600" size={20} />
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {/* Name Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                className="input"
                placeholder="John"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                className="input"
                placeholder="Doe"
                required
              />
            </div>
          </div>

          {/* Email Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="input pl-10"
                placeholder="you@example.com"
                required
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="input pl-10 pr-10"
                placeholder="••••••••"
                minLength={8}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {formData.password && (
              <div className="mt-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Password Strength</span>
                  <span className={`text-xs font-semibold ${
                    passwordStrength === 4 ? 'text-green-600' :
                    passwordStrength === 3 ? 'text-blue-600' :
                    passwordStrength === 2 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {getPasswordStrengthText(passwordStrength)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getPasswordStrengthColor(passwordStrength)}`}
                    style={{ width: `${(passwordStrength / 4) * 100}%` }}
                  />
                </div>
                <div className="mt-3 grid grid-cols-1 gap-1 text-xs">
                  <p className={passwordChecks.minLength ? 'text-green-600' : 'text-red-600'}>
                    {passwordChecks.minLength ? 'OK' : 'Required'}: at least 8 characters
                  </p>
                  <p className={passwordChecks.hasUpper ? 'text-green-600' : 'text-red-600'}>
                    {passwordChecks.hasUpper ? 'OK' : 'Required'}: one uppercase letter
                  </p>
                  <p className={passwordChecks.hasLower ? 'text-green-600' : 'text-red-600'}>
                    {passwordChecks.hasLower ? 'OK' : 'Required'}: one lowercase letter
                  </p>
                  <p className={passwordChecks.hasNumber ? 'text-green-600' : 'text-red-600'}>
                    {passwordChecks.hasNumber ? 'OK' : 'Required'}: one number
                  </p>
                  <p className={passwordChecks.hasSpecial ? 'text-green-600' : 'text-red-600'}>
                    {passwordChecks.hasSpecial ? 'OK' : 'Required'}: one special character (!@#$%^&*)
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleInputChange}
                className="input pl-10 pr-10"
                placeholder="••••••••"
                minLength={8}
                required
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {formData.confirm_password && formData.password === formData.confirm_password && (
              <div className="flex items-center space-x-2 mt-2 text-green-600">
                <CheckCircle size={16} />
                <span className="text-xs font-medium">Passwords match</span>
              </div>
            )}
          </div>

          {/* Register Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 font-semibold bg-green-600 hover:bg-green-700 active:bg-green-800"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>

          {/* Login Link */}
          <p className="text-center text-gray-600 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-green-600 font-semibold hover:text-green-700">
              Login
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
