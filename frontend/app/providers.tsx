"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState, useEffect } from "react"

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient())
  useEffect(() => {
    function onPageShow(e: PageTransitionEvent) {
      if (e.persisted) window.location.reload()
    }
    window.addEventListener("pageshow", onPageShow)
    return () => window.removeEventListener("pageshow", onPageShow)
  }, [])

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}