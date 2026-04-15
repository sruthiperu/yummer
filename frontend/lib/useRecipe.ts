import {useQuery} from "@tanstack/react-query"
import {getRecipe} from "@/lib/api"

export function useRecipe(id: number) {
  return useQuery({
    queryKey: ["recipe", id],
    queryFn: () => getRecipe(id),
    enabled: !!id,
  })
}