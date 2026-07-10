import {useQuery} from "@tanstack/react-query"
import {searchRecipes, SearchResponse} from "@/lib/api"

export function useSearch(query: string, filters: Record<string, any> = {}, page: number = 1) { 
    return useQuery<SearchResponse>({
        queryKey: ["search", query, {...filters}, page],
        queryFn: () => searchRecipes(query, {...filters, page}),
        enabled: query.length >= 2,
        staleTime: 1000 * 60 * 2,       // 2 min
    })
}