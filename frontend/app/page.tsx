"use client"

import {useState, useEffect, SyntheticEvent} from "react"
import {useRouter} from "next/navigation"
import Link from "next/link"
import SearchBar from "./search_bar"
import BrowseDesign from "./browse_design"
import SearchIngredientsCTA from "./search_ingredients_cta"
import "./home.css"

export default function HomePage() {
  const [q, set_q] = useState("")
  const router = useRouter()

  const title_before = "Find your next "
  const blue_part = "favorite"
  const title_after = " recipe"
  const title = title_before + blue_part + title_after
  const subtitle = "using the ingredients you already have"
  /* typing effect */
  const [titleText, setTitleText] = useState("")
  const [subText, setSubText] = useState("")
  const [titleDone, setTitleDone] = useState(false)
  const [subStarted, setSubStarted] = useState(false)
  const [subDone, setSubDone] = useState(false)
  const [showEndCursor, setShowEndCursor] = useState(false)

  function showText() {
    setTitleText(title)
    setSubText(subtitle)
    setTitleDone(true)
    setSubStarted(true)
    setSubDone(true)
    setShowEndCursor(false)
  }

  // typing effect
  useEffect(() => {

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
        schedule(typeTitle, 40)
      } else {
        setTitleDone(true)
        schedule(() => {
          setSubStarted(true)
          typeSub()
        }, 300)
      }
    }
  
    function typeSub() {
      if (j < subtitle.length) {
        setSubText(subtitle.slice(0, j + 1))
        j++
        schedule(typeSub, 40)
      } else {
        setSubDone(true)
        // remove cursor after it blinks 3 times
        schedule(() => {
          setShowEndCursor(true)
          schedule(() => setShowEndCursor(false), 2500)
        }, 300)
      }
    }
  
    typeTitle()

    return () => {
      cancelled = true
      timers.forEach(clearTimeout)
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

  function handleSearch(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault()
    if (q.trim()) {
      if (q.includes(",")) {
        router.push(`/search/by-ingredients?ingredients=${encodeURIComponent(q.trim())}`)
      } else {
        router.push(`/search?q=${encodeURIComponent(q.trim())}`)
      }
    }
  }

  const quick_options = [
    {label: "Under 30 min", q: "quick dinner"},
    {label: "High protein", q: "high protein meal"}, 
    {label: "Vegetarian", q: "vegetarian dinner"}, 
    {label: "Keto", q: "keto recipes"},
    {label: "Gluten-Free", q: "gluten-free recipes"}
  ]
  
  return (
    <>
      <nav className="navbar">
        <div className="nav_cont">
          <Link href="/" className="nav_logo">
            yummer<span className="logo_dot"></span>
          </Link>

          <Link href="/api/v1/auth/google" className="signin">
            <i className="fa-regular fa-circle-user"></i>
          </Link>
        </div>
      </nav>

      <main className="home">
        <div className="title_wrap">
          <h1 className="home_title">
            {renderTitle(titleText)}
            {!titleDone && <span className="cursor-solid"></span>}
          </h1>
        </div>
        <div className="subtitle_wrap">
          <h2 className="home_subtitle">
            {subText}
            {subStarted && !subDone && <span className="cursor-solid"></span>}
            <span className={`cursor-end ${showEndCursor ? 'visible' : 'hidden'}`}></span>
          </h2>
        </div>

        {/* <SearchBar placeholder="chicken, pasta, broccoli, ..." /> */}
        <div id="home-search">
          <SearchBar placeholder="chicken, pasta, broccoli, ..." />
        </div>

        <div className="quick_options">
          {quick_options.map(opt => (
            <button key={opt.label} onClick={() => router.push(`/search?q=${encodeURIComponent(opt.q)}`)} className="quick_opt">
              {opt.label}
            </button>
          ))}
        </div>
      </main>

      <BrowseDesign />    {/* browse popular, trendy recipes */}
      
      <SearchIngredientsCTA />
    </>
  )
}