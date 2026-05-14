"use client"

import {useState} from "react"
import {useRouter} from "next/navigation"

import "./recipe_card.css"


type RecipeCardProps = {
    id: number      // required
    name: string     // required
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

// builds a recipe card using provided info
// maybe add img (pull from source)?
export default function RecipeCard({id, name, total_time, nutrition, tags, match_score, user_match_pct, missing_ings = [], recipe_ings = [], user_ings = []}: 
RecipeCardProps) {

    const router = useRouter()
    
    // show (max 3) helpful tags
    const TAGS = new Set(["vegetarian", "vegan", "gluten-free", "keto", "dairy-free", "low-calorie", "high-protein", 
                          "30-minutes-or-less", "15-minutes-or-less", "60-minutes-or-less",
                          "main-dish", "side-dishes"])
    const display_tags = tags?.filter(t => TAGS.has(t)).slice(0, 3) ?? []

    // normalize userIngredients and recipeIngredients
    // const userIngredients = (user_ings ?? []).map(i => i.trim().toLowerCase())
    // const recipeIngredients = (recipe_ings ?? []).map(i => i.trim().toLowerCase())
    // const matched = userIngredients.filter(userIng => recipeIngredients.some(recipeIng => recipeIng.includes(userIng))).length
    // const pct = userIngredients.length > 0 ? (matched / userIngredients.length) * 100 : 0
    // const matched = userIngredients.filter(ing => recipeIngredients.includes(ing)).length
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
                {nutrition?.calories && (
                    <span><i className="fa-brands fa-nutritionix"></i> {Math.round(nutrition.calories)} cal</span>
                )}
            </div>   

            {/* ing match */}
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
                
                    {/* missing ingredients */}
                    {missing_ings.length > 0 && (
                        <p className="missing_ings">
                            You'd also need: {missing_ings.slice(0, 3).join(", ")}
                            {missing_ings.length > 3 && `, and ${missing_ings.length - 3} more`}
                        </p>
                    )}
                
                </div>
            )}

            {/* tags */}
            
            {display_tags.length > 0 && (
                <div className="tags_box">
                    {display_tags.map(tag => (
                        <span key={tag} className="tag">{tag}</span>
                    ))}
                </div>
            )}

            {/* relevance score */}
            {/* 
            {match_score !== undefined && (
                <div className="relevance">Relevance: {(match_score * 100).toFixed(0)}%</div>
            )} */}

        </div>
    )   
}