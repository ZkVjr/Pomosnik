import { useState, useEffect, useCallback } from 'react'

interface UseTimerProps {
  initialTime: number
  onComplete?: () => void
}

interface UseTimerReturn {
  timeLeft: number
  isActive: boolean
  startTimer: () => void
  pauseTimer: () => void
  resetTimer: (newTime?: number) => void
}

export function useTimer({ initialTime, onComplete }: UseTimerProps): UseTimerReturn {
  const [timeLeft, setTimeLeft] = useState(initialTime)
  const [isActive, setIsActive] = useState(false)

  useEffect(() => {
    let interval: NodeJS.Timeout

    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((time) => {
          if (time <= 1) {
            setIsActive(false)
            onComplete?.()
            return 0
          }
          return time - 1
        })
      }, 1000)
    }

    return () => clearInterval(interval)
  }, [isActive, timeLeft, onComplete])

  const startTimer = useCallback(() => {
    setIsActive(true)
  }, [])

  const pauseTimer = useCallback(() => {
    setIsActive(false)
  }, [])

  const resetTimer = useCallback((newTime?: number) => {
    setIsActive(false)
    setTimeLeft(newTime ?? initialTime)
  }, [initialTime])

  return {
    timeLeft,
    isActive,
    startTimer,
    pauseTimer,
    resetTimer,
  }
} 