"use client"

import React from 'react'
import './page.css'
import {useParams} from "next/navigation"       /* get url parameter; e.g. '1' in recipes/1 */
import {useRecipe} from "@/lib/useRecipe" 
import {useState} from "react"

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

            { /* header */ }
            <section className="recipe_header">
                <h1 className="recipe_title">{displayRecipe.name}</h1>

                <div className="recipe_meta">
                    {displayRecipe.total_time && (
                    <span className="meta_chip meta_chip--time">
                        <i className="fa-regular fa-clock" />
                        {displayRecipe.total_time} min
                    </span>
                    )}

                    {recipe.link && (
                    <a
                        href={recipe.link.startsWith("http") ? recipe.link : `https://${recipe.link}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="meta_chip meta_chip--link"
                    >
                        <i className="fa-solid fa-arrow-up-right-from-square" />
                        View original
                    </a>
                    )}
                </div>

                {displayRecipe.tags && displayRecipe.tags.length > 0 && (
                    <div className="tags_rec">
                    {displayRecipe.tags.slice(0, 5).map((tag: string) => (
                        <span key={tag} className="tag_rec">{tag}</span>
                    ))}
                    </div>
                )}
            </section>
            
            { /* AI chat */ }
            <section className="chatbox">
                <div className="chatbox_header">
                    <div className="chatbox_header_text">
                        <h2 className="chatbox_title">Modify this recipe</h2>
                        <p className="chatbox_subtitle">
                            Make it keto, gluten-free, higher in protein, adjust servings, or anything else.
                        </p>
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
                        {aiLoading ? (
                            <><i className="fa-solid fa-spinner fa-spin" />Loading...</>
                        ) : (
                            <><i className="fa-solid fa-wand-magic-sparkles" />Modify</>
                        )}
                    </button>
                </div>

                {aiError && <p className="error_msg">{aiError}</p>}

                {modifiedRecipe && (
                    <div className="success_msg">
                        <span className="success_text">
                            <i className="fa-solid fa-circle-check" /> Recipe modified
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

            { /* nutrition */ }
            {displayRecipe.nutrition && (
                <section className="nutrition_info">
                    <h2 className="section_title">Nutrition <i className="fa-brands fa-nutritionix"></i></h2>
                    <div className="nutrition_layout">
                        {[{label: "Calories", value: displayRecipe.nutrition.calories}, {label: "Protein", value: `${displayRecipe.nutrition.protein}g`},
                        {label: "Carbs", value: `${displayRecipe.nutrition.carbs}g`}, {label: "Fat", value: `${displayRecipe.nutrition.total_fat}g`},
                        {label: "Sugar", value: `${displayRecipe.nutrition.sugar}g`}].map(({ label, value }) => (
                            <div key={label} className={"nutrition_card"}>
                                <div className="nutrition_val">{value}</div>
                                <div className="nutrition_label">{label}</div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            { /* ingredients */ }
            <section className="ingredients">
                <h2 className="ingredients_title">
                    Ingredients <i className="fa-solid fa-carrot" />
                </h2>
                <ul className="ingredients_list">
                    {displayRecipe.ingredients?.map((ing: any, i: number) => {
                    const qty = [ing.quantity, ing.unit].filter(Boolean).join(" ")
                    const name = ing.name || ing.raw_ingredient

                    return (
                        <li key={i} className="ingredient_tile">
                        {qty && (<span className="ingredient_qty">{qty}</span>)}
                        <span className="ingredient_name">{name}</span>
                        </li>
                    )
                    })}
                </ul>
            </section>
            
            { /* directions */}
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