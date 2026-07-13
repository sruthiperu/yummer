"use client"

import {useSearchParams, useRouter} from "next/navigation"
import {useState} from "react"
import {useSearch} from "@/lib/useSearch"

import RecipeCard from "../recipe_card"
import SearchBar from "../search_bar"
import CuratedTagFilters from "@/lib/tag_filters"
import "./search.css"


export default function SearchPage() {
    
    const router = useRouter()

    const searchParams = useSearchParams()
    const query = searchParams.get("q") || ""
    const tagsParam = searchParams.get("tags") || ""
    const selectedTags = tagsParam ? tagsParam.split(",") : []
    
    const [maxTime, setMaxTime] = useState<number | undefined>()
    const [maxCalories, setMaxCalories] = useState<number | undefined>()
    
    const page = Number(searchParams.get("page") || 1)
    const {data, isLoading, isError} = useSearch(query, {
        tags: tagsParam, 
        max_time: maxTime, 
        max_calories: maxCalories
    }, page)

    const handleTagsChange = (newTags: string[]) => {
        const params = new URLSearchParams()
        params.set("q", query)
        if (newTags.length > 0) {
            params.set("tags", newTags.join(","))
        }
        params.set("page", "1")
        router.push(`/search?${params.toString()}`)
    }

    return (
        <main className="search_page">

            <SearchBar defaultValue={query}/>

            <div className="search_layout">
                {/* left: filter panel */}
                <CuratedTagFilters 
                    selected={selectedTags} 
                    onChange={handleTagsChange}
                    maxTime={maxTime}
                    onMaxTimeChange={setMaxTime}
                    maxCalories={maxCalories}
                    onMaxCaloriesChange={setMaxCalories}
                />
                
                {/* right: recipe grid */}
                <div className="search_content">
                    {!isLoading && data && (
                        <div className="res_header">
                            <p className="res_count">{data.total > 0 ? `${data.total} results for "${query}"` : `No results for "${query}"`}</p>
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
                            <p className="empty_title">No recipes found for &quot;{query}&quot;</p>

                            {data.suggestions && data.suggestions.length > 0 && (
                                <ul className="suggestions_list">
                                {data.suggestions.map((s: string) => (
                                    <li key={s} className="suggestion_item">→ {s}</li>
                                ))}
                                </ul>
                            )}

                            {data.empty_reason === "filters_too_strict" && (
                                <button onClick={() => router.push(`/search?q=${encodeURIComponent(query)}`)} className="rm_filters_btn">
                                    Search without filters
                                </button>
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
                                    match_score={recipe.match_score}
                                />))}
                            </div>
                            
                            <div className="page_split">
                                <button
                                    disabled={page <= 1}
                                    onClick={() => {
                                        const params = new URLSearchParams(searchParams.toString())
                                        params.set("page", String(page - 1))
                                        router.push(`/search?${params.toString()}`)
                                    }}
                                    className="page_btn"
                                >Previous</button>

                                <button
                                    disabled={data.results.length < 20}
                                    onClick={() => {
                                        const params = new URLSearchParams(searchParams.toString())
                                        params.set("page", String(page + 1))
                                        router.push(`/search?${params.toString()}`)
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
