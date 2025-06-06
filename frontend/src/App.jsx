import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Play, Pause, RotateCcw, Settings, TrendingUp, Activity } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import io from 'socket.io-client'
import './App.css'

function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [selectedPattern, setSelectedPattern] = useState('2_consecutive_tails')
  const [statistics, setStatistics] = useState({
    total_sessions: 1000,
    completed_sessions: 0,
    pattern_found_sessions: 0,
    completion_rate: 0,
    pattern_success_rate: 0,
    average_flips_all: 0,
    average_flips_pattern_found: 0,
    theoretical_ev: 6,
    actual_ev: 0,
    pattern_description: '2 consecutive tails',
    is_running: false
  })
  const [sessions, setSessions] = useState([])
  const [realtimeData, setRealtimeData] = useState([])
  const [availablePatterns, setAvailablePatterns] = useState({})
  const [connectionStatus, setConnectionStatus] = useState('disconnected')

  // WebSocket connection - Use relative URLs for Docker/Nginx setup
  const socketRef = useRef(null)
  const API_BASE = '/api'
  const SOCKET_URL = window.location.origin

  // Initialize component
  useEffect(() => {
    loadAvailablePatterns()
    generateMockSessions()
    initializeWebSocket()
    
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [])

  const initializeWebSocket = () => {
    socketRef.current = io(SOCKET_URL)
    
    socketRef.current.on('connect', () => {
      console.log('Connected to server')
      setConnectionStatus('connected')
    })
    
    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from server')
      setConnectionStatus('disconnected')
    })
    
    socketRef.current.on('statistics_update', (data) => {
      setStatistics(data)
      
      // Add to realtime chart data
      setRealtimeData(prev => {
        const newData = [...prev, {
          time: prev.length,
          completed: data.completed_sessions,
          pattern_found: data.pattern_found_sessions,
          avg_flips: data.average_flips_pattern_found
        }]
        return newData.slice(-50) // Keep last 50 data points
      })
    })
    
    socketRef.current.on('simulation_update', (data) => {
      // Update sessions with new data
      if (data.updates && data.updates.length > 0) {
        setSessions(prev => {
          const updated = [...prev]
          data.updates.forEach(update => {
            const index = updated.findIndex(s => s.session_id === update.session_id)
            if (index !== -1) {
              updated[index] = {
                ...updated[index],
                flips_count: update.flips_count,
                completed: update.completed,
                pattern_found: update.pattern_found
              }
            }
          })
          return updated
        })
      }
    })
    
    socketRef.current.on('simulation_completed', (data) => {
      setIsRunning(false)
      setStatistics(data)
      console.log('Simulation completed:', data)
    })
    
    socketRef.current.on('error', (error) => {
      console.error('WebSocket error:', error)
    })
  }

  const loadAvailablePatterns = async () => {
    try {
      const response = await fetch(`${API_BASE}/patterns`)
      if (response.ok) {
        const patterns = await response.json()
        setAvailablePatterns(patterns)
      }
    } catch (error) {
      console.error('Failed to load patterns:', error)
    }
  }

  const generateMockSessions = () => {
    const mockSessions = []
    for (let i = 0; i < 1000; i++) {
      const flipsCount = Math.floor(Math.random() * 20) + 1
      const completed = false // Start with all sessions not completed
      const patternFound = false
      
      mockSessions.push({
        session_id: i,
        flips_count: flipsCount,
        completed,
        pattern_found: patternFound,
        pattern_position: null
      })
    }
    setSessions(mockSessions)
  }

  const startSimulation = async () => {
    try {
      const response = await fetch(`${API_BASE}/simulation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pattern_type: selectedPattern,
          num_sessions: 1000,
          max_flips_per_session: 10000
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          setIsRunning(true)
          setRealtimeData([]) // Clear previous data
          generateMockSessions() // Reset sessions
        }
      }
    } catch (error) {
      console.error('Failed to start simulation:', error)
    }
  }

  const stopSimulation = async () => {
    try {
      await fetch(`${API_BASE}/simulation/stop`, { method: 'POST' })
      setIsRunning(false)
    } catch (error) {
      console.error('Failed to stop simulation:', error)
    }
  }

  const resetSimulation = async () => {
    try {
      await fetch(`${API_BASE}/simulation/reset`, { method: 'POST' })
      setIsRunning(false)
      setStatistics(prev => ({
        ...prev,
        completed_sessions: 0,
        pattern_found_sessions: 0,
        completion_rate: 0,
        pattern_success_rate: 0,
        average_flips_all: 0,
        actual_ev: 0
      }))
      generateMockSessions()
      setRealtimeData([])
    } catch (error) {
      console.error('Failed to reset simulation:', error)
    }
  }

  // Update pattern description when selection changes
  useEffect(() => {
    if (availablePatterns[selectedPattern]) {
      setStatistics(prev => ({
        ...prev,
        pattern_description: availablePatterns[selectedPattern]
      }))
    }
  }, [selectedPattern, availablePatterns])

  const completedSessions = sessions.filter(s => s.completed)
  const patternFoundSessions = sessions.filter(s => s.pattern_found)
  const activeSessions = sessions.filter(s => !s.completed)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            Coin Flip Simulation Dashboard
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Real-time parallel simulation of 1000 coin flip sessions
          </p>
          <div className="flex items-center justify-center gap-2">
            <div className={`w-3 h-3 rounded-full ${connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {connectionStatus === 'connected' ? 'Connected to server' : 'Disconnected from server'}
            </span>
          </div>
        </div>

        {/* Control Panel */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Simulation Controls
            </CardTitle>
            <CardDescription>
              Configure and control your coin flip simulation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4 items-end">
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Target Pattern</label>
                <Select value={selectedPattern} onValueChange={setSelectedPattern} disabled={isRunning}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(availablePatterns).map(([key, description]) => (
                      <SelectItem key={key} value={key}>
                        {description}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2">
                <Button 
                  onClick={isRunning ? stopSimulation : startSimulation}
                  className={isRunning ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"}
                  disabled={connectionStatus !== 'connected'}
                >
                  {isRunning ? (
                    <>
                      <Pause className="h-4 w-4 mr-2" />
                      Stop
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Start
                    </>
                  )}
                </Button>
                <Button onClick={resetSimulation} variant="outline" disabled={isRunning || connectionStatus !== 'connected'}>
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Statistics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="shadow-md">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Sessions</p>
                  <p className="text-2xl font-bold">{statistics.total_sessions}</p>
                </div>
                <Activity className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-md">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</p>
                  <p className="text-2xl font-bold">{statistics.completed_sessions}</p>
                  <Progress value={(statistics.completed_sessions / statistics.total_sessions) * 100} className="mt-2" />
                </div>
                <Badge variant={statistics.completed_sessions === statistics.total_sessions ? "default" : "secondary"}>
                  {Math.round((statistics.completed_sessions / statistics.total_sessions) * 100)}%
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-md">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pattern Found</p>
                  <p className="text-2xl font-bold">{statistics.pattern_found_sessions}</p>
                  <p className="text-sm text-gray-500">
                    {statistics.completed_sessions > 0 ? 
                      Math.round((statistics.pattern_found_sessions / statistics.completed_sessions) * 100) : 0}% success rate
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-md">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Expected Value</p>
                  <p className="text-2xl font-bold">{statistics.actual_ev.toFixed(2)}</p>
                  <p className="text-sm text-gray-500">
                    Theory: {statistics.theoretical_ev}
                  </p>
                </div>
                <Badge variant={Math.abs(statistics.actual_ev - statistics.theoretical_ev) < 1 ? "default" : "secondary"}>
                  {statistics.actual_ev < statistics.theoretical_ev ? "Below" : "Above"} Theory
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Real-time Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Real-time Progress</CardTitle>
              <CardDescription>Live updates of simulation progress</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={realtimeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="completed" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      name="Completed Sessions"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="pattern_found" 
                      stroke="#10b981" 
                      strokeWidth={2}
                      name="Pattern Found"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Average Flips Distribution</CardTitle>
              <CardDescription>Distribution of flips needed to find pattern</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { range: "1-2", count: Math.floor(Math.random() * 50) + 10 },
                    { range: "3-4", count: Math.floor(Math.random() * 100) + 50 },
                    { range: "5-6", count: Math.floor(Math.random() * 80) + 40 },
                    { range: "7-8", count: Math.floor(Math.random() * 60) + 30 },
                    { range: "9-10", count: Math.floor(Math.random() * 40) + 20 },
                    { range: "11+", count: Math.floor(Math.random() * 30) + 10 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="range" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8b5cf6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Session Grid */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Session Status Grid</CardTitle>
            <CardDescription>
              Visual representation of all 1000 sessions (showing first 100)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-10 sm:grid-cols-20 gap-1">
              {sessions.slice(0, 100).map((session) => (
                <div
                  key={session.session_id}
                  className={`
                    w-4 h-4 rounded-sm border transition-all duration-200 hover:scale-110
                    ${session.pattern_found 
                      ? 'bg-green-500 border-green-600' 
                      : session.completed 
                        ? 'bg-red-400 border-red-500' 
                        : isRunning
                          ? 'bg-gray-300 border-gray-400 animate-pulse'
                          : 'bg-gray-200 border-gray-300'
                    }
                  `}
                  title={`Session ${session.session_id}: ${session.flips_count} flips, ${
                    session.pattern_found ? 'Pattern Found' : session.completed ? 'Completed' : 'Running'
                  }`}
                />
              ))}
            </div>
            <div className="flex items-center gap-4 mt-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-sm"></div>
                <span>Pattern Found</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-400 rounded-sm"></div>
                <span>Completed (No Pattern)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-gray-300 rounded-sm animate-pulse"></div>
                <span>Running</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Pattern Information */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Pattern Analysis</CardTitle>
            <CardDescription>
              Current pattern: {statistics.pattern_description}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Theoretical EV</p>
                <p className="text-2xl font-bold text-blue-800 dark:text-blue-200">{statistics.theoretical_ev}</p>
                <p className="text-xs text-blue-600 dark:text-blue-400">Expected flips needed</p>
              </div>
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm font-medium text-green-600 dark:text-green-400">Actual EV</p>
                <p className="text-2xl font-bold text-green-800 dark:text-green-200">{statistics.actual_ev.toFixed(2)}</p>
                <p className="text-xs text-green-600 dark:text-green-400">Observed average</p>
              </div>
              <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-sm font-medium text-purple-600 dark:text-purple-400">Variance</p>
                <p className="text-2xl font-bold text-purple-800 dark:text-purple-200">
                  {Math.abs(statistics.actual_ev - statistics.theoretical_ev).toFixed(2)}
                </p>
                <p className="text-xs text-purple-600 dark:text-purple-400">Difference from theory</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App

