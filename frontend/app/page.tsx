"use client"

import {useState, useEffect} from "react"
import SearchBar from "./search_bar"
import HomeCarousel from "./home_carousel"
import HomeMetrics from "./home_metrics"
import {searchRecipes} from "@/lib/api"
import type {Recipe} from "@/types/recipe"
import "./home.css"

const CAROUSEL_LIMIT = 12

function withoutPlantBased(recipes: Recipe[]): Recipe[] {
  return recipes.filter((r) => {
    const tags = (r.tags || []).map((t) => t.toLowerCase())
    return !tags.includes("vegetarian") && !tags.includes("vegan")
  })
}

export default function HomePage() {
  const title_before = "Find your next "
  const blue_part = "favorite"
  const title_after = " recipe"
  const title = title_before + blue_part + title_after
  const subtitle = "using the ingredients you already have"

  const [titleText, setTitleText] = useState("")
  const [subText, setSubText] = useState("")
  const [titleDone, setTitleDone] = useState(false)
  const [subStarted, setSubStarted] = useState(false)
  const [subDone, setSubDone] = useState(false)
  const [showEndCursor, setShowEndCursor] = useState(false)

  const [meatRecipes, setMeatRecipes] = useState<Recipe[]>([])
  const [vegRecipes, setVegRecipes] = useState<Recipe[]>([])
  const [ketoRecipes, setKetoRecipes] = useState<Recipe[]>([])
  const [carouselsLoading, setCarouselsLoading] = useState(true)

  // typing effect
  useEffect(() => {
    setTitleText("")
    setSubText("")
    setTitleDone(false)
    setSubStarted(false)
    setSubDone(false)
    setShowEndCursor(false)

    let i = 0
    let j = 0
    let cancelled = false
    const timers: ReturnType<typeof setTimeout>[] = []
    function schedule(fn: () => void, ms: number) {
      timers.push(
        setTimeout(() => {
          if (!cancelled) fn()
        }, ms)
      )
    }

    function typeTitle() {
      if (i < title.length) {
        setTitleText(title.slice(0, i + 1))
        i++
        schedule(typeTitle, 36)
      } else {
        setTitleDone(true)
        schedule(() => {
          setSubStarted(true)
          typeSub()
        }, 280)
      }
    }

    function typeSub() {
      if (j < subtitle.length) {
        setSubText(subtitle.slice(0, j + 1))
        j++
        schedule(typeSub, 32)
      } else {
        setSubDone(true)
        schedule(() => {
          setShowEndCursor(true)
          schedule(() => setShowEndCursor(false), 2200)
        }, 250)
      }
    }

    typeTitle()

    return () => {
      cancelled = true
      timers.forEach(clearTimeout)
    }
  }, [])

  // carousel data
  useEffect(() => {
    let cancelled = false

    async function loadCarousels() {
      setCarouselsLoading(true)
      try {
        const [meatRes, vegRes, ketoRes] = await Promise.all([
          searchRecipes("chicken", {tags: "main-course"}),
          searchRecipes("dinner", {tags: "vegetarian"}),
          searchRecipes("dinner", {tags: "keto"}),
        ])
        if (cancelled) return
        setMeatRecipes(withoutPlantBased(meatRes.results || []).slice(0, CAROUSEL_LIMIT))
        setVegRecipes((vegRes.results || []).slice(0, CAROUSEL_LIMIT))
        setKetoRecipes((ketoRes.results || []).slice(0, CAROUSEL_LIMIT))
      } catch {
        if (!cancelled) {
          setMeatRecipes([])
          setVegRecipes([])
          setKetoRecipes([])
        }
      } finally {
        if (!cancelled) setCarouselsLoading(false)
      }
    }

    loadCarousels()
    return () => {
      cancelled = true
    }
  }, [])

  function renderTitle(text: string) {
    const beforeLen = title_before.length
    const accentEnd = beforeLen + blue_part.length
    const before = text.slice(0, Math.min(text.length, beforeLen))
    const accent = text.length > beforeLen ? text.slice(beforeLen, Math.min(text.length, accentEnd)) : ""
    const after = text.length > accentEnd ? text.slice(accentEnd) : ""

    return (
      <>
        {before}
        {accent && <span className="home_title_accent">{accent}</span>}
        {after}
      </>
    )
  }

  return (
    <div className="home_page">
      <main className="home">
        <div className="home_hero">
          <div className="title_wrap">
            <h1 className="home_title">
              {renderTitle(titleText)}
              {!titleDone && <span className="cursor-solid" />}
            </h1>
          </div>
          <div className="subtitle_wrap">
            <h2 className="home_subtitle">
              {subText}
              {subStarted && !subDone && <span className="cursor-solid" />}
              <span className={`cursor-end ${showEndCursor ? "visible" : "hidden"}`} />
            </h2>
          </div>

          <div id="home-search" className="home_search">
            <SearchBar placeholder="chicken, pasta, broccoli, ..." />
          </div>
        </div>
      </main>

      <div className="home_discover">
        <div className="home_carousels">
          <HomeCarousel
            title="Meat Lovers"
            recipes={meatRecipes}
            loading={carouselsLoading}
            direction="left"
            durationSec={58}
          />
          <HomeCarousel
            title="Vegetarian"
            recipes={vegRecipes}
            loading={carouselsLoading}
            direction="right"
            durationSec={64}
          />
          <HomeCarousel
            title="Keto"
            recipes={ketoRecipes}
            loading={carouselsLoading}
            direction="left"
            durationSec={52}
          />
        </div>
      </div>

      <HomeMetrics />

      <section className="home_ai">
        <div className="home_ai_inner">
          <h2 className="home_section_heading home_ai_heading">And the best part?</h2>
          <div className="home_ai_row">
            <p className="home_ai_copy">
              Customize recipes using your own{" "}
              <span className="home_ai_accent">AI cooking assistant</span>
            </p>
            <div className="home_ai_video" aria-label="App demo video placeholder">
              <div className="home_video_placeholder_content">
                <i className="fa-regular fa-circle-play home_video_play" aria-hidden="true" />
                <span className="home_ai_video_label">Video coming soon</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
