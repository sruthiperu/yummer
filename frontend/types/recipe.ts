// define types

export type Instruction = {
    step_num: number
    direction: string
}

export type Nutrition = {
    calories: number
    total_fat: number
    sugar: number
    sodium: number
    protein: number
    saturated_fat: number
    carbs: number
}

export type Recipe = {
    id: number
    name: string
    description: string | null
    directions: Instruction[]
    total_time: number | null
    servings: number | null
    nutrition: Nutrition | null
    tags: string[] | null
    date: string | null
    link: string | null
    ingredients?: Ingredient[]
}

export type Ingredient = {
    id: number
    name: string
    quantity: string | null
    unit: string | null
    container_size?: string | null
    raw_ingredient: string | null
    food_type?: string | null
    allergens?: string[] | null
    is_vegan?: boolean | null
    is_vegetarian?: boolean | null
    is_gluten_free?: boolean | null
}