"use client"

import React, { useState, useEffect } from 'react'
import './page.css'
import {useParams, useSearchParams} from "next/navigation"
import {useRecipe} from "@/lib/useRecipe"
import {ingredientTypeClass, INGREDIENT_LEGEND} from "@/lib/ingredientColors"
import {displayAllergens, allergenContainsText, ALLERGEN_LEGEND} from "@/lib/allergenIcons"
import {displayDietaryIcons, DIETARY_LEGEND} from "@/lib/dietaryIcons"
import {formatRecipeTags} from "@/lib/recipeTags"
import {groupIngredientsBySection, sectionKey, distributeSectionsToColumns} from "@/lib/ingredientSections"
import {groupDirectionsBySection, directionSectionKey} from "@/lib/directionSections"
import type {Ingredient, Instruction} from "@/types/recipe"
import type {IngredientSection} from "@/lib/ingredientSections"
import type {DirectionSection} from "@/lib/directionSections"
import StarRating from "@/lib/StarRating"
import LoadingAnimation from "@/lib/loadingAnimation";


// const [baselineRecipe, setBaselineRecipe] = useState(null);     // cleaned recipe


function areIngredientsEqual(a: any, b: any): boolean {
    return (a.name === b.name) && (a.quantity === b.quantity) && (a.unit === b.unit) && (a.container_size === b.container_size) && (a.section_title === b.section_title);
}
function areDirectionsEqual(a: any, b: any): boolean {
    return (a.direction === b.direction) && (a.section_title === b.section_title);
}
function getModifiedIndices<T>(original: T[], modified: T[], comparator: (a: T, b: T) => boolean): Set<number> {
    const modifiedIndices = new Set<number>();
    const maxLen = Math.max(original.length, modified.length);
    for (let i = 0; i < maxLen; i++) {
        if (i >= original.length || i >= modified.length) {
            modifiedIndices.add(i);
        } else if (!comparator(original[i], modified[i])) {
            modifiedIndices.add(i);
        }
    }
    return modifiedIndices;
}

function formatNutritionWhole(n: number) {
    return `${Math.ceil(n)}`
}
function formatNutritionGrams(n: number) {
    return `${Math.ceil(n)} g`
}
function formatNutritionGramsDecimal(n: number) {
    return `${Number(n.toFixed(1))} g`
}

function DirectionSectionPanel({
    section,
    sectionIndex,
    startIndex,
    modifiedIndices,
} : {
    section: DirectionSection;
    sectionIndex: number;
    startIndex: number;
    modifiedIndices: Set<number>;
}) {
    return (
        <div className="direction_section">
            {section.title && (
                <h3 className="direction_section_title">{section.title}</h3>
            )}
            <ol className="direction_section_list">
                {section.steps.map((step, localIndex) => {
                    const globalIndex = startIndex + localIndex;
                    const isModified = modifiedIndices.has(globalIndex);
                    
                    return (
                        <li key={`${sectionIndex}-${localIndex}`} className="direction_tile">
                            <span className="direction_step">{localIndex + 1}</span>
                            <p className="direction_text">
                                {step.direction}
                                {isModified && (<i className="fa-solid fa-pen-to-square" style={{ marginLeft: '6px', color: '#2D6A4F', fontSize: '0.8rem' }} />
                                )}
                            </p>
                        </li>
                    );
                })}
            </ol>
        </div>
    );
}

function IngredientSectionPanel({
    section,
    sectionIndex,
    startIndex,
    modifiedIndices,
} : {
    section: IngredientSection;
    sectionIndex: number;
    startIndex: number;
    modifiedIndices: Set<number>;
}) {
    return (
        <div className="ingredient_section">
            {section.title && (
                <h3 className="ingredient_section_title">{section.title}</h3>
            )}
            <ul className="ingredient_section_list">
                {section.ingredients.map((ing, localIndex) => {
                    const globalIndex = startIndex + localIndex;
                    return (
                        <IngredientTile
                            key={`${sectionIndex}-${localIndex}`}
                            ing={ing}
                            isModified={modifiedIndices.has(globalIndex)}
                        />
                    );
                })}
            </ul>
        </div>
    );
}

function IngredientTile({ ing, isModified }: { ing: Ingredient; isModified?: boolean }) {
    const qtyParts = [ing.quantity, ing.unit].filter(Boolean);
    const qty = ing.container_size ? `${qtyParts.join(" ")} (${ing.container_size})` : qtyParts.join(" ");
    const name = (ing.name && ing.name.trim()) || "Unknown ingredient";
    const typeClass = ingredientTypeClass(ing.food_type);
    const allergens = displayAllergens(ing.allergens);
    const allergenTooltip = allergenContainsText(allergens);
    const dietaryIcons = displayDietaryIcons(ing);

    return (
        <li className={`ingredient_tile ingredient_tile--${typeClass}`}>
            {/* quantity */}
            {qty ? (
                <span className={`ingredient_qty ingredient_qty--${typeClass}`}>{qty}</span>
            ) : (
                <span
                    className={`ingredient_qty ingredient_qty--empty ingredient_qty--${typeClass}`}
                    aria-label="As much as you'd like!"
                    data-tooltip="As much as you'd like!"
                    tabIndex={0}
                >
                    <i className="fa-solid fa-minus" aria-hidden="true" />
                </span>
            )}
            <span className="ingredient_name">
                {name}
                {isModified && (
                    <i
                        className="fa-solid fa-pen-to-square"
                        style={{ marginLeft: '6px', color: '#2D6A4F', fontSize: '0.8rem' }}
                    />
                )}
            </span>
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
    );
}

export default function RecipePage() {
    const params = useParams()
    const searchParams = useSearchParams();
    const id = Number(params.id)
    const {data: recipe, isLoading, isError} = useRecipe(id)
    const [message, setMessage] = useState("")     /* user types in input box */
    const [modifiedRecipe, setModifiedRecipe] = useState(null)      /* AI modifies, or null */
    const [aiLoading, setAiLoading] = useState(false) 
    const [aiError, setAiError] = useState("")

    const shouldClean = searchParams.get("cleaned") === "1";


    useEffect(() => {
        if (shouldClean && recipe && !modifiedRecipe) {
            const cached = sessionStorage.getItem(`cleaned-${id}`);
            if (cached) {
                try {
                    setModifiedRecipe(JSON.parse(cached));
                    sessionStorage.removeItem(`cleaned-${id}`);
                    return;
                } catch {}
            }
            handleClean();
        }
    }, [shouldClean, recipe, modifiedRecipe]);

    if (aiLoading) {
        return (
            <div className="ai_loading_overlay">
                <LoadingAnimation text="Loading recipe…"/>
            </div>
        );
    }
    if (isLoading) return <div>Loading...</div>
    if (isError || !recipe) return <div>Recipe not found</div>

    const displayRecipe = modifiedRecipe || recipe
    const originalIngredients = recipe?.ingredients || [];
    const displayIngredients = displayRecipe?.ingredients || [];
    const modifiedIngredientIndices = getModifiedIndices(originalIngredients, displayIngredients, areIngredientsEqual);
    const originalDirections = recipe?.directions || [];
    const displayDirections = displayRecipe?.directions || [];
    const modifiedDirectionIndices = getModifiedIndices(originalDirections, displayDirections, areDirectionsEqual);

    const recipeTags = formatRecipeTags(displayRecipe.tags)
    const ingredientSections = groupIngredientsBySection(displayRecipe.ingredients ?? [])
    const useSectionLayout = ingredientSections.length > 1
    const [leftSections, rightSections] = distributeSectionsToColumns(ingredientSections)
    const directionSections = groupDirectionsBySection(displayRecipe.directions ?? [])
    const useDirectionSectionLayout = directionSections.length > 1

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

    async function handleClean() {
        setAiLoading(true);
        setAiError("");
      
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/recipes/${id}/clean`,
                { method: "POST" }
            );
      
            if (!response.ok) throw new Error("Clean failed");
      
            const data = await response.json();
            setModifiedRecipe(data);
        } catch (err) {
            setAiError("AI Error");
        } finally {
            setAiLoading(false);
        }
    }


    return (
        <main className="styles">

            {/* header */}
            <section className="recipe_header">
                <h1 className="recipe_title">{displayRecipe.name}</h1>

                <div className="recipe_header_footer">
                    <div className="recipe_meta">
                        {displayRecipe.rating != null && (
                            <span className="meta_chip meta_chip--rating">
                                <StarRating rating={displayRecipe.rating} num_ratings={displayRecipe.num_ratings} showCount size="md" />
                            </span>
                        )}

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

                    {recipeTags.length > 0 && (
                        <div className="tags_rec">
                            {recipeTags.map(({ id, label }) => (<span key={id} className="tag_rec">{label}</span>))}
                        </div>
                    )}
                </div>

                {/* image */}
                {displayRecipe.image && (
                    <img 
                        src={displayRecipe.image} 
                        alt={displayRecipe.name} 
                        className="recipe_hero_image" 
                    />
                )}
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
                        {aiLoading ? (<><i className="fa-solid fa-spinner fa-spin"/>Loading...</>) : (<>Modify<i className="fa-solid fa-pen-to-square"/></>)}
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
                <div className="legend_content">
                    <div className="legend_row">
                        <span className="legend_row_label">Food types</span>
                        <div className="ingredient_legend">
                            {INGREDIENT_LEGEND.map(({ type, label }) => (<span key={type} className={`legend_item legend_item--${type}`}>{label}</span>))}
                        </div>
                    </div>
                    <div className="legend_row">
                        <span className="legend_row_label">Dietary</span>
                        <div className="ingredient_icon_legend">
                            <span className="icon_legend_item">
                                <span className="allergen_icon icon_legend_icon" aria-hidden="true">
                                    <span className="material-symbols-outlined">allergies</span>
                                </span>
                                {ALLERGEN_LEGEND[0].label}
                            </span>
                            {DIETARY_LEGEND.map((d) => (
                                <span key={d.id} className="icon_legend_item">
                                    <span className={`dietary_icon dietary_icon--${d.id} icon_legend_icon`} aria-hidden="true">
                                        <i className={`fa-solid ${d.iconClass}`} />
                                    </span>
                                    {d.label}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
                {useSectionLayout ? (
                    <>
                        <div className="ingredients_sections_stack">
                            {ingredientSections.map((section, sectionIndex, sections) => {
                                // calculate start index
                                const startIndex = sections.slice(0, sectionIndex).reduce((sum, s) => sum + s.ingredients.length, 0);
                                return (
                                    <IngredientSectionPanel
                                        key={sectionKey(section, sectionIndex)}
                                        section={section}
                                        sectionIndex={sectionIndex}
                                        startIndex={startIndex}
                                        modifiedIndices={modifiedIngredientIndices}
                                    />
                                );
                            })}
                        </div>
                        <div className="ingredients_sections_grid">
                            <div className="ingredients_sections_column">
                                {leftSections.map((section, sectionIndex, sections) => {
                                    // Need startIndex for left sections too – we can compute it from the full ingredientSections array
                                    // But leftSections is a subset; we need the global start index.
                                    // Better: compute from the full ingredientSections by finding the section's position.
                                    // Simpler: use the same approach but we need the global index of each section.
                                    // Since we have ingredientSections (full list), we can find the start index by looking up the section in the full list.
                                    const fullIndex = ingredientSections.findIndex(s => s === section);
                                    const startIndex = ingredientSections
                                        .slice(0, fullIndex)
                                        .reduce((sum, s) => sum + s.ingredients.length, 0);
                                    return (
                                        <IngredientSectionPanel
                                            key={sectionKey(section, sectionIndex)}
                                            section={section}
                                            sectionIndex={sectionIndex}
                                            startIndex={startIndex}
                                            modifiedIndices={modifiedIngredientIndices}
                                        />
                                    );
                                })}
                            </div>
                            <div className="ingredients_sections_column">
                                {rightSections.map((section, sectionIndex, sections) => {
                                    const fullIndex = ingredientSections.findIndex(s => s === section);
                                    const startIndex = ingredientSections
                                        .slice(0, fullIndex)
                                        .reduce((sum, s) => sum + s.ingredients.length, 0);
                                    return (
                                        <IngredientSectionPanel
                                            key={`right-${sectionKey(section, sectionIndex)}`}
                                            section={section}
                                            sectionIndex={sectionIndex}
                                            startIndex={startIndex}
                                            modifiedIndices={modifiedIngredientIndices}
                                        />
                                    );
                                })}
                            </div>
                        </div>
                    </>
                ) : (
                    <ul className="ingredients_list">
                        {displayRecipe.ingredients?.map((ing: Ingredient, index: number) => (
                            <IngredientTile
                                key={`ing-${index}`}
                                ing={ing}
                                isModified={modifiedIngredientIndices.has(index)}
                            />
                        ))}
                    </ul>
                )}
            </section>
            
            {/* directions */}
            <section className="directions">
                <h2 className="directions_title"> Directions <i className="fa-solid fa-list-check" /></h2>
                {useDirectionSectionLayout ? (
                    <div className="directions_sections_stack">
                        {directionSections.map((section, sectionIndex, sections) => {
                            // calculate start index
                            const startIndex = sections
                                .slice(0, sectionIndex)
                                .reduce((sum, s) => sum + s.steps.length, 0);
                            return (
                                <DirectionSectionPanel
                                    key={directionSectionKey(section, sectionIndex)}
                                    section={section}
                                    sectionIndex={sectionIndex}
                                    startIndex={startIndex}
                                    modifiedIndices={modifiedDirectionIndices}
                                />
                            );
                        })}
                    </div>
                ) : (
                    <ol className="directions_list">
                        {displayRecipe.directions
                            ?.filter((step: Instruction) => step.direction && step.direction.trim() !== '')
                            .map((step: Instruction, index: number) => {
                                const isModified = modifiedDirectionIndices.has(index);
                                return (
                                    <li key={`${step.step_num}-${index}`} className="direction_tile">
                                        <span className="direction_step">{step.step_num}</span>
                                        <p className="direction_text">
                                            {step.direction}
                                            {isModified && (
                                                <i
                                                    className="fa-solid fa-pen-to-square"
                                                    style={{ marginLeft: '6px', color: '#2D6A4F', fontSize: '0.8rem' }}
                                                />
                                            )}
                                        </p>
                                    </li>
                                );
                            })
                        }
                    </ol>
                )}
            </section>

        </main>
    )

}