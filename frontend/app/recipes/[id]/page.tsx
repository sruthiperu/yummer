"use client"

import React from 'react'
import './page.css'
import {useParams} from "next/navigation"
import {useRecipe} from "@/lib/useRecipe"
import {useState} from "react"
import {ingredientTypeClass, INGREDIENT_LEGEND} from "@/lib/ingredientColors"
import {displayAllergens, allergenContainsText} from "@/lib/allergenIcons"
import {displayDietaryIcons} from "@/lib/dietaryIcons"

function formatNutritionWhole(n: number) {
    return `${Math.ceil(n)}`
}
function formatNutritionGrams(n: number) {
    return `${Math.ceil(n)} g`
}
function formatNutritionGramsDecimal(n: number) {
    return `${Number(n.toFixed(1))} g`
}

export default function RecipePage() {
    const params = useParams()
    const id = Number(params.id)
    const {data: recipe, isLoading, isError} = useRecipe(id)
    const [message, setMessage] = useState("")     /* user types in input box */
    const [modifiedRecipe, setModifiedRecipe] = useState(null)      /* AI modifies, or null */
    const [aiLoading, setAiLoading] = useState(false) 
    const [aiError, setAiError] = useState("")

    if (isLoading) return <div>Loading...</div>
    if (isError || !recipe) return <div>Recipe not found</div>
    const displayRecipe = modifiedRecipe || recipe

    async function handleModify() {
        if (!message.trim()) {      /* if no input from user */
            return
        }
        setAiLoading(true)
        setAiError("")

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/recipes/${id}/modify`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message }),
            })

            if (!response.ok) {
                throw new Error("handleModify() failed")
            }

            const data = await response.json()      /* parse */

            if (data.conflict) {
                setAiError(data.conflict)
            } else {
                setModifiedRecipe(data)
            }
        } catch (err) {
            setAiError("AI Error")
        } finally {
            setAiLoading(false)
            setMessage("")
        }
    }


    return (
        <main className="styles">

            {/* header */}
            <section className="recipe_header">
                <h1 className="recipe_title">{displayRecipe.name}</h1>

                <div className="recipe_header_footer">
                    <div className="recipe_meta">
                        {displayRecipe.total_time && (
                        <span className="meta_chip meta_chip--time">
                            <i className="fa-regular fa-clock" />
                            {displayRecipe.total_time} min
                        </span>
                        )}

                        {displayRecipe.servings && (
                        <span className="meta_chip meta_chip--servings">
                            <i className="fa-solid fa-user-group" />
                            {displayRecipe.servings} {displayRecipe.servings === 1 ? "serving" : "servings"}
                        </span>
                        )}

                        {recipe.link && (
                        <a
                            href={recipe.link.startsWith("http") ? recipe.link : `https://${recipe.link}`}
                            target="_blank" rel="noopener noreferrer" className="meta_chip meta_chip--link"
                        >
                            <i className="fa-solid fa-arrow-up-right-from-square"/>View original
                        </a>
                        )}
                    </div>

                    {displayRecipe.tags && displayRecipe.tags.length > 0 && (
                        <div className="tags_rec">
                        {displayRecipe.tags.slice(0, 5).map((tag: string) => (<span key={tag} className="tag_rec">{tag}</span>))}
                        </div>
                    )}
                </div>
            </section>
            
            {/* AI chat */}
            <section className="chatbox">
                <div className="chatbox_header">
                    <div className="chatbox_header_text">
                        <h2 className="chatbox_title">Modify this recipe</h2>
                        <p className="chatbox_subtitle">Make it keto, gluten-free, higher in protein, adjust servings, or anything else.</p>
                    </div>
                </div>

                <div className="user_input">
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleModify()}
                        placeholder="How would you like to change this recipe?"
                        disabled={aiLoading}
                        className="chatbox_input"
                    />
                    <button onClick={handleModify} disabled={aiLoading || !message.trim()} className="change_btn">
                        {aiLoading ? (<><i className="fa-solid fa-spinner fa-spin"/>Loading...</>) : (<><i className="fa-solid fa-wand-magic-sparkles"/>Modify</>)}
                    </button>
                </div>

                {aiError && <p className="error_msg">{aiError}</p>}

                {modifiedRecipe && (
                    <div className="success_msg">
                        <span className="success_text">
                            <i className="fa-solid fa-circle-check"/> Recipe modified
                        </span>
                        <button onClick={() => {
                            setModifiedRecipe(null) 
                            setAiError("")}}
                            className="restore_btn"
                        > 
                        Restore original
                        </button>
                    </div>
                )}
            </section>

            {/* nutrition */}
            {displayRecipe.nutrition && (
                <section className="nutrition_info">
                    <h2 className="nutrition_title">Nutrition <i className="fa-brands fa-nutritionix"></i></h2>
                    <div className="nutrition_layout">
                        {[{label: "Calories", value: formatNutritionWhole(displayRecipe.nutrition.calories)}, {label: "Protein", value: formatNutritionGramsDecimal(displayRecipe.nutrition.protein)},
                        {label: "Carbs", value: formatNutritionGrams(displayRecipe.nutrition.carbs)}, {label: "Fat", value: formatNutritionGrams(displayRecipe.nutrition.total_fat)},
                        {label: "Sugar", value: formatNutritionGrams(displayRecipe.nutrition.sugar)}].map(({ label, value }) => (
                            <div key={label} className={"nutrition_card"}>
                                <div className="nutrition_label">{label}</div>
                                <div className="nutrition_val">{value}</div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* ingredients */}
            <section className="ingredients">
                <h2 className="ingredients_title">
                    Ingredients <i className="fa-solid fa-carrot" />
                </h2>
                <div className="ingredient_legend">
                    {INGREDIENT_LEGEND.map(({ type, label }) => (<span key={type} className={`legend_item legend_item--${type}`}>{label}</span>))}
                </div>
                <ul className="ingredients_list">
                    {displayRecipe.ingredients?.map((ing: any) => {
                    const qtyParts = [ing.quantity, ing.unit].filter(Boolean)
                    const qty = ing.container_size
                        ? `${qtyParts.join(" ")} (${ing.container_size})`
                        : qtyParts.join(" ")
                    const name = (ing.name && ing.name.trim()) || "Unknown ingredient"
                    const typeClass = ingredientTypeClass(ing.food_type)
                    const allergens = displayAllergens(ing.allergens)
                    const allergenTooltip = allergenContainsText(allergens)
                    const dietaryIcons = displayDietaryIcons(ing)

                    return (
                        <li key={ing.id} className={`ingredient_tile ingredient_tile--${typeClass}`}>
                            {qty ? (<span className={`ingredient_qty ingredient_qty--${typeClass}`}>{qty}</span>) : (
                                <span className={`ingredient_qty ingredient_qty--empty ingredient_qty--${typeClass}`} aria-label="Up to user's discretion" data-tooltip="Up to user's discretion" tabIndex={0}>
                                    <i className="fa-solid fa-minus" aria-hidden="true" />
                                </span>
                            )}
                            <span className="ingredient_name">{name}</span>
                            {(allergens.length > 0 || dietaryIcons.length > 0) && (
                                <div className="ingredient_tile_icons">
                                    {allergens.length > 0 && (
                                        <span className="allergen_icon" data-tooltip={allergenTooltip} aria-label={allergenTooltip} tabIndex={0}>
                                            <span className="material-symbols-outlined" aria-hidden="true">allergies</span>
                                        </span>
                                    )}
                                    {dietaryIcons.map((d) => (
                                        <span key={d.id} className={`dietary_icon dietary_icon--${d.id}`} data-tooltip={d.label} aria-label={d.label} tabIndex={0}>
                                            <i className={`fa-solid ${d.iconClass}`} aria-hidden="true" />
                                        </span>
                                    ))}
                                </div>
                            )}
                        </li>
                    )
                    })}
                </ul>
            </section>
            
            {/* directions */}
            <section className="directions">
                <h2 className="directions_title"> Directions <i className="fa-solid fa-list-check" /></h2>
                <ol className="directions_list">
                    {displayRecipe.directions?.map((step: any) => (
                    <li key={step.step_num} className="direction_tile">
                        <span className="direction_step">{step.step_num}</span>
                        <p className="direction_text">{step.direction}</p>
                    </li>
                    ))}
                </ol>
            </section>

        </main>

    )

}