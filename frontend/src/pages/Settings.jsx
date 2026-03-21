import React, { useState } from 'react'
import { Save, Eye, EyeOff, Bell, Lock, User, Building, Globe } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { useAuth } from '../context/AuthContext'

export default function Settings() {
  const { user, updateProfile, changePassword, refreshProfile } = useAuth()
  const [activeTab, setActiveTab] = useState('account')
  const [showPassword, setShowPassword] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [settings, setSettings] = useState({
    account: {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com',
      phone: '+1 (555) 123-4567',
      bio: 'Passionate about learning and development',
    },
    organization: {
      companyName: 'Tech Corp',
      industry: 'Technology',
      size: '101-500',
      website: 'https://techcorp.com',
    },
    notifications: {
      emailNotifications: true,
      programUpdates: true,
      userActivity: true,
      weeklyReport: true,
      dailyDigest: false,
    },
    security: {
      twoFactor: false,
      sessionTimeout: 30,
      loginAlerts: true,
    },
  })

  const tabs = [
    { id: 'account', label: 'Account', icon: User },
    { id: 'organization', label: 'Organization', icon: Building },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
  ]

  const handleInputChange = (section, field, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }))
  }

  const handleToggle = (section, field) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: !prev[section][field],
      },
    }))
  }

  const handleSave = () => {
    const save = async () => {
      setSaving(true)
      setError('')
      setMessage('')
      try {
        const fullName = `${settings.account.firstName} ${settings.account.lastName}`.trim()
        await updateProfile({
          name: fullName,
          email: settings.account.email,
        })
        await refreshProfile()
        setMessage('Settings saved successfully.')
      } catch (err) {
        setError(err?.detail || 'Failed to save settings')
      } finally {
        setSaving(false)
      }
    }

    save()
  }

  const handleChangePassword = async () => {
    setSaving(true)
    setError('')
    setMessage('')
    try {
      await changePassword(passwordForm)
      setMessage('Password changed successfully.')
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      setError(err?.detail || 'Failed to change password')
    } finally {
      setSaving(false)
    }
  }

  const ActiveIcon = tabs.find(tab => tab.id === activeTab)?.icon || User

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
              <p className="text-gray-600 mt-2">Manage your account and preferences</p>
            </div>

            {message && (
              <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
                {message}
              </div>
            )}

            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              {/* Sidebar Navigation */}
              <div className="lg:col-span-1">
                <nav className="space-y-2">
                  {tabs.map((tab) => {
                    const TabIcon = tab.icon
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                          activeTab === tab.id
                            ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-600'
                            : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        <TabIcon size={20} />
                        <span className="font-medium">{tab.label}</span>
                      </button>
                    )
                  })}
                </nav>
              </div>

              {/* Content */}
              <div className="lg:col-span-3">
                <div className="card rounded-lg shadow-md p-6">
                  {/* Account Settings */}
                  {activeTab === 'account' && (
                    <div className="space-y-6">
                      <div className="flex items-center space-x-4 pb-6 border-b border-gray-200">
                        <span className="text-5xl">👤</span>
                        <div>
                          <p className="text-lg font-semibold text-gray-900">Profile Picture</p>
                          <p className="text-sm text-gray-600">Change your avatar</p>
                        </div>
                        <button className="ml-auto btn-secondary px-4 py-2">Upload</button>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                          <input
                            type="text"
                            value={settings.account.firstName}
                            onChange={(e) => handleInputChange('account', 'firstName', e.target.value)}
                            className="input w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                          <input
                            type="text"
                            value={settings.account.lastName}
                            onChange={(e) => handleInputChange('account', 'lastName', e.target.value)}
                            className="input w-full"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                        <input
                          type="email"
                          value={settings.account.email}
                          onChange={(e) => handleInputChange('account', 'email', e.target.value)}
                          className="input w-full"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                        <input
                          type="tel"
                          value={settings.account.phone}
                          onChange={(e) => handleInputChange('account', 'phone', e.target.value)}
                          className="input w-full"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                        <textarea
                          value={settings.account.bio}
                          onChange={(e) => handleInputChange('account', 'bio', e.target.value)}
                          rows={4}
                          className="input w-full"
                        />
                      </div>
                    </div>
                  )}

                  {/* Organization Settings */}
                  {activeTab === 'organization' && (
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
                        <input
                          type="text"
                          value={settings.organization.companyName}
                          onChange={(e) => handleInputChange('organization', 'companyName', e.target.value)}
                          className="input w-full"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
                        <select
                          value={settings.organization.industry}
                          onChange={(e) => handleInputChange('organization', 'industry', e.target.value)}
                          className="input w-full"
                        >
                          <option>Technology</option>
                          <option>Finance</option>
                          <option>Healthcare</option>
                          <option>Retail</option>
                          <option>Manufacturing</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Company Size</label>
                        <select
                          value={settings.organization.size}
                          onChange={(e) => handleInputChange('organization', 'size', e.target.value)}
                          className="input w-full"
                        >
                          <option>1-10</option>
                          <option>11-50</option>
                          <option>51-100</option>
                          <option>101-500</option>
                          <option>500+</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Website</label>
                        <input
                          type="url"
                          value={settings.organization.website}
                          onChange={(e) => handleInputChange('organization', 'website', e.target.value)}
                          className="input w-full"
                        />
                      </div>
                    </div>
                  )}

                  {/* Notification Settings */}
                  {activeTab === 'notifications' && (
                    <div className="space-y-4">
                      {Object.entries(settings.notifications).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
                          <div>
                            <p className="font-medium text-gray-900 capitalize">
                              {key.replace(/([A-Z])/g, ' $1').trim()}
                            </p>
                            <p className="text-sm text-gray-600">
                              {key === 'emailNotifications' && 'Receive all notifications via email'}
                              {key === 'programUpdates' && 'Get notified about program changes'}
                              {key === 'userActivity' && 'Alerts about user activities'}
                              {key === 'weeklyReport' && 'Weekly summary report'}
                              {key === 'dailyDigest' && 'Daily activity digest'}
                            </p>
                          </div>
                          <button
                            onClick={() => handleToggle('notifications', key)}
                            className={`w-12 h-6 rounded-full transition ${
                              value ? 'bg-green-500' : 'bg-gray-300'
                            }`}
                          >
                            <div className={`w-5 h-5 rounded-full bg-white transition transform ${
                              value ? 'translate-x-6' : 'translate-x-0.5'
                            }`} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Security Settings */}
                  {activeTab === 'security' && (
                    <div className="space-y-6">
                      <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">Two-Factor Authentication</p>
                          <p className="text-sm text-gray-600">Add an extra layer of security</p>
                        </div>
                        <button
                          onClick={() => handleToggle('security', 'twoFactor')}
                          className={`w-12 h-6 rounded-full transition ${
                            settings.security.twoFactor ? 'bg-green-500' : 'bg-gray-300'
                          }`}
                        >
                          <div className={`w-5 h-5 rounded-full bg-white transition transform ${
                            settings.security.twoFactor ? 'translate-x-6' : 'translate-x-0.5'
                          }`} />
                        </button>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (minutes)</label>
                        <input
                          type="number"
                          value={settings.security.sessionTimeout}
                          onChange={(e) => handleInputChange('security', 'sessionTimeout', parseInt(e.target.value))}
                          className="input w-full"
                        />
                      </div>

                      <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">Login Alerts</p>
                          <p className="text-sm text-gray-600">Get notified of login attempts</p>
                        </div>
                        <button
                          onClick={() => handleToggle('security', 'loginAlerts')}
                          className={`w-12 h-6 rounded-full transition ${
                            settings.security.loginAlerts ? 'bg-green-500' : 'bg-gray-300'
                          }`}
                        >
                          <div className={`w-5 h-5 rounded-full bg-white transition transform ${
                            settings.security.loginAlerts ? 'translate-x-6' : 'translate-x-0.5'
                          }`} />
                        </button>
                      </div>

                      <div className="pt-4 border-t border-gray-200">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                          <input
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Current password"
                            value={passwordForm.old_password}
                            onChange={(e) => setPasswordForm((prev) => ({ ...prev, old_password: e.target.value }))}
                            className="input w-full"
                          />
                          <input
                            type={showPassword ? 'text' : 'password'}
                            placeholder="New password"
                            value={passwordForm.new_password}
                            onChange={(e) => setPasswordForm((prev) => ({ ...prev, new_password: e.target.value }))}
                            className="input w-full"
                          />
                          <input
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Confirm password"
                            value={passwordForm.confirm_password}
                            onChange={(e) => setPasswordForm((prev) => ({ ...prev, confirm_password: e.target.value }))}
                            className="input w-full"
                          />
                        </div>
                        <div className="flex items-center gap-3">
                          <button
                            onClick={() => setShowPassword((prev) => !prev)}
                            className="btn-secondary px-4 py-2 inline-flex items-center space-x-2"
                          >
                            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                            <span>{showPassword ? 'Hide' : 'Show'} Passwords</span>
                          </button>
                          <button onClick={handleChangePassword} className="btn-secondary px-6 py-2" disabled={saving}>
                            Change Password
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Save Button */}
                  <div className="mt-8 flex justify-end pt-6 border-t border-gray-200">
                    <button onClick={handleSave} className="btn-primary px-8 py-3 inline-flex items-center space-x-2" disabled={saving}>
                      <Save size={20} />
                      <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
