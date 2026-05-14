import {Recipe} from "@/types/recipe"

const API_URL = process.env.NEXT_PUBLIC_API_URL

// define user type
export type User = {
  id: number
  name: string
  email: string
  dietary_restrictions?: any
  allergens?: string[]
}
export type SearchResponse = {
  results: Recipe[]
  total: number
  suggestions?: string[]
  empty_reason?: string
}

// fetch wrapper
async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options, credentials: "include", 
    headers: {"Content-Type": "application/json", ...options?.headers,},
  })

  if (!response.ok) throw new Error(`API error: ${response.status}`)
  return response.json()
}

// recipes
export async function getRecipe(id: number): Promise<Recipe> {
  return fetchJSON(`${API_URL}/recipes/${id}`)
}
export async function modifyRecipe(id: number, message: string) {
  return fetchJSON(`${API_URL}/recipes/${id}/modify`, {
    method: "POST",
    body: JSON.stringify({message}),
  })
}

// search
export async function searchRecipes(query: string, params: Record<string, any> = {}) {
  const searchParams = new URLSearchParams()
  searchParams.set("q", query)

  // only add params with actual values
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== false && value !== "") {
      searchParams.set(key, String(value))
    }
  })

  const url = `${API_URL}/search?${searchParams.toString()}`

  return fetchJSON<SearchResponse>(url)
}
// search by ingredients
export async function searchByIngredients(ingredients: string, params: Record<string, any> = {}) {
  const searchParams = new URLSearchParams()
  searchParams.set("ingredients", ingredients)

  // only add params with actual values
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== false && value !== "") {
      searchParams.set(key, String(value))
    }
  })

  const url = `${API_URL}/search/by-ingredients?${searchParams.toString()}`

  return fetchJSON<SearchResponse>(url)
}


// favorites
export async function getFavorites() {
  return fetchJSON(`${API_URL}/users/me/favorites`)
}
export async function addFavorite(recipeId: number, modifiedRecipe?: any) {
  return fetchJSON(`${API_URL}/users/me/favorites`, {
    method: "POST",
    body: JSON.stringify({ recipe_id: recipeId, modified_recipe: modifiedRecipe ?? null }),
  })
}
export async function removeFavorite(recipeId: number) {
  return fetchJSON(`${API_URL}/users/me/favorites/${recipeId}`, {
    method: "DELETE",
  })
}

// user profile
export async function getMe(): Promise<User>{
  return fetchJSON(`${API_URL}/users/me`)
}
export async function updateMe(data: { dietary_restrictions?: any; allergens?: string[] }) {
  return fetchJSON(`${API_URL}/users/me`, {
    method: "PATCH",
    body: JSON.stringify(data),
  })
}