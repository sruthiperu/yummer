// Recipe cards for browse section in home page

"use client"

import { useState } from "react"
import type { BrowseRecipe } from "./browse_recipes"
import Image from "next/image"
import "./browse_recipe_card.css"

type BrowseRecipeCardProps = {
  recipe: BrowseRecipe
}

// show rating
function StarRating({ rating }: { rating: number }) {
  return (
    <div className="browse_rating" aria-label={`${rating}`}>
      <div className="browse_stars">
        {[1, 2, 3, 4, 5].map((i) => {
          const fill = Math.min(Math.max(rating - i + 1, 0), 1)

          if (fill >= 1) {      // full star
            return (
              <span key={i} className="browse_star_wrap">
                <i className="fa-solid fa-star browse_star browse_star--filled" />
              </span>
            )
          }
          if (fill <= 0) {      // empty star
            return (
              <span key={i} className="browse_star_wrap">
                <i className="fa-regular fa-star browse_star browse_star--empty" />
              </span>
            )
          }
        
          return (
            <span key={i} className="browse_star_wrap">
              <i className="fa-regular fa-star browse_star browse_star--empty" />
              <span className="browse_star_fill" style={{ width: `${fill * 100}%` }}>
                <i className="fa-solid fa-star browse_star browse_star--filled" />
              </span>
            </span>
          )
        })}
      </div>
      <span className="browse_rating_text">{rating.toFixed(1)}</span>
    </div>
  )
}

export default function BrowseRecipeCard({recipe}: BrowseRecipeCardProps) {
  const [imgError, setImgError] = useState(false)

  return (
    <a href={recipe.link} target="_blank" rel="noopener noreferrer" className="browse_card">        {/* link the card */}
      <div className="browse_card_image_wrap">          {/* image container */}
        {!imgError ? (
          <Image src={recipe.image} alt={recipe.name} fill sizes="260px" className="browse_card_image" onError={() => setImgError(true)}/>
        ) : (
          <div className="browse_card_image_fallback">
            <i className="fa-solid fa-utensils"/>
          </div>
        )}
      </div>

      <div className="browse_card_body">
        <h3 className="browse_card_title">{recipe.name}</h3>
        <StarRating rating={recipe.rating} />
        <p className="browse_card_description">{recipe.description}</p>
      </div>
    </a>
  )
}