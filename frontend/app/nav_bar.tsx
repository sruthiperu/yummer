"use client"

import {useEffect, useRef, useState} from "react"
import Link from "next/link"
import {usePathname, useSearchParams} from "next/navigation"
import {useMe} from "@/lib/useMe"
import "./nav_bar.css"

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function Navbar() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const {data: user, isLoading} = useMe()
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement | null>(null)

  const search = searchParams?.toString()
  const nextPath = `${pathname || "/"}${search ? `?${search}` : ""}`
  const nextQuery = `next=${encodeURIComponent(nextPath)}`

  useEffect(() => {
    function onPointerDown(e: MouseEvent) {
      if (!menuRef.current?.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", onPointerDown)
    return () => document.removeEventListener("mousedown", onPointerDown)
  }, [])

  useEffect(() => {
    setOpen(false)
  }, [pathname, search])

  return (
    <nav className="navbar">
      <div className="nav_cont">
        <Link href="/" className="nav_logo">yummers</Link>

        <div className="nav_auth" ref={menuRef}>
          <button
            type="button"
            className="signin"
            aria-label={user ? "Account menu" : "Sign in"}
            aria-expanded={open}
            aria-haspopup="menu"
            onClick={() => setOpen((v) => !v)}
          >
            <i className="fa-regular fa-circle-user" aria-hidden="true" />
          </button>

          {open && (
            <div className="nav_auth_menu" role="menu">
              {isLoading ? (
                <p className="nav_auth_status">Checking session…</p>
              ) : user ? (
                <>
                  <div className="nav_auth_user">
                    <span className="nav_auth_name">{user.name}</span>
                    <span className="nav_auth_email">{user.email}</span>
                  </div>
                  <a
                    className="nav_auth_item"
                    role="menuitem"
                    href={`${API_URL}/auth/logout?${nextQuery}`}
                  >
                    Sign out
                  </a>
                </>
              ) : (
                <>
                  <p className="nav_auth_status">Sign in to continue</p>
                  <a
                    className="nav_auth_item"
                    role="menuitem"
                    href={`${API_URL}/auth/google?${nextQuery}`}
                  >
                    <i className="fa-brands fa-google" aria-hidden="true" />
                    Continue with Google
                  </a>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
