"use client"

import Link from "next/link"
import "./nav_bar.css"

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav_cont">
        <Link href="/" className="nav_logo">yummer</Link>
        <a href={`${process.env.NEXT_PUBLIC_API_URL}/auth/google`} className="signin">
          <i className="fa-regular fa-circle-user" />
        </a>
      </div>
    </nav>
  )
}