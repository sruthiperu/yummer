"use client"

import {useState, useEffect, SyntheticEvent} from "react"
import {useRouter} from "next/navigation"
import Link from "next/link"
import SearchBar from "./search_bar"
import "./home.css"

export default function HomePage() {
  const [q, set_q] = useState("")
  const router = useRouter()

  const title = "Find your next favorite recipe"
  const subtitle = "with ingredients you already have"
  /* typing effect */
  const [titleText, setTitleText] = useState("")
  const [subText, setSubText] = useState("")
  const [titleDone, setTitleDone] = useState(false)
  const [subStarted, setSubStarted] = useState(false)
  const [subDone, setSubDone] = useState(false)
  const [showEndCursor, setShowEndCursor] = useState(false)

  useEffect(() => {
    let i = 0
    let j = 0
    
    function typeTitle() {
      if (i < title.length) {
        setTitleText(title.slice(0, i + 1))
        i++
        setTimeout(typeTitle, 40)
      } else {
        setTitleDone(true)
        setTimeout(() => {
          setSubStarted(true)
          typeSub()
        }, 300)
      }
    }
  
    function typeSub() {
      if (j < subtitle.length) {
        setSubText(subtitle.slice(0, j + 1))
        j++
        setTimeout(typeSub, 40)
      } else {
        setSubDone(true)
        setTimeout(() => {
          setShowEndCursor(true)
          // remove cursor after it blinks 3 times
          setTimeout(() => {
            setShowEndCursor(false)
          }, 2500)
        }, 300)
      }
    }
  
    typeTitle()
  }, [])

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
    {label: "Vegetarian", q: "vegetarian dinner"}, 
    {label: "Under 30 min", q: "quick dinner"},
    {label: "High protein", q: "high protein meal"}, 
    {label: "Keto", q: "keto recipes"}
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
            {titleText}
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

        <SearchBar placeholder="chicken, pasta, broccoli, ..." />
        {/* 
        <form onSubmit={handleSearch} className="home_form">
          <div className="search_row">
            <div className="search_input_wrapper">
              <i className="fa-solid fa-magnifying-glass search_icon"></i>
              <input
                type="text"
                autoComplete="off"
                value={q}
                onChange={e => set_q(e.target.value)}
                placeholder="chicken, pasta, broccoli, ..."
                className="search_input"
              />
            </div>
          </div>
        </form>
        */}

        <div className="quick_options">
          {quick_options.map(opt => (
            <button
              key={opt.label}
              onClick={() => router.push(`/search?q=${encodeURIComponent(opt.q)}`)}
              className="quick_opt"
            >
              {opt.label}
            </button>
          ))}
        </div>
      </main>
    </>
  )
}