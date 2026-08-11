"use client"

import {useEffect, useState} from "react"

const MOBILE_MQ = "(max-width: 640px)"
const MOBILE_PAGE_SIZE = 10
const DESKTOP_PAGE_SIZE = 20

// page size for search results: 10 on mobile (<= 640px), 20 otherwise (on tablet, desktop, etc.)
export function usePageSize(): number {
  const [pageSize, setPageSize] = useState(DESKTOP_PAGE_SIZE)

  useEffect(() => {
    const mq = window.matchMedia(MOBILE_MQ)
    const sync = () => setPageSize(mq.matches ? MOBILE_PAGE_SIZE : DESKTOP_PAGE_SIZE)
    sync()
    mq.addEventListener("change", sync)
    return () => mq.removeEventListener("change", sync)
  }, [])

  return pageSize
}
