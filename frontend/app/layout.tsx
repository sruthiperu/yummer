"use client"

import {Suspense} from "react"
import {Providers} from "./providers"
import "./globals.css"
import Navbar from "./nav_bar"

import '@fortawesome/fontawesome-free/css/all.min.css';


export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&icon_names=allergies" />
      </head>
      <body>
        <Providers>
          <Suspense fallback={<nav className="navbar" aria-hidden="true" />}>
            <Navbar />
          </Suspense>
          <div className="app_content">{children}</div>
        </Providers>
      </body>
    </html>
  )
}
