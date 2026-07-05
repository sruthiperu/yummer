"use client"

import {useSearchParams, useRouter} from "next/navigation"
import {useState} from "react"
import {useQuery} from "@tanstack/react-query"
import {searchByIngredients} from "@/lib/api"

import RecipeCard from "../../recipe_card"
import SearchBar from "../../search_bar"

import "../search.css"


export default function IngredientSearchPage() {
    
    const router = useRouter()

    // read ingredients from url
    const searchParams = useSearchParams()
    const ingredients = searchParams.get("ingredients") || ""
    const user_ingredients = ingredients.split(",")// .map(i => i.trim().toLowerCase()).filter(Boolean)
    
    const [sort, setSort] = useState("relevance")
    const page = Number(searchParams.get("page") || 1)
    
    const {data, isLoading, isError} = useQuery({
        queryKey: ["ingredient-search", ingredients, page, sort],
        queryFn: () => searchByIngredients(ingredients, {page, sort}),
        enabled: ingredients.length >= 2,
        staleTime: 1000 * 60 * 2,
    })

    return (
        <main className="search_page">

            {/* search bar */}
            <SearchBar defaultValue={ingredients}/>
            

            {/* header for results */}
            {!isLoading && data && (
                <div className="res_header">
                    <p className="res_count">{data.total > 0 ? `${data.total} results for "${ingredients}"` : `No results for "${ingredients}"`}</p>

                    {data.total > 0 && (
                        <select value={sort} onChange={e => setSort(e.target.value)} className="sort_select">
                            <option value="relevance">Best match</option>
                            <option value="quickest">Quickest first</option>
                            <option value="newest">Latest</option>
                            <option value="calories_asc">Lowest calories</option>
                        </select>
                    )}
                </div>
            )}

            {isLoading && (
                <div className="res_grid">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="skeleton_card" />
                    ))}
                </div>
            )}

            {/* error */}
            {isError && (
                <div className="error">
                    <p className="error_title">Something went wrong</p>
                    <p className="error_subtitle">Please try again in a moment</p>
                </div>
            )}

            {/* empty */}
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
                            user_match_pct={recipe.user_match_pct}
                            missing_ings={recipe.missing_ingredients}
                            recipe_ings={recipe.ingredients}
                            user_ings={user_ingredients}
                        />))}
                    </div>
                    
                    {/* splitting up pages */}
                    <div className="page_split">

                        {/* prev button */}
                        <button
                            disabled={page <= 1}
                            onClick={() => {
                                router.push(`/search/by-ingredients?ingredients=${encodeURIComponent(ingredients)}&page=${page - 1}`)
                            }}
                            className="page_btn"
                        >Previous</button>

                        {/* next button */}
                        <button
                            disabled={data.results.length < 20}
                            onClick={() => {
                                router.push(`/search/by-ingredients?ingredients=${encodeURIComponent(ingredients)}&page=${page + 1}`)
                            }}
                            className="page_btn"
                        >Next</button>

                    </div>
                </>
            )}

        </main>
    )
}