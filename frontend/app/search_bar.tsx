"use client"

import {useState, SyntheticEvent, useEffect} from "react"
import {useRouter} from "next/navigation"
import "./search_bar.css"

type SearchBarProps = {
  defaultValue?: string
  placeholder?: string
}

export default function SearchBar({defaultValue = "", placeholder = "chicken, pasta, broccoli, ..."}: SearchBarProps) {
  const [q, setQ] = useState(defaultValue)
  const router = useRouter()

  useEffect(() => {setQ(defaultValue)}, [defaultValue])

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

  return (
    <form onSubmit={handleSearch} className="search_form">
      <div className="search_row">
        <div className="search_input_wrapper">
          <i className="fa-solid fa-magnifying-glass search_icon" />
          <input
            type="text"
            autoComplete="off"
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder={placeholder}
            className="search_input"
          />
        </div>
      </div>
    </form>
  )
}
