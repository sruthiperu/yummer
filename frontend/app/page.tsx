"use client"

import {useState, SyntheticEvent} from "react"
import {useRouter} from "next/navigation"
import "./home.css"

export default function HomePage() {
  const [q, set_q] = useState("")   // query
  const router = useRouter()

  function handleSearch(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault()
    if (q.trim()) {
      if (q.includes(",")) {    // search by ingredients
        router.push(`/search/by-ingredients?ingredients=${encodeURIComponent(q.trim())}`)
      } else {    // search
        router.push(`/search?q=${encodeURIComponent(q.trim())}`)
      }
    }
  }

  const quickOptions = [{label: "Vegetarian", q: "vegetarian dinner"}, {label: "Under 30 min", q: "quick dinner"},
                         {label: "High protein", q: "high protein meal"}, {label: "Keto", q: "keto recipes"}]
  
  return (
    <main className="home">

      <h1 className="home_title">Yummer</h1>
      <p className="home_subtitle">Find recipes by ingredients!</p>

      <form onSubmit={handleSearch} className="home_form">
        <div className="search_row">
          <input value={q} onChange={e => set_q(e.target.value)} placeholder="pasta, parmesan, garlic, ..." className="home_input"/>
          
          <button type="submit" className="home_btn">Search</button>
        </div>
      </form>

      <div className="quick_options">
        {quickOptions.map(opt => (
          <button
            key={opt.label}
            onClick={() => router.push(`/search?q=${encodeURIComponent(opt.q)}`)}
            className="quick_opt"
          >{opt.label}</button>
        ))}
      </div>

    </main>
  )
}