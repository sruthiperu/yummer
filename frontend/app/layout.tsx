// Wraps app

"use client"

import {Providers} from "./providers"
import {useMe} from "@/lib/useMe"

import "./globals.css"
import "./nav.css"    // for navigation bar

import '@fortawesome/fontawesome-free/css/all.min.css';


export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers><Nav />{children}</Providers>
      </body>
    </html>
  )
}

function Nav() {
  const {data: user, isLoading} = useMe()
  const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "")

  return (
    <nav className="nav_bar">
      {/* add logo? */}
      <a href="/" className="nav_link">Search</a>
      
      <div className="nav_right">
        {isLoading ? null : user ? (
          // when logged in
          <>
            <span className="user_name">{user.name}</span>
            <a href={`${API_URL}/api/v1/auth/logout`} className="sign-out">
              Sign out
            </a>
          </>
        ):(
          // when logged out
          <a href={`${API_URL}/api/v1/auth/google`} className="sign-in">
            Sign in with Google
          </a>
        )}
      </div>
    </nav>
  )
}
