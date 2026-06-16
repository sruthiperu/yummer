"use client"

import { useRef, useState, useEffect, useCallback } from "react"
import BrowseRecipeCard from "./browse_recipe_card"
import { BROWSE_RECIPES } from "./browse_recipes"
import "./browse_design.css"

export default function BrowseDesign() {
  const trackRef = useRef<HTMLDivElement>(null)
  // state for arrow buttons
  const [canScrollLeft, setCanScrollLeft] = useState(false)     // grayed out if can no longer scroll left (at 1st recipe card)
  const [canScrollRight, setCanScrollRight] = useState(true)    // grayed out if can no longer school right (at last recipe card)

  const updateScrollState = useCallback(() => {
    const track = trackRef.current
    if (!track) return
    
    const { scrollLeft, scrollWidth, clientWidth } = track
    const maxScroll = scrollWidth - clientWidth
    setCanScrollLeft(scrollLeft > 1)
    setCanScrollRight(scrollLeft < maxScroll - 1)
  }, [])

  useEffect(() => {
    const track = trackRef.current
    if (!track) return
    updateScrollState()

    track.addEventListener("scroll", updateScrollState, {passive: true})
    window.addEventListener("resize", updateScrollState)

    return () => {
      track.removeEventListener("scroll", updateScrollState)
      window.removeEventListener("resize", updateScrollState)
    }
  }, [updateScrollState])

  // scrolling
  function scroll(direction: "left" | "right") {
    if (direction === "left" && !canScrollLeft) return
    if (direction === "right" && !canScrollRight) return

    trackRef.current?.scrollBy({left: direction === "left" ? -300 : 300, behavior: "smooth"})
  }

  return (
    <section className="browse_section">
      <div className="browse_header">
        <h2 className="browse_title">Browse</h2>
        <div className="browse_arrows">
          <button type="button" onClick={() => scroll("left")} className={`browse_arrow ${!canScrollLeft ? "browse_arrow--disabled" : ""}`} aria-label="Scroll left" disabled={!canScrollLeft}>
            <i className="fa-solid fa-chevron-left" />
          </button>
          <button type="button" onClick={() => scroll("right")} className={`browse_arrow ${!canScrollRight ? "browse_arrow--disabled" : ""}`} aria-label="Scroll right" disabled={!canScrollRight}>
            <i className="fa-solid fa-chevron-right" />
          </button>
        </div>
      </div>

      <div ref={trackRef} className="browse_track">
        {BROWSE_RECIPES.map((recipe) => (
          <BrowseRecipeCard key={recipe.link} recipe={recipe} />
        ))}
      </div>
    </section>
  )
}