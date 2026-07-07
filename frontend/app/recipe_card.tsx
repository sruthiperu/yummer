"use client"

import {useRouter} from "next/navigation"

import "./recipe_card.css"
import {formatRecipeTags} from "@/lib/recipeTags"


type RecipeCardProps = {
    id: number
    name: string
    total_time?: number | null
    nutrition?: { calories: number } | null
    tags?: string[] | null
    match_score?: number
    user_match_pct?: number
    missing_ings?: string[]
    recipe_ings?: string[]
    user_ings?: string[]
}

function getProgressColor(pct: number): string {
    if (pct >= 75) {
        return "progress_high"
    }
    if (pct >= 50) {
        return "progress_medium"
    }
    return "progress_low"
}

export default function RecipeCard({id, name, total_time, nutrition, tags, match_score, user_match_pct, missing_ings = [], recipe_ings = [], user_ings = []}:
RecipeCardProps) {

    const router = useRouter()

    const display_tags = formatRecipeTags(tags, 3)

    const total_user_ings = user_ings?.length || 0
    const matched = Math.round(((user_match_pct ?? 0) / 100) * total_user_ings)
    const pct = user_match_pct ?? 0

    return (
        <div onClick={() => router.push(`/recipes/${id}`)} className="card">
            <h3 className="recipe_name">
                {name}
            </h3>

            <div className="info">
                {total_time && <span><i className="fa-regular fa-alarm-clock"></i> {total_time} min</span>}
                {nutrition?.calories && (<span><i className="fa-brands fa-nutritionix"></i> {Math.ceil(nutrition.calories)} cal</span>)}
            </div>

            {user_match_pct !== undefined && (
                <div className="ing_match">
                    <div className="match_pct">
                        {matched}/{total_user_ings} of your ingredients used
                    </div>

                    <div className="progress_bar">
                        <div
                            className={`progress_fill ${getProgressColor(pct)}`}
                            style={{width: `${pct}%`}}
                        />
                    </div>

                    {missing_ings.length > 0 && (
                        <p className="missing_ings">
                            You'd also need: {missing_ings.slice(0, 3).join(", ")}
                            {missing_ings.length > 3 && `, and ${missing_ings.length - 3} more`}
                        </p>
                    )}
                </div>
            )}

            {display_tags.length > 0 && (
                <div className="tags_box">
                    {display_tags.map(({ id, label }) => (
                        <span key={id} className="tag">{label}</span>
                    ))}
                </div>
            )}
        </div>
    )
}
