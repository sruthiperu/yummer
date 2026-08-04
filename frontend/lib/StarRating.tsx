"use client"

import "./StarRating.css"

type StarRatingProps = {
  rating: number
  num_ratings?: number | null
  showCount?: boolean
  size?: "sm" | "md"
}

export default function StarRating({rating, num_ratings, showCount = false, size = "sm"}: StarRatingProps) {
  return (
    <div className={`star_rating star_rating--${size}`} aria-label={`${rating} out of 5 stars`}>
      <i className="fa-solid fa-star star_rating__icon" />
      <span className="star_rating__text">{rating.toFixed(1)}</span>
        {showCount && num_ratings != null && (
          <span className="star_rating__count">({num_ratings})</span>
        )}
    </div>
  )
}
