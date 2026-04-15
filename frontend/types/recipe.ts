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
    raw_ingredient: string | null
}