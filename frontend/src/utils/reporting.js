import { adminAPI, analysisAPI } from '../api/client'

const MONTH_FORMATTER = new Intl.DateTimeFormat('en', { month: 'short' })
const WEEKDAY_KEYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function toDate(value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

function getDisplayName(user) {
  const name = (user?.name || '').trim()
  if (name) return name
  const email = user?.email || ''
  return email.includes('@') ? email.split('@')[0] : 'User'
}

function getMatchPercentage(analysis) {
  if (typeof analysis?.match_percentage === 'number') {
    return analysis.match_percentage
  }
  const total = Number(analysis?.total_jd_skills || 0)
  const matched = Number(analysis?.matched_skills_count || 0)
  if (!total) return 0
  return (matched / total) * 100
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function round(value, digits = 1) {
  const factor = 10 ** digits
  return Math.round((value + Number.EPSILON) * factor) / factor
}

function normalizeSkillName(skill) {
  const raw = String(skill || '').trim()
  if (!raw) return null

  const lower = raw.toLowerCase()
  const aliases = {
    js: 'JavaScript',
    javascript: 'JavaScript',
    ts: 'TypeScript',
    typescript: 'TypeScript',
    sql: 'SQL',
    rest: 'REST',
    api: 'API',
    ml: 'Machine Learning',
    ai: 'AI',
  }

  if (aliases[lower]) {
    return aliases[lower]
  }

  return raw
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

export async function fetchReportingSnapshot(currentUser) {
  if (!currentUser?.id) {
    return {
      users: [],
      usersById: {},
      analysesByUser: {},
      allAnalyses: [],
      stats: {
        totalUsers: 0,
        activeUsers: 0,
        completions: 0,
        avgMatchPercentage: 0,
        avgTimeHours: 0,
        satisfactionScore: 0,
        completionRate: 0,
      },
      monthlyTrend: [],
      skillsDistribution: [],
      recentActivities: [],
      engagementData: [],
      performanceData: [],
      progressData: [],
      topPerformers: [],
      completionStatus: [
        { label: 'Completed', value: 0, color: 'bg-green-500' },
        { label: 'In Progress', value: 0, color: 'bg-yellow-500' },
        { label: 'Not Started', value: 100, color: 'bg-gray-400' },
      ],
      roleRestricted: false,
      scopeLabel: 'your',
    }
  }

  let users = []
  let roleRestricted = false

  if (currentUser.role === 'admin') {
    const response = await adminAPI.listUsers({
      limit: 100,
      sort_by: 'created_at',
      sort_order: 'desc',
    })
    users = response?.data?.data || []
  } else {
    roleRestricted = true
    users = [
      {
        id: currentUser.id,
        email: currentUser.email,
        name: currentUser.name,
        role: currentUser.role,
        is_active: currentUser.is_active,
        created_at: currentUser.created_at,
      },
    ]
  }

  const analysesEntries = await Promise.all(
    users.map(async (user) => {
      try {
        const response = await analysisAPI.listAnalyses(user.id, {
          limit: 100,
          sort_by: 'created_at',
          sort_order: 'desc',
        })
        return [user.id, response?.data?.data || []]
      } catch (error) {
        return [user.id, []]
      }
    })
  )

  const analysesByUser = Object.fromEntries(analysesEntries)
  const usersById = Object.fromEntries(users.map((user) => [user.id, user]))
  const allAnalyses = Object.values(analysesByUser).flat()

  const analysesWithMatch = allAnalyses.map((analysis) => ({
    ...analysis,
    match_percentage: getMatchPercentage(analysis),
  }))

  const latestByUser = users.map((user) => {
    const list = analysesByUser[user.id] || []
    return list.length > 0 ? list[0] : null
  })

  const latestExisting = latestByUser.filter(Boolean)
  const completionCutoff = 80
  const inProgressCutoff = 50

  const completedUsers = latestExisting.filter((analysis) => analysis.match_percentage >= completionCutoff).length
  const inProgressUsers = latestExisting.filter((analysis) => (
    analysis.match_percentage >= inProgressCutoff && analysis.match_percentage < completionCutoff
  )).length
  const notStartedUsers = Math.max(users.length - completedUsers - inProgressUsers, 0)

  const totalUsers = users.length
  const activeUsers = users.filter((user) => user.is_active !== false).length
  const avgMatch = analysesWithMatch.length
    ? analysesWithMatch.reduce((sum, analysis) => sum + analysis.match_percentage, 0) / analysesWithMatch.length
    : 0
  const avgMissingSkills = analysesWithMatch.length
    ? analysesWithMatch.reduce((sum, analysis) => sum + Number(analysis.missing_skills_count || 0), 0) / analysesWithMatch.length
    : 0
  const avgTimeHours = round(avgMissingSkills * 6, 1)
  const completionRate = totalUsers > 0 ? round((completedUsers / totalUsers) * 100, 1) : 0

  const now = new Date()
  const monthBuckets = Array.from({ length: 6 }).map((_, idx) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (5 - idx), 1)
    const key = `${date.getFullYear()}-${date.getMonth()}`
    return {
      key,
      month: MONTH_FORMATTER.format(date),
      users: 0,
      completions: 0,
    }
  })
  const monthMap = Object.fromEntries(monthBuckets.map((bucket) => [bucket.key, bucket]))

  users.forEach((user) => {
    const date = toDate(user.created_at)
    if (!date) return
    const key = `${date.getFullYear()}-${date.getMonth()}`
    if (monthMap[key]) {
      monthMap[key].users += 1
    }
  })

  analysesWithMatch.forEach((analysis) => {
    const date = toDate(analysis.created_at)
    if (!date) return
    const key = `${date.getFullYear()}-${date.getMonth()}`
    if (monthMap[key] && analysis.match_percentage >= completionCutoff) {
      monthMap[key].completions += 1
    }
  })

  const skillsCounter = {}
  analysesWithMatch.forEach((analysis) => {
    const skills = Array.isArray(analysis.missing_skills) ? analysis.missing_skills : []
    skills.forEach((skill) => {
      const clean = normalizeSkillName(skill)
      if (!clean) return
      skillsCounter[clean] = (skillsCounter[clean] || 0) + 1
    })
  })

  const skillPalette = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
  const sortedSkills = Object.entries(skillsCounter)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  const skillsDistribution = (() => {
    const total = sortedSkills.reduce((sum, [, count]) => sum + count, 0)
    if (!total) {
      return [{ name: 'No Data', value: 100, color: '#94a3b8' }]
    }
    return sortedSkills.map(([name, count], index) => ({
      name,
      value: round((count / total) * 100, 1),
      color: skillPalette[index % skillPalette.length],
    }))
  })()

  const recentActivities = analysesWithMatch
    .slice()
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 6)
    .map((analysis) => {
      const actor = usersById[analysis.user_id]
      const missing = Number(analysis.missing_skills_count || 0)
      const type = analysis.match_percentage >= completionCutoff ? 'completion' : 'start'
      return {
        id: analysis.analysis_id,
        user: getDisplayName(actor),
        action: `Analysis completed (${round(analysis.match_percentage, 0)}% match, ${missing} skill gaps)`,
        time: new Date(analysis.created_at).toLocaleString(),
        type,
      }
    })

  const dayBuckets = WEEKDAY_KEYS.map((day) => ({
    day,
    engagement: 0,
    sessions: 0,
    _sumMatch: 0,
  }))
  const dayMap = Object.fromEntries(dayBuckets.map((bucket) => [bucket.day, bucket]))
  const last7 = new Date(now)
  last7.setDate(now.getDate() - 6)

  analysesWithMatch.forEach((analysis) => {
    const date = toDate(analysis.created_at)
    if (!date || date < last7) return
    const weekday = WEEKDAY_KEYS[date.getDay()]
    const bucket = dayMap[weekday]
    if (!bucket) return
    bucket.sessions += 1
    bucket._sumMatch += analysis.match_percentage
  })

  const engagementData = dayBuckets.map((bucket) => {
    const engagement = bucket.sessions > 0 ? round(bucket._sumMatch / bucket.sessions, 1) : 0
    return {
      day: bucket.day,
      engagement,
      sessions: bucket.sessions,
    }
  })

  const analysisCount = Math.max(analysesWithMatch.length, 1)
  const performanceData = Object.entries(skillsCounter)
    .map(([program, count]) => ({
      program,
      score: round(clamp(100 - (count / analysisCount) * 100, 0, 100), 1),
      target: 80,
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 6)

  const progressData = users
    .map((user) => {
      const latest = (analysesByUser[user.id] || [])[0]
      if (!latest) return null
      return {
        name: getDisplayName(user),
        started: Number(latest.total_jd_skills || 0),
        completed: Number(latest.matched_skills_count || 0),
      }
    })
    .filter(Boolean)
    .slice(0, 6)

  const topPerformers = users
    .map((user) => {
      const latest = (analysesByUser[user.id] || [])[0]
      return {
        user,
        latest,
      }
    })
    .filter((entry) => !!entry.latest)
    .sort((a, b) => b.latest.match_percentage - a.latest.match_percentage)
    .slice(0, 5)
    .map((entry, index) => ({
      rank: index + 1,
      name: getDisplayName(entry.user),
      score: round(entry.latest.match_percentage, 0),
      completed: Number(entry.latest.matched_skills_count || 0),
    }))

  return {
    users,
    usersById,
    analysesByUser,
    allAnalyses: analysesWithMatch,
    stats: {
      totalUsers,
      activeUsers,
      completions: completedUsers,
      avgMatchPercentage: round(avgMatch, 1),
      avgTimeHours,
      satisfactionScore: round(avgMatch, 0),
      completionRate,
    },
    monthlyTrend: monthBuckets,
    skillsDistribution,
    recentActivities,
    engagementData,
    performanceData,
    progressData,
    topPerformers,
    completionStatus: [
      {
        label: 'Completed',
        value: totalUsers ? round((completedUsers / totalUsers) * 100, 1) : 0,
        color: 'bg-green-500',
      },
      {
        label: 'In Progress',
        value: totalUsers ? round((inProgressUsers / totalUsers) * 100, 1) : 0,
        color: 'bg-yellow-500',
      },
      {
        label: 'Not Started',
        value: totalUsers ? round((notStartedUsers / totalUsers) * 100, 1) : 100,
        color: 'bg-gray-400',
      },
    ],
    roleRestricted,
    scopeLabel: currentUser.role === 'admin' ? 'organization' : 'your',
  }
}
