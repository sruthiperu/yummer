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

/*
export default function StarRating({rating, num_ratings, showCount = false, size = "sm"}: StarRatingProps) {
  
    return (
    <div className={`star_rating star_rating--${size}`} aria-label={`${rating} out of 5 stars`}>
      
      <div className="star_rating__stars">
        {[1, 2, 3, 4, 5].map((i) => {
          const fill = Math.min(Math.max(rating - i + 1, 0), 1)

          if (fill >= 1) {
            return (
              <span key={i} className="star_rating__star_wrap">
                <i className="fa-solid fa-star star_rating__star star_rating__star--filled" />
              </span>
            )
          }
          if (fill <= 0) {
            return (
              <span key={i} className="star_rating__star_wrap">
                <i className="fa-regular fa-star star_rating__star star_rating__star--empty" />
              </span>
            )
          }

          return (
            <span key={i} className="star_rating__star_wrap">
              <i className="fa-regular fa-star star_rating__star star_rating__star--empty" />
              <span className="star_rating__star_fill" style={{ width: `${fill * 100}%` }}>
                <i className="fa-solid fa-star star_rating__star star_rating__star--filled" />
              </span>
            </span>
          )

        })}
      </div>
      
      <span className="star_rating__text">{rating.toFixed(1)}</span>
      
      {showCount && num_ratings != null && (
        <span className="star_rating__count">({num_ratings})</span>
      )}
    </div>
  )
}
*/