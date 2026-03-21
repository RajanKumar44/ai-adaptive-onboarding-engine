import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { analysisAPI } from '../api/client'

export default function AnalysisUpload() {
  const navigate = useNavigate()
  const [resumeFile, setResumeFile] = useState(null)
  const [jdFile, setJdFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!resumeFile || !jdFile) {
      setError('Please upload both resume and job description files.')
      return
    }

    try {
      setSubmitting(true)
      const formData = new FormData()
      formData.append('resume_file', resumeFile)
      formData.append('jd_file', jdFile)

      const response = await analysisAPI.analyze(formData)
      const analysisId = response?.data?.analysis_id

      if (!analysisId) {
        throw new Error('Analysis completed but no analysis ID was returned.')
      }

      navigate(`/analysis/${analysisId}`)
    } catch (err) {
      const message = err?.response?.data?.detail || err?.message || 'Analysis failed. Please try again.'
      setError(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900">Resume Analysis</h1>
            <p className="text-gray-600 mt-2">Upload a resume and job description to generate a personalized skill-gap report.</p>

            <form onSubmit={handleSubmit} className="card rounded-lg shadow-md p-6 mt-6 space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Resume File (PDF or TXT)</label>
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                  className="input w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Job Description File (PDF or TXT)</label>
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                  className="input w-full"
                />
              </div>

              {error && (
                <div className="rounded-md bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
                  {error}
                </div>
              )}

              <button type="submit" disabled={submitting} className="btn-primary px-6 py-2 rounded-lg disabled:opacity-60">
                {submitting ? 'Analyzing...' : 'Run Analysis'}
              </button>
            </form>
          </div>
        </main>
      </div>
    </div>
  )
}
