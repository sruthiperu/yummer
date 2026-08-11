"use client"

import {Suspense, useState, useEffect} from "react"
import SearchBar from "./search_bar"
import HomeCarousel from "./home_carousel"
import HomeMetrics from "./home_metrics"
import {getRecipesByIds} from "@/lib/api"
import {HOME_CAROUSELS} from "@/lib/home_carousels"
import type {Recipe} from "@/types/recipe"
import "./home.css"

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
        schedule(typeTitle, 24)
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
        schedule(typeSub, 22)
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

  useEffect(() => {
    let cancelled = false

    async function loadCarousels() {
      setCarouselsLoading(true)
      try {
        const [meat, veg, keto] = await Promise.all([
          getRecipesByIds(HOME_CAROUSELS.meat.ids),
          getRecipesByIds(HOME_CAROUSELS.vegetarian.ids),
          getRecipesByIds(HOME_CAROUSELS.keto.ids),
        ])
        if (cancelled) return
        setMeatRecipes(meat)
        setVegRecipes(veg)
        setKetoRecipes(keto)
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
            <Suspense fallback={null}>
              <SearchBar placeholder="chicken, pasta, broccoli, ..." />
            </Suspense>
          </div>
        </div>
      </main>

      <div className="home_discover">
        <div className="home_carousels">
          <HomeCarousel
            title={HOME_CAROUSELS.meat.title}
            recipes={meatRecipes}
            loading={carouselsLoading}
            direction="left"
            durationSec={55}
          />
          <HomeCarousel
            title={HOME_CAROUSELS.vegetarian.title}
            recipes={vegRecipes}
            loading={carouselsLoading}
            direction="right"
            durationSec={55}
          />
          <HomeCarousel
            title={HOME_CAROUSELS.keto.title}
            recipes={ketoRecipes}
            loading={carouselsLoading}
            direction="left"
            durationSec={55}
          />
        </div>
      </div>

      <HomeMetrics />

      <section className="home_ai">
        <div className="home_ai_inner">
          <h2 className="home_ai_heading">And the best part?</h2>
          <p className="home_ai_copy">
            Customize recipes using your own{" "}
            <span className="home_ai_accent">AI cooking assistant</span>
          </p>
          <div className="home_ai_video" aria-label="AI recipe customization demo">
            <video
              className="home_customize_demo"
              src="/demos/yummers_customize_demo.mp4"
              autoPlay
              muted
              loop
              playsInline
            />
          </div>
        </div>
      </section>

      <footer className="home_footer">
        <p className="home_footer_text">
          Want to report a bug or suggest a feature? Contact <a href="mailto:sruthiperumalla1107@gmail.com">me</a>!{" "}
          <a
            className="home_footer_github"
            href="https://github.com/sruthiperu/yummer"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Yummer on GitHub"
          >
            <i className="fa-brands fa-github" aria-hidden="true" />
          </a>
        </p>
      </footer>
    </div>
  )
}
