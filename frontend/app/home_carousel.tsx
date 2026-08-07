"use client"

import type {CSSProperties} from "react"
import RecipeCard from "./recipe_card"
import type {Recipe} from "@/types/recipe"
import "./home_carousel.css"

type HomeCarouselProps = {
  title: string
  recipes: Recipe[]
  loading?: boolean
  direction?: "left" | "right"
  durationSec?: number
}

function CarouselSkeleton() {
  return (
    <div className="home_carousel_skeleton" aria-hidden="true">
      {Array.from({length: 6}).map((_, i) => (
        <div key={i} className="home_carousel_skel_card" />
      ))}
    </div>
  )
}

export default function HomeCarousel({
  title,
  recipes,
  loading = false,
  direction = "left",
  durationSec = 55,
}: HomeCarouselProps) {
  const loop = recipes.length > 0 ? [...recipes, ...recipes] : []

  return (
    <section className="home_carousel">
      <h2 className="home_carousel_title">{title}</h2>
      <div
        className={`home_carousel_viewport home_carousel_viewport--${direction}`}
        aria-label={`${title} recipes`}
      >
        {loading ? (
          <CarouselSkeleton />
        ) : loop.length === 0 ? (
          <p className="home_carousel_empty">No recipes found right now.</p>
        ) : (
          <div
            className="home_carousel_track"
            style={{"--carousel-duration": `${durationSec}s`} as CSSProperties}
          >
            {loop.map((recipe, index) => (
              <div
                key={`${recipe.id}-${index}`}
                className="home_carousel_slide"
              >
                <RecipeCard
                  id={recipe.id}
                  name={recipe.name}
                  total_time={recipe.total_time}
                  nutrition={recipe.nutrition}
                  tags={recipe.tags}
                  rating={recipe.rating}
                  num_ratings={recipe.num_ratings}
                  image={recipe.image}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
