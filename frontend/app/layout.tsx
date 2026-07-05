"use client"

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
      <body>
        <Providers>
          <Navbar />
          {children}
        </Providers>
      </body>
    </html>
  )
}