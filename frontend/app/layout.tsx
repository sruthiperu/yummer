"use client"

import {Providers} from "./providers"

import "./globals.css"

import '@fortawesome/fontawesome-free/css/all.min.css';


export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}