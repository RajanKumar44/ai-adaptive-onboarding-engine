import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { analysisAPI } from '../api/client'

export default function AnalysisResults() {
  const { id } = useParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    const loadResult = async () => {
      try {
        setLoading(true)
        setError('')
        const response = await analysisAPI.getAnalysis(id)
        setResult(response.data)
      } catch (err) {
        const message = err?.response?.data?.detail || 'Could not load analysis results.'
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    loadResult()
  }, [id])

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 md:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
            <p className="text-gray-600 mt-2">Analysis ID: {id}</p>

            {loading && <p className="mt-6 text-gray-600">Loading analysis...</p>}

            {error && (
              <div className="mt-6 rounded-md bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
                {error}
              </div>
            )}

            {!loading && !error && result && (
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <section className="card rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">Matched Skills</h2>
                  <ul className="list-disc pl-5 space-y-1 text-gray-700">
                    {(result.matched_skills || []).map((skill) => (
                      <li key={skill}>{skill}</li>
                    ))}
                  </ul>
                </section>

                <section className="card rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">Missing Skills</h2>
                  <ul className="list-disc pl-5 space-y-1 text-gray-700">
                    {(result.missing_skills || []).map((skill) => (
                      <li key={skill}>{skill}</li>
                    ))}
                  </ul>
                </section>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
