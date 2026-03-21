import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Clock3, CheckCircle2, AlertTriangle, BookOpen, Target, Sparkles, Star } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { analysisAPI } from '../api/client'

export default function AnalysisResults() {
  const { id } = useParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [feedbackRating, setFeedbackRating] = useState(0)
  const [feedbackComment, setFeedbackComment] = useState('')
  const [feedbackSaving, setFeedbackSaving] = useState(false)
  const [feedbackMessage, setFeedbackMessage] = useState('')
  const [showFeedbackReminder, setShowFeedbackReminder] = useState(false)

  useEffect(() => {
    const loadResult = async () => {
      try {
        setLoading(true)
        setError('')
        const response = await analysisAPI.getAnalysis(id)
        setResult(response.data)
        const initialRating = Number(response?.data?.feedback_rating || 0)
        setFeedbackRating(initialRating)
        setFeedbackComment(response?.data?.feedback_comment || '')
        setShowFeedbackReminder(!initialRating)
      } catch (err) {
        const message = err?.response?.data?.detail || 'Could not load analysis results.'
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    loadResult()
  }, [id])

  const toTitle = (text = '') =>
    String(text)
      .replace(/[_-]/g, ' ')
      .split(' ')
      .filter(Boolean)
      .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
      .join(' ')

  const matchedSkills = result?.matched_skills || []
  const missingSkills = result?.missing_skills || []
  const resumeSkills = result?.resume_skills || []
  const jdSkills = result?.jd_skills || []
  const learningPath = result?.learning_path || []
  const reasoningItems = result?.reasoning || []

  const jdSkillSet = new Set(jdSkills.map((skill) => String(skill).toLowerCase()))
  const resumeOnlySkills = resumeSkills.filter(
    (skill) => !jdSkillSet.has(String(skill).toLowerCase())
  )

  const totalJdSkills = jdSkills.length
  const matchedCount = matchedSkills.length
  const missingCount = missingSkills.length
  const coverage = totalJdSkills > 0 ? Math.round((matchedCount / totalJdSkills) * 100) : 0
  const estimatedHours = learningPath.reduce(
    (sum, node) => sum + Number(node?.estimated_hours || 0),
    0
  )

  const learningPathBySkill = learningPath.reduce((acc, node) => {
    if (node?.skill) {
      acc[String(node.skill).toLowerCase()] = node
    }
    return acc
  }, {})

  const reasoningBySkill = reasoningItems.reduce((acc, item) => {
    if (item?.skill) {
      acc[String(item.skill).toLowerCase()] = item
    }
    return acc
  }, {})

  const createdAt = result?.created_at ? new Date(result.created_at) : null
  const createdAtLabel = createdAt
    ? createdAt.toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
      })
    : 'N/A'

  const handleSubmitFeedback = async () => {
    if (!feedbackRating || feedbackRating < 1 || feedbackRating > 5) {
      setFeedbackMessage('Please select a rating from 1 to 5 stars.')
      return
    }

    try {
      setFeedbackSaving(true)
      setFeedbackMessage('')
      await analysisAPI.submitFeedback(id, {
        rating: feedbackRating,
        comment: feedbackComment?.trim() || null,
      })
      setResult((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          feedback_rating: feedbackRating,
          feedback_comment: feedbackComment?.trim() || '',
        }
      })
      setShowFeedbackReminder(false)
      setFeedbackMessage('Thanks for your feedback. Satisfaction metric has been updated.')
    } catch (err) {
      setFeedbackMessage(err?.response?.data?.detail || 'Could not submit feedback right now.')
    } finally {
      setFeedbackSaving(false)
    }
  }

  const priorityBadgeClass = {
    high: 'bg-red-100 text-red-700',
    medium: 'bg-yellow-100 text-yellow-700',
    low: 'bg-blue-100 text-blue-700',
  }

  const levelBadgeClass = {
    beginner: 'bg-gray-100 text-gray-700',
    intermediate: 'bg-indigo-100 text-indigo-700',
    advanced: 'bg-green-100 text-green-700',
  }

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
              <div className="mt-6 space-y-6">
                {showFeedbackReminder && (
                  <div className="fixed inset-0 z-40 bg-black/40 flex items-center justify-center px-4">
                    <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
                      <h2 className="text-xl font-semibold text-gray-900">Quick Feedback Reminder</h2>
                      <p className="text-sm text-gray-600 mt-2">
                        Analysis is complete. Please add at least a star rating so satisfaction reports reflect real user outcomes.
                      </p>

                      <div className="flex items-center gap-2 mt-4 mb-3">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={`popup-${star}`}
                            type="button"
                            onClick={() => setFeedbackRating(star)}
                            className="p-1"
                            aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
                          >
                            <Star
                              size={24}
                              className={star <= feedbackRating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}
                            />
                          </button>
                        ))}
                        <span className="text-sm text-gray-700 ml-2">{feedbackRating ? `${feedbackRating}/5` : 'Select rating'}</span>
                      </div>

                      <textarea
                        value={feedbackComment}
                        onChange={(e) => setFeedbackComment(e.target.value)}
                        rows={3}
                        maxLength={1000}
                        className="input w-full"
                        placeholder="Optional comment"
                      />

                      <div className="mt-4 flex items-center gap-3">
                        <button
                          type="button"
                          onClick={handleSubmitFeedback}
                          disabled={feedbackSaving}
                          className="btn-primary px-4 py-2"
                        >
                          {feedbackSaving ? 'Submitting...' : 'Submit Feedback'}
                        </button>
                        <button
                          type="button"
                          onClick={() => setShowFeedbackReminder(false)}
                          className="btn-secondary px-4 py-2"
                        >
                          Remind Me Later
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                <section className="card rounded-lg shadow-md p-6">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">Analysis Overview</h2>
                      <p className="text-gray-600 mt-1">Comprehensive skill fit and personalized roadmap</p>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-100 rounded-lg px-3 py-2">
                      <Clock3 size={16} />
                      <span>{createdAtLabel}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
                    <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
                      <p className="text-xs text-blue-700 font-semibold uppercase">Match Coverage</p>
                      <p className="text-2xl font-bold text-blue-900 mt-1">{coverage}%</p>
                    </div>
                    <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                      <p className="text-xs text-green-700 font-semibold uppercase">Matched Skills</p>
                      <p className="text-2xl font-bold text-green-900 mt-1">{matchedCount}</p>
                    </div>
                    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                      <p className="text-xs text-red-700 font-semibold uppercase">Missing Skills</p>
                      <p className="text-2xl font-bold text-red-900 mt-1">{missingCount}</p>
                    </div>
                    <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-4">
                      <p className="text-xs text-indigo-700 font-semibold uppercase">Learning Hours</p>
                      <p className="text-2xl font-bold text-indigo-900 mt-1">{estimatedHours}h</p>
                    </div>
                  </div>

                  <div className="mt-5">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-700 font-medium">Skill Alignment</span>
                      <span className="text-gray-600">{matchedCount}/{totalJdSkills || 0} JD skills matched</span>
                    </div>
                    <div className="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-3 bg-blue-600 rounded-full transition-all" style={{ width: `${coverage}%` }} />
                    </div>
                  </div>
                </section>

                <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="card rounded-lg shadow-md p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <CheckCircle2 className="text-green-600" size={20} />
                      <h2 className="text-xl font-semibold text-gray-900">Matched Skills</h2>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {matchedSkills.length > 0 ? (
                        matchedSkills.map((skill) => (
                          <span
                            key={skill}
                            className="px-3 py-1 rounded-full text-sm bg-green-100 text-green-800 border border-green-200"
                          >
                            {toTitle(skill)}
                          </span>
                        ))
                      ) : (
                        <p className="text-gray-600 text-sm">No matched skills found.</p>
                      )}
                    </div>
                  </div>

                  <div className="card rounded-lg shadow-md p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <AlertTriangle className="text-red-600" size={20} />
                      <h2 className="text-xl font-semibold text-gray-900">Missing Skills</h2>
                    </div>
                    <div className="space-y-2">
                      {missingSkills.length > 0 ? (
                        missingSkills.map((skill) => {
                          const node = learningPathBySkill[String(skill).toLowerCase()]
                          const priority = String(node?.priority || 'medium').toLowerCase()

                          return (
                            <div
                              key={skill}
                              className="flex items-center justify-between gap-3 rounded-lg border border-gray-200 px-3 py-2"
                            >
                              <span className="font-medium text-gray-900">{toTitle(skill)}</span>
                              <span
                                className={`text-xs px-2 py-1 rounded-full font-semibold ${priorityBadgeClass[priority] || priorityBadgeClass.medium}`}
                              >
                                {toTitle(priority)} Priority
                              </span>
                            </div>
                          )
                        })
                      ) : (
                        <p className="text-gray-600 text-sm">No missing skills. Great alignment.</p>
                      )}
                    </div>
                  </div>
                </section>

                <section className="card rounded-lg shadow-md p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <BookOpen className="text-indigo-600" size={20} />
                    <h2 className="text-xl font-semibold text-gray-900">Personalized Learning Path</h2>
                  </div>

                  {learningPath.length === 0 ? (
                    <p className="text-gray-600 text-sm">No learning path steps available for this analysis.</p>
                  ) : (
                    <div className="space-y-4">
                      {learningPath.map((item, index) => {
                        const skillKey = String(item?.skill || `step-${index}`).toLowerCase()
                        const reasoning = reasoningBySkill[skillKey]
                        const currentLevel = String(item?.current_level || item?.level || 'beginner').toLowerCase()
                        const targetLevel = String(item?.target_level || item?.difficulty || 'intermediate').toLowerCase()
                        const priority = String(item?.priority || 'medium').toLowerCase()
                        const steps = item?.steps || []
                        const resources = item?.resources || []
                        const estimated = Number(item?.estimated_hours || 0)

                        return (
                          <article key={`${skillKey}-${index}`} className="rounded-lg border border-gray-200 p-4">
                            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3 mb-3">
                              <div>
                                <h3 className="text-lg font-semibold text-gray-900">{toTitle(item?.skill || 'Skill')}</h3>
                                <div className="flex flex-wrap items-center gap-2 mt-2 text-xs">
                                  <span
                                    className={`px-2 py-1 rounded-full font-semibold ${levelBadgeClass[currentLevel] || levelBadgeClass.beginner}`}
                                  >
                                    Current: {toTitle(currentLevel)}
                                  </span>
                                  <span
                                    className={`px-2 py-1 rounded-full font-semibold ${levelBadgeClass[targetLevel] || levelBadgeClass.intermediate}`}
                                  >
                                    Target: {toTitle(targetLevel)}
                                  </span>
                                  <span
                                    className={`px-2 py-1 rounded-full font-semibold ${priorityBadgeClass[priority] || priorityBadgeClass.medium}`}
                                  >
                                    {toTitle(priority)} Priority
                                  </span>
                                </div>
                              </div>
                              <div className="text-sm font-medium text-gray-700 bg-gray-100 rounded-lg px-3 py-2">
                                Est. {estimated} hours
                              </div>
                            </div>

                            {steps.length > 0 && (
                              <div className="mb-3">
                                <p className="text-sm font-semibold text-gray-800 mb-1">Recommended Steps</p>
                                <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                                  {steps.map((step, stepIndex) => (
                                    <li key={`${skillKey}-step-${stepIndex}`}>{step}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {resources.length > 0 && (
                              <div className="mb-3">
                                <p className="text-sm font-semibold text-gray-800 mb-1">Resources</p>
                                <div className="space-y-1">
                                  {resources.map((resource, resourceIndex) => {
                                    const title = resource?.title || resource?.name || 'Learning Resource'
                                    const type = resource?.type ? `(${resource.type})` : ''
                                    const url = resource?.url

                                    return (
                                      <p key={`${skillKey}-resource-${resourceIndex}`} className="text-sm text-gray-700">
                                        {url ? (
                                          <a
                                            href={url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-blue-600 hover:text-blue-700 font-medium"
                                          >
                                            {title}
                                          </a>
                                        ) : (
                                          <span className="font-medium">{title}</span>
                                        )}{' '}
                                        {type}
                                      </p>
                                    )
                                  })}
                                </div>
                              </div>
                            )}

                            {reasoning?.reason && (
                              <div className="text-sm text-gray-700 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
                                <span className="font-semibold text-blue-800">Why this skill: </span>
                                {reasoning.reason}
                              </div>
                            )}
                          </article>
                        )
                      })}
                    </div>
                  )}
                </section>

                <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="card rounded-lg shadow-md p-6 lg:col-span-1">
                    <div className="flex items-center gap-2 mb-4">
                      <Target className="text-blue-600" size={20} />
                      <h2 className="text-xl font-semibold text-gray-900">JD Skill Inventory</h2>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {jdSkills.map((skill) => (
                        <span
                          key={`jd-${skill}`}
                          className="px-2 py-1 rounded-md text-sm bg-gray-100 text-gray-800 border border-gray-200"
                        >
                          {toTitle(skill)}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="card rounded-lg shadow-md p-6 lg:col-span-1">
                    <div className="flex items-center gap-2 mb-4">
                      <Sparkles className="text-green-600" size={20} />
                      <h2 className="text-xl font-semibold text-gray-900">Resume Skill Inventory</h2>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {resumeSkills.map((skill) => (
                        <span
                          key={`resume-${skill}`}
                          className="px-2 py-1 rounded-md text-sm bg-gray-100 text-gray-800 border border-gray-200"
                        >
                          {toTitle(skill)}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="card rounded-lg shadow-md p-6 lg:col-span-1">
                    <div className="flex items-center gap-2 mb-4">
                      <BookOpen className="text-yellow-600" size={20} />
                      <h2 className="text-xl font-semibold text-gray-900">Additional Resume Strengths</h2>
                    </div>
                    <div className="space-y-2">
                      {resumeOnlySkills.length > 0 ? (
                        resumeOnlySkills.map((skill) => (
                          <div
                            key={`extra-${skill}`}
                            className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-800"
                          >
                            {toTitle(skill)}
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-600 text-sm">No additional resume-only skills identified.</p>
                      )}
                    </div>
                  </div>
                </section>

                <section className="card rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Reasoning Highlights</h2>
                  {reasoningItems.length === 0 ? (
                    <p className="text-gray-600 text-sm">No detailed reasoning available for this analysis.</p>
                  ) : (
                    <div className="space-y-2">
                      {reasoningItems.map((item, idx) => (
                        <div
                          key={`${item?.skill || 'reason'}-${idx}`}
                          className="rounded-lg border border-gray-200 px-3 py-3 text-sm"
                        >
                          <p className="font-semibold text-gray-900 mb-1">{toTitle(item?.skill || 'Skill')}</p>
                          <p className="text-gray-700">{item?.reason || 'No reasoning text available.'}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                <section className="card rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Program Feedback</h2>
                  <p className="text-sm text-gray-600 mb-4">
                    Rate this program outcome. Your feedback is used in the Satisfaction metric across users.
                  </p>

                  <div className="flex items-center gap-2 mb-4">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setFeedbackRating(star)}
                        className="p-1"
                        aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
                      >
                        <Star
                          size={24}
                          className={star <= feedbackRating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}
                        />
                      </button>
                    ))}
                    <span className="text-sm text-gray-700 ml-2">{feedbackRating ? `${feedbackRating}/5` : 'No rating selected'}</span>
                  </div>

                  <textarea
                    value={feedbackComment}
                    onChange={(e) => setFeedbackComment(e.target.value)}
                    rows={4}
                    maxLength={1000}
                    className="input w-full"
                    placeholder="Optional: share what worked well and what can be improved."
                  />

                  <div className="mt-4 flex items-center gap-3">
                    <button
                      type="button"
                      onClick={handleSubmitFeedback}
                      disabled={feedbackSaving}
                      className="btn-primary px-5 py-2"
                    >
                      {feedbackSaving ? 'Submitting...' : 'Submit Feedback'}
                    </button>
                    {feedbackMessage && <p className="text-sm text-gray-700">{feedbackMessage}</p>}
                  </div>
                </section>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
