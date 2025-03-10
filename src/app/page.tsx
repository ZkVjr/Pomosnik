'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { useToast } from '@/components/ui/use-toast'
import { useTimer } from '@/hooks/useTimer'

export default function Home() {
  const { toast } = useToast()
  const [isRunning, setIsRunning] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [isBreak, setIsBreak] = useState(false)
  const [isLongBreak, setIsLongBreak] = useState(false)
  const [pomodoroCount, setPomodoroCount] = useState(0)
  const [taskName, setTaskName] = useState('')
  const [tasks, setTasks] = useState<Array<{ id: number; name: string; completed: boolean }>>([])
  const [selectedTask, setSelectedTask] = useState<number | null>(null)
  const [timerMode, setTimerMode] = useState<'pomodoro' | 'break' | 'longBreak'>('pomodoro')
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [settings, setSettings] = useState({
    pomodoroTime: 25,
    breakTime: 5,
    longBreakTime: 15,
    longBreakInterval: 4,
  })

  const {
    timeLeft,
    startTimer,
    pauseTimer,
    resetTimer,
    isActive,
  } = useTimer({
    initialTime: settings.pomodoroTime * 60,
    onComplete: handleTimerComplete,
  })

  function handleTimerComplete() {
    const audio = new Audio('/notification.mp3')
    audio.play()

    if (timerMode === 'pomodoro') {
      setPomodoroCount(prev => prev + 1)
      if (selectedTask !== null) {
        setTasks(prev => prev.map(task => 
          task.id === selectedTask ? { ...task, completed: true } : task
        ))
      }
      setIsBreak(true)
      setTimerMode('break')
      resetTimer(settings.breakTime * 60)
      startTimer()
    } else if (timerMode === 'break') {
      if (pomodoroCount % settings.longBreakInterval === 0) {
        setIsLongBreak(true)
        setTimerMode('longBreak')
        resetTimer(settings.longBreakTime * 60)
      } else {
        setIsBreak(false)
        setTimerMode('pomodoro')
        resetTimer(settings.pomodoroTime * 60)
      }
      startTimer()
    } else if (timerMode === 'longBreak') {
      setIsLongBreak(false)
      setTimerMode('pomodoro')
      resetTimer(settings.pomodoroTime * 60)
      startTimer()
    }
  }

  const handleStart = useCallback(() => {
    if (!isActive) {
      startTimer()
      setIsRunning(true)
      setIsPaused(false)
    }
  }, [isActive, startTimer])

  const handlePause = useCallback(() => {
    if (isActive) {
      pauseTimer()
      setIsRunning(false)
      setIsPaused(true)
    }
  }, [isActive, pauseTimer])

  const handleReset = useCallback(() => {
    resetTimer(settings.pomodoroTime * 60)
    setIsRunning(false)
    setIsPaused(false)
    setIsBreak(false)
    setIsLongBreak(false)
    setTimerMode('pomodoro')
  }, [resetTimer, settings.pomodoroTime])

  const handleAddTask = useCallback(() => {
    if (taskName.trim()) {
      setTasks(prev => [...prev, { id: Date.now(), name: taskName, completed: false }])
      setTaskName('')
    }
  }, [taskName])

  const handleDeleteTask = useCallback((id: number) => {
    setTasks(prev => prev.filter(task => task.id !== id))
    if (selectedTask === id) {
      setSelectedTask(null)
    }
  }, [selectedTask])

  const handleSaveSettings = useCallback(() => {
    localStorage.setItem('pomodoroSettings', JSON.stringify(settings))
    toast({
      title: 'Настройки сохранены',
      description: 'Ваши настройки таймера были успешно сохранены.',
    })
    setIsSettingsOpen(false)
  }, [settings, toast])

  useEffect(() => {
    const savedSettings = localStorage.getItem('pomodoroSettings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }
  }, [])

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-4xl font-bold">Pomoshnik</h1>
          <Button
            variant="outline"
            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
            className="bg-gray-800 hover:bg-gray-700"
          >
            Настройки
          </Button>
        </div>

        {isSettingsOpen && (
          <Card className="p-6 bg-gray-800 border-gray-700">
            <h2 className="text-2xl font-semibold mb-4">Настройки таймера</h2>
            <div className="space-y-4">
              <div>
                <Label>Время помодоро (минуты)</Label>
                <Input
                  type="number"
                  value={settings.pomodoroTime}
                  onChange={(e) => setSettings(prev => ({ ...prev, pomodoroTime: parseInt(e.target.value) }))}
                  className="bg-gray-700 border-gray-600"
                />
              </div>
              <div>
                <Label>Время перерыва (минуты)</Label>
                <Input
                  type="number"
                  value={settings.breakTime}
                  onChange={(e) => setSettings(prev => ({ ...prev, breakTime: parseInt(e.target.value) }))}
                  className="bg-gray-700 border-gray-600"
                />
              </div>
              <div>
                <Label>Время длинного перерыва (минуты)</Label>
                <Input
                  type="number"
                  value={settings.longBreakTime}
                  onChange={(e) => setSettings(prev => ({ ...prev, longBreakTime: parseInt(e.target.value) }))}
                  className="bg-gray-700 border-gray-600"
                />
              </div>
              <div>
                <Label>Интервал длинного перерыва (количество помодоро)</Label>
                <Input
                  type="number"
                  value={settings.longBreakInterval}
                  onChange={(e) => setSettings(prev => ({ ...prev, longBreakInterval: parseInt(e.target.value) }))}
                  className="bg-gray-700 border-gray-600"
                />
              </div>
              <Button onClick={handleSaveSettings} className="w-full bg-blue-600 hover:bg-blue-700">
                Сохранить настройки
              </Button>
            </div>
          </Card>
        )}

        <Card className="p-8 bg-gray-800 border-gray-700">
          <div className="text-center mb-8">
            <div className="text-6xl font-bold mb-4">{formatTime(timeLeft)}</div>
            <div className="text-xl text-gray-400">
              {isBreak ? 'Перерыв' : isLongBreak ? 'Длинный перерыв' : 'Помодоро'}
            </div>
          </div>

          <div className="flex justify-center space-x-4">
            {!isRunning ? (
              <Button
                onClick={handleStart}
                className="bg-green-600 hover:bg-green-700"
                size="lg"
              >
                Старт
              </Button>
            ) : (
              <Button
                onClick={handlePause}
                className="bg-yellow-600 hover:bg-yellow-700"
                size="lg"
              >
                Пауза
              </Button>
            )}
            <Button
              onClick={handleReset}
              className="bg-red-600 hover:bg-red-700"
              size="lg"
            >
              Сброс
            </Button>
          </div>
        </Card>

        <Card className="p-6 bg-gray-800 border-gray-700">
          <h2 className="text-2xl font-semibold mb-4">Задачи</h2>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Input
                value={taskName}
                onChange={(e) => setTaskName(e.target.value)}
                placeholder="Введите название задачи"
                className="bg-gray-700 border-gray-600"
              />
              <Button onClick={handleAddTask} className="bg-blue-600 hover:bg-blue-700">
                Добавить
              </Button>
            </div>

            <div className="space-y-2">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className={`flex items-center justify-between p-3 rounded-lg ${
                    task.completed ? 'bg-gray-700' : 'bg-gray-700/50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={selectedTask === task.id}
                      onChange={() => setSelectedTask(task.id)}
                      className="w-4 h-4"
                    />
                    <span className={task.completed ? 'line-through text-gray-400' : ''}>
                      {task.name}
                    </span>
                  </div>
                  <Button
                    onClick={() => handleDeleteTask(task.id)}
                    variant="ghost"
                    className="text-red-400 hover:text-red-300"
                  >
                    Удалить
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
} 