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
import {groupDirectionsBySection, directionSectionKey, filterRealDirectionSteps} from "@/lib/directionSections"
import type {Ingredient, Instruction, Recipe} from "@/types/recipe"
import type {IngredientSection} from "@/lib/ingredientSections"
import type {DirectionSection} from "@/lib/directionSections"
import StarRating from "@/lib/StarRating"
import CleanProgressLoading from "@/lib/cleanProgressLoading";


function AiEditMarker() {
    return (
        <span
            className="ai_edit_marker"
            data-tooltip="Modified by AI"
            aria-label="Modified by AI"
            tabIndex={0}
        >
            <i className="fa-solid fa-pen-to-square ai_edit_pen" aria-hidden="true" />
        </span>
    );
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
                            <p className="direction_text">{step.direction}</p>
                            {isModified && <AiEditMarker />}
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
    showFoodTypes,
    showDietary,
} : {
    section: IngredientSection;
    sectionIndex: number;
    startIndex: number;
    modifiedIndices: Set<number>;
    showFoodTypes: boolean;
    showDietary: boolean;
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
                            showFoodTypes={showFoodTypes}
                            showDietary={showDietary}
                        />
                    );
                })}
            </ul>
        </div>
    );
}

function IngredientTile({
    ing,
    isModified,
    showFoodTypes = false,
    showDietary = false,
}: {
    ing: Ingredient;
    isModified?: boolean;
    showFoodTypes?: boolean;
    showDietary?: boolean;
}) {
    const qtyParts = [ing.quantity, ing.unit].filter(Boolean);
    const qtyRaw = ing.container_size
        ? `${qtyParts.join(" ")} (${ing.container_size})`
        : qtyParts.join(" ");
    const qty = qtyRaw.toLowerCase();
    const name = ((ing.name && ing.name.trim()) || "Unknown ingredient").toLowerCase();
    const typeClass = showFoodTypes ? ingredientTypeClass(ing.food_type) : "neutral";
    const allergens = displayAllergens(ing.allergens);
    const allergenTooltip = allergenContainsText(allergens);
    const dietaryIcons = displayDietaryIcons(ing);
    const showIcons = showDietary && (allergens.length > 0 || dietaryIcons.length > 0);

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
            <span className="ingredient_name">{name}</span>
            {(showIcons || isModified) && (
                <div className="ingredient_tile_trailing">
                    {showIcons && (
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
                    {isModified && <AiEditMarker />}
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
    const [modifiedRecipe, setModifiedRecipe] = useState<Recipe | null>(null)      /* AI modifies, or null */
    const [baselineRecipe, setBaselineRecipe] = useState<Recipe | null>(null)      /* cleaned (or pre-modify) baseline */
    const [wasCleaned, setWasCleaned] = useState(false)
    const [modifyLoading, setModifyLoading] = useState(false)
    const [cleanLoading, setCleanLoading] = useState(false)
    const [cleanError, setCleanError] = useState("")
    const [aiError, setAiError] = useState("")
    const [showFoodTypes, setShowFoodTypes] = useState(false)
    const [showDietary, setShowDietary] = useState(false)

    const shouldClean = searchParams.get("cleaned") === "1";

    useEffect(() => {
        if (shouldClean && recipe && !modifiedRecipe && !cleanError) {
            handleClean();
        }
    }, [shouldClean, recipe, modifiedRecipe, cleanError]);

    if (cleanLoading) {
        return (
            <div className="ai_loading_overlay">
                <CleanProgressLoading />
            </div>
        );
    }
    if (isLoading) return <div>Loading...</div>
    if (isError || !recipe) return <div>Recipe not found</div>
    if (cleanError && !wasCleaned && !modifiedRecipe) {
        return (
            <div className="ai_loading_overlay">
                <p className="clean_error_msg">{cleanError}</p>
            </div>
        );
    }

    const displayRecipe = modifiedRecipe || recipe;

    // Pens only after Modify changes the baseline (Clean alone sets both to the same object)
    const showEditMarks = Boolean(baselineRecipe && modifiedRecipe && modifiedRecipe !== baselineRecipe);
    const displayDirections = filterRealDirectionSteps(displayRecipe.directions)
    const modifiedIngredientIndices = new Set<number>(
        showEditMarks
            ? (displayRecipe.ingredients ?? [])
                .map((ing, i) => (ing.modified ? i : -1))
                .filter((i) => i >= 0)
            : [],
    );
    const modifiedDirectionIndices = new Set<number>(
        showEditMarks
            ? displayDirections
                .map((step, i) => (step.modified ? i : -1))
                .filter((i) => i >= 0)
            : [],
    );

    const nutritionKeys = ["calories", "protein", "carbs", "total_fat", "sugar"] as const;
    const nutritionChanged = nutritionKeys.reduce((acc, key) => {
        acc[key] = showEditMarks && Boolean(displayRecipe.nutrition_modified?.[key]);
        return acc;
    }, {} as Record<(typeof nutritionKeys)[number], boolean>);

    const recipeTags = formatRecipeTags(displayRecipe.tags)
    const ingredientSections = groupIngredientsBySection(displayRecipe.ingredients ?? [])
    const useSectionLayout = ingredientSections.length > 1
    const [leftSections, rightSections] = distributeSectionsToColumns(ingredientSections)
    const directionSections = groupDirectionsBySection(displayDirections)
    const useDirectionSectionLayout = directionSections.length > 1

    const timeChanged = showEditMarks && Boolean(displayRecipe.total_time_modified);
    const servingsChanged = showEditMarks && Boolean(displayRecipe.servings_modified);

    async function handleModify() {
        if (!message.trim()) {
            return
        }
        // Always lock current on-screen recipe as pen baseline for this edit
        setBaselineRecipe(displayRecipe);
        setModifyLoading(true)
        setAiError("")

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/recipes/${id}/modify`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message,
                    recipe: {
                        name: displayRecipe.name,
                        ingredients: displayRecipe.ingredients,
                        directions: displayRecipe.directions,
                        nutrition: displayRecipe.nutrition,
                        total_time: displayRecipe.total_time,
                        servings: displayRecipe.servings,
                    },
                }),
            })

            const data = await response.json().catch(() => ({}))
            if (!response.ok) {
                const detail = typeof data?.detail === "string" ? data.detail : null
                setAiError(detail || (response.status === 429
                    ? "Sorry! You've reached your token limit for the day. Check back in tomorrow!"
                    : "AI Error"))
                return
            }

            if (data.conflict) {
                setAiError(data.conflict)
            } else {
                setModifiedRecipe(data)
            }
        } catch (err) {
            setAiError("AI Error")
        } finally {
            setModifyLoading(false)
        }
    }

    async function handleClean() {
        setCleanLoading(true);
        setCleanError("");
        setAiError("");
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/recipes/${id}/clean`, {
                method: "POST",
                credentials: "include",
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                const detail = typeof data?.detail === "string" ? data.detail : null;
                setCleanError(detail || (response.status === 429
                    ? "Sorry! You've reached your token limit for the day. Check back in tomorrow!"
                    : "AI Error"));
                return;
            }
            setCleanError("");
            setModifiedRecipe(data);
            setBaselineRecipe(data);
            setWasCleaned(true);
        } catch (err) {
            setCleanError("AI Error");
        } finally {
            setCleanLoading(false);
        }
    }

    function handleRestore() {
        if (baselineRecipe) {
            setModifiedRecipe(baselineRecipe);
        } else {
            setModifiedRecipe(null);
        }
        setAiError("");
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
                                {timeChanged && <AiEditMarker />}
                            </span>
                        )}
                        {displayRecipe.servings && (
                            <span className="meta_chip meta_chip--servings">
                                <i className="fa-solid fa-user-group" />
                                {displayRecipe.servings} {displayRecipe.servings === 1 ? "serving" : "servings"}
                                {servingsChanged && <AiEditMarker />}
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
                        <p className="chatbox_subtitle">Make it gluten-free, higher in protein, adjust servings, lower calories, or anything else.</p>
                    </div>
                </div>

                <div className="user_input">
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && !modifyLoading && handleModify()}
                        placeholder="How would you like to change this recipe?"
                        disabled={modifyLoading}
                        className="chatbox_input"
                    />
                    <button onClick={handleModify} disabled={modifyLoading || !message.trim()} className="change_btn">
                        {modifyLoading ? (<><i className="fa-solid fa-spinner fa-spin"/>Loading...</>) : (<>Modify<i className="fa-solid fa-pen-to-square"/></>)}
                    </button>
                </div>

                {aiError && <p className="error_msg">{aiError}</p>}

                {showEditMarks && (
                    <>
                        <div className="success_msg">
                            <span className="success_text">
                                <i className="fa-solid fa-circle-check"/> Recipe modified
                            </span>
                            <button onClick={handleRestore} className="restore_btn">
                                {"Restore original"}
                            </button>
                        </div>
                        <p className="ai_disclaimer">
                            <i className="fa-solid fa-triangle-exclamation"></i> 
                            This recipe was modified by AI. Recipes may occasionally be misleading; please review carefully before cooking.
                        </p>
                        <a className="report_issue" href="mailto:sruthiperumalla1107@gmail.com">
                            Report an issue
                        </a>
                    </>
                )}
            </section>

            {/* nutrition */}
            {displayRecipe.nutrition && (
                <section className="nutrition_info">
                    <h2 className="nutrition_title">Nutrition <i className="fa-brands fa-nutritionix"></i></h2>
                    <div className="nutrition_layout">
                        {([
                            { label: "Calories", key: "calories" as const, value: formatNutritionWhole(displayRecipe.nutrition.calories) },
                            { label: "Protein", key: "protein" as const, value: formatNutritionGramsDecimal(displayRecipe.nutrition.protein) },
                            { label: "Carbs", key: "carbs" as const, value: formatNutritionGrams(displayRecipe.nutrition.carbs) },
                            { label: "Fat", key: "total_fat" as const, value: formatNutritionGrams(displayRecipe.nutrition.total_fat) },
                            { label: "Sugar", key: "sugar" as const, value: formatNutritionGrams(displayRecipe.nutrition.sugar) },
                        ]).map(({ label, key, value }) => (
                            <div key={label} className="nutrition_card">
                                <div className="nutrition_label">{label}</div>
                                <div className="nutrition_val">
                                    {value}
                                    {nutritionChanged[key] && <AiEditMarker />}
                                </div>
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
                        <label className="legend_check">
                            <input
                                type="checkbox"
                                checked={showFoodTypes}
                                onChange={(e) => setShowFoodTypes(e.target.checked)}
                            />
                            <span className="legend_check_box" aria-hidden="true" />
                            <span className="legend_check_label">Food types</span>
                        </label>
                        <div className="ingredient_legend">
                            {INGREDIENT_LEGEND.map(({ type, label }) => (
                                <span key={type} className={`legend_item legend_item--${type}`}>{label}</span>
                            ))}
                        </div>
                    </div>
                    <div className="legend_row">
                        <label className="legend_check">
                            <input
                                type="checkbox"
                                checked={showDietary}
                                onChange={(e) => setShowDietary(e.target.checked)}
                            />
                            <span className="legend_check_box" aria-hidden="true" />
                            <span className="legend_check_label">Dietary</span>
                        </label>
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
                                        showFoodTypes={showFoodTypes}
                                        showDietary={showDietary}
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
                                            showFoodTypes={showFoodTypes}
                                            showDietary={showDietary}
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
                                            showFoodTypes={showFoodTypes}
                                            showDietary={showDietary}
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
                                showFoodTypes={showFoodTypes}
                                showDietary={showDietary}
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
                        {displayDirections.map((step: Instruction, index: number) => {
                            const isModified = modifiedDirectionIndices.has(index);
                            return (
                                <li key={`direction-${index}`} className="direction_tile">
                                    <span className="direction_step">{index + 1}</span>
                                    <p className="direction_text">{step.direction}</p>
                                    {isModified && <AiEditMarker />}
                                </li>
                            );
                        })}
                    </ol>
                )}
            </section>

        </main>
    )

}