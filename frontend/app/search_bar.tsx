"use client"

import {useState, SyntheticEvent, useEffect} from "react"
import {useRouter, useSearchParams} from "next/navigation"
import "./search_bar.css"

type SearchBarProps = {
  defaultValue?: string
  placeholder?: string
}

const FILTER_KEYS = ["tags", "max_time", "max_calories"] as const

export default function SearchBar({defaultValue = "", placeholder = "chicken, pasta, broccoli, ..."}: SearchBarProps) {
  const [q, setQ] = useState(defaultValue)
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {setQ(defaultValue)}, [defaultValue])

  function handleSearch(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault()
    const trimmed = q.trim()
    if (!trimmed) return

    const params = new URLSearchParams()
    for (const key of FILTER_KEYS) {
      const value = searchParams.get(key)
      if (value) params.set(key, value)
    }
    params.set("page", "1")

    if (trimmed.includes(",")) {
      params.set("ingredients", trimmed)
      router.push(`/search/by-ingredients?${params.toString()}`)
    } else {
      params.set("q", trimmed)
      router.push(`/search?${params.toString()}`)
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
