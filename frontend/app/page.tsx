"use client"

import {useState} from "react"
import {useRouter} from "next/navigation"

export default function HomePage() {
  const [recipeId, setRecipeId] = useState("")
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (recipeId.trim()) router.push(`/recipes/${recipeId}`)
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4">
      <h1 className="text-4xl font-bold mb-8">Recipe App</h1>
      <form onSubmit={handleSubmit} className="w-full max-w-md">
        <input
          type="text"
          value={recipeId}
          onChange={(e) => setRecipeId(e.target.value)}
          placeholder="Enter recipe ID (e.g. 1)"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4"
        />
        <button
          type="submit"
          className="w-full px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800"
        >
          View Recipe
        </button>
      </form>
    </div>
  )
}