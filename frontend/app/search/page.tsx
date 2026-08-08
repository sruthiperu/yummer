"use client"

import {useSearchParams, useRouter} from "next/navigation"
import {useState} from "react"
import {useSearch} from "@/lib/useSearch"

import RecipeCard from "../recipe_card"
import SearchBar from "../search_bar"
import CuratedTagFilters from "@/lib/tag_filters"
import "./search.css"
import LoadingAnimation from "@/lib/loadingAnimation";


export default function SearchPage() {
    
    const router = useRouter()

    const searchParams = useSearchParams()
    const query = searchParams.get("q") || ""
    const tagsParam = searchParams.get("tags") || ""
    const selectedTags = tagsParam ? tagsParam.split(",") : []
    
    const [maxTime, setMaxTime] = useState<number | undefined>()
    const [maxCalories, setMaxCalories] = useState<number | undefined>()
    
    const page = Number(searchParams.get("page") || 1)
    const {data, isFetching, isError} = useSearch(query, {
        tags: tagsParam, 
        max_time: maxTime, 
        max_calories: maxCalories
    }, page)

    const showLoading = isFetching && !data

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
                    {/* when there are results */}
                    {!showLoading && data && data.total > 0 && (
                        <div className="res_header">
                            <p className="res_count">{data.total} recipes</p>
                        </div>
                    )}
                    {showLoading && <LoadingAnimation key={query + page} text="Cooking up some recipes for you!"/>}

                    {isError && (
                        <div className="error">
                            <p className="error_title">Something went wrong</p>
                            <p className="error_subtitle">Please try again in a moment</p>
                        </div>
                    )}

                    {/* when there aren't any results */}
                    {!showLoading && data?.total === 0 && (
                        <div className="empty">
                            <p className="empty_title">Sorry, no recipes found!</p>
                        </div>
                    )}

                    {!showLoading && data && data.results?.length > 0 && (
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
                                    link={recipe.link}
                                    match_score={recipe.match_score}
                                />))}
                            </div>
                            
                            {data.total > 20 && (
                                <div className="page_split">
                                    <button
                                        disabled={page <= 1}
                                        onClick={() => {
                                            const params = new URLSearchParams(searchParams.toString())
                                            params.set("page", String(page - 1))
                                            router.push(`/search?${params.toString()}`)
                                            window.scrollTo({top: 0, behavior: "smooth"})
                                        }}
                                        className="page_btn"
                                    >
                                        <i className="fa-solid fa-arrow-left" />
                                    </button>

                                    <button
                                        disabled={page * 20 >= data.total}
                                        onClick={() => {
                                            const params = new URLSearchParams(searchParams.toString())
                                            params.set("page", String(page + 1))
                                            router.push(`/search?${params.toString()}`)
                                            window.scrollTo({top: 0, behavior: "smooth"})
                                        }}
                                        className="page_btn"
                                    >
                                        <i className="fa-solid fa-arrow-right" />
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

        </main>
    )
}
