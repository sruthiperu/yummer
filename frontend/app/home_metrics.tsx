"use client"

import {useEffect, useRef, useState} from "react"
import "./home_metrics.css"

type MetricItem = {
  target: number
  heading: string
  label: string
}

const METRICS: MetricItem[] = [
  {target: 224_000, heading: "Browse", label: "recipes"},
  {target: 30_000, heading: "Search", label: "ingredients"},
]

const DURATION_MS = 1800

function easeOutCubic(t: number) {
  return 1 - Math.pow(1 - t, 3)
}

function formatCount(n: number) {
  return `${Math.round(n).toLocaleString("en-US")}+`
}

export default function HomeMetrics() {
  const sectionRef = useRef<HTMLElement | null>(null)
  const [values, setValues] = useState(() => METRICS.map(() => 0))
  const [started, setStarted] = useState(false)

  useEffect(() => {
    const el = sectionRef.current
    if (!el) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          setStarted(true)
          observer.disconnect()
        }
      },
      {threshold: 0.35},
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!started) return

    let frame = 0
    const start = performance.now()

    function tick(now: number) {
      const t = Math.min(1, (now - start) / DURATION_MS)
      const eased = easeOutCubic(t)
      setValues(METRICS.map((m) => m.target * eased))
      if (t < 1) {
        frame = requestAnimationFrame(tick)
      }
    }

    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [started])

  return (
    <section
      ref={sectionRef}
      className={`home_metrics_block${started ? " home_metrics_section--started" : ""}`}
      aria-label="Yummers by the numbers"
    >
      <h2 className="home_section_heading home_metrics_title">yummers by the numbers</h2>
      <div className="home_metrics_section">
        <div className="home_metrics_inner">
          <div className="home_metrics">
            {/* left: video */}
            <div className="home_metrics_video">
              <video
                className="home_demo_video"
                src="/demos/yummers_browse_demo.mp4"
                autoPlay
                muted
                loop
                playsInline
              />
            </div>

            {/* right: metrics */}
            <div className="home_metrics_values">

              <div className="home_metric">
                <h3 className="home_metric_heading">
                  {METRICS[0].heading}
                </h3>
                <span className="home_metric_value">
                  {formatCount(values[0] ?? 0)}
                </span>
                <span className="home_metric_label">
                  {METRICS[0].label}
                </span>
              </div>

              <div className="home_metric">
                <h3 className="home_metric_heading">
                  {METRICS[1].heading}
                </h3>
                <span className="home_metric_value">
                  {formatCount(values[1] ?? 0)}
                </span>
                <span className="home_metric_label">
                  {METRICS[1].label}
                </span>
              </div>

            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
