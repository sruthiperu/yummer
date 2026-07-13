"use client"

import {useSearchParams, useRouter} from "next/navigation"
import {useState} from "react"
import {useQuery} from "@tanstack/react-query"
import {searchByIngredients} from "@/lib/api"

import RecipeCard from "../../recipe_card"
import SearchBar from "../../search_bar"
import CuratedTagFilters from "@/lib/tag_filters"
import "../search.css"


export default function IngredientSearchPage() {
    
    const router = useRouter()

    const searchParams = useSearchParams()
    const ingredients = searchParams.get("ingredients") || ""
    const user_ingredients = ingredients.split(",")
    const tagsParam = searchParams.get("tags") || ""
    const selectedTags = tagsParam ? tagsParam.split(",") : []
    
    const [maxTime, setMaxTime] = useState<number | undefined>()
    const [maxCalories, setMaxCalories] = useState<number | undefined>()
    
    const page = Number(searchParams.get("page") || 1)
    
    const {data, isLoading, isError} = useQuery({
        queryKey: ["ingredient-search", ingredients, page, tagsParam, maxTime, maxCalories],
        queryFn: () => searchByIngredients(ingredients, {
            page, 
            tags: tagsParam,
            max_time: maxTime,
            max_calories: maxCalories
        }),
        enabled: ingredients.length >= 2,
        staleTime: 1000 * 60 * 2,
    })

    const handleTagsChange = (newTags: string[]) => {
        const params = new URLSearchParams()
        params.set("ingredients", ingredients)
        if (newTags.length > 0) {
            params.set("tags", newTags.join(","))
        }
        params.set("page", "1")
        router.push(`/search/by-ingredients?${params.toString()}`)
    }

    return (
        <main className="search_page">

            <SearchBar defaultValue={ingredients}/>

            <div className="search_layout">
                {/* Left filter panel */}
                <CuratedTagFilters 
                    selected={selectedTags} 
                    onChange={handleTagsChange}
                    maxTime={maxTime}
                    onMaxTimeChange={setMaxTime}
                    maxCalories={maxCalories}
                    onMaxCaloriesChange={setMaxCalories}
                />
                
                {/* Right content area */}
                <div className="search_content">
                    {!isLoading && data && (
                        <div className="res_header">
                            <p className="res_count">{data.total > 0 ? `${data.total} results for "${ingredients}"` : `No results for "${ingredients}"`}</p>
                        </div>
                    )}

                    {isLoading && (
                        <div className="res_grid">
                            {Array.from({ length: 6 }).map((_, i) => (
                                <div key={i} className="skeleton_card" />
                            ))}
                        </div>
                    )}

                    {isError && (
                        <div className="error">
                            <p className="error_title">Something went wrong</p>
                            <p className="error_subtitle">Please try again in a moment</p>
                        </div>
                    )}

                    {!isLoading && data?.total === 0 && (
                        <div className="empty">
                            <p className="empty_title">No recipes found for &quot;{ingredients}&quot;</p>

                            {data.suggestions && data.suggestions.length > 0 && (
                                <ul className="suggestions_list">
                                {data.suggestions.map((s: string) => (
                                    <li key={s} className="suggestion_item">→ {s}</li>
                                ))}
                                </ul>
                            )}
                        </div>
                    )}

                    {!isLoading && data && data.results?.length > 0 && (
                        <>
                            <div className="res_grid">
                                {data.results.map((recipe: any) => (<RecipeCard
                                    key={recipe.id}
                                    id={recipe.id}
                                    name={recipe.name}
                                    total_time={recipe.total_time}
                                    nutrition={recipe.nutrition}
                                    tags={recipe.tags}
                                    rating={recipe.rating}
                                    num_ratings={recipe.num_ratings}
                                    image={recipe.image}
                                    user_match_pct={recipe.user_match_pct}
                                    missing_ings={recipe.missing_ingredients}
                                    recipe_ings={recipe.ingredients}
                                    user_ings={user_ingredients}
                                />))}
                            </div>
                            
                            <div className="page_split">
                                <button
                                    disabled={page <= 1}
                                    onClick={() => {
                                        const params = new URLSearchParams(searchParams.toString())
                                        params.set("page", String(page - 1))
                                        router.push(`/search/by-ingredients?${params.toString()}`)
                                    }}
                                    className="page_btn"
                                >Previous</button>

                                <button
                                    disabled={data.results.length < 20}
                                    onClick={() => {
                                        const params = new URLSearchParams(searchParams.toString())
                                        params.set("page", String(page + 1))
                                        router.push(`/search/by-ingredients?${params.toString()}`)
                                    }}
                                    className="page_btn"
                                >Next</button>
                            </div>
                        </>
                    )}
                </div>
            </div>

        </main>
    )
}