import {Recipe} from "@/types/recipe"

const API_URL = process.env.NEXT_PUBLIC_API_URL

// fetch wrapper
async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
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
    body: JSON.stringify({ message }),
  })
}

// search
export async function searchRecipes(query: string, filters?: Record<string, any>) {
  let url = `${API_URL}/search?q=${encodeURIComponent(query)}`
  if (filters) url += `&${new URLSearchParams(filters).toString()}`
  return fetchJSON(url)
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
export async function getMe() {
  return fetchJSON(`${API_URL}/users/me`)
}
export async function updateMe(data: { dietary_restrictions?: any; allergens?: string[] }) {
  return fetchJSON(`${API_URL}/users/me`, {
    method: "PATCH",
    body: JSON.stringify(data),
  })
}