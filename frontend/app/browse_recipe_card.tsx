// Recipe cards for browse section in home page

"use client"

import type {BrowseRecipe} from "./browse_recipes"
import "./browse_recipe_card.css"
import StarRating from "@/lib/StarRating"


type BrowseRecipeCardProps = {
  recipe: BrowseRecipe
}

export default function BrowseRecipeCard({recipe}: BrowseRecipeCardProps) {
  return (
    <a href={recipe.link} target="_blank" rel="noopener noreferrer" className="browse_card">
      <div className="browse_card_body">
        <h3 className="browse_card_title">{recipe.name}</h3>
        <StarRating rating={recipe.rating} />
        <p className="browse_card_description">{recipe.description}</p>
      </div>
    </a>
  )
}
