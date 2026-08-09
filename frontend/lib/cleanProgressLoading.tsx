"use client"

import {useEffect, useState} from "react"
import "./cleanProgressLoading.css"

const STEPS = [
  "Preparing your ingredients",
  "Cleaning up directions",
  "Checking nutrition details",
  "Putting it all together",
] as const

const STEP_MS = 2000

export default function CleanProgressLoading() {
  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    if (stepIndex >= STEPS.length - 1) return
    const timer = setTimeout(() => setStepIndex((i) => i + 1), STEP_MS)
    return () => clearTimeout(timer)
  }, [stepIndex])

  return (
    <div className="clean_progress">
      <div className="clean_progress_spinner">
        <i className="fa-solid fa-fire-burner" aria-hidden="true" />
      </div>
      <p className="clean_progress_status" key={stepIndex}>
        {STEPS[stepIndex]}
      </p>
      <div className="clean_progress_dots" aria-hidden="true">
        {STEPS.map((_, i) => (
          <span
            key={i}
            className={`clean_progress_dot${i <= stepIndex ? " clean_progress_dot--active" : ""}`}
          />
        ))}
      </div>
    </div>
  )
}
