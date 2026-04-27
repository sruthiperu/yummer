import {useQuery} from "@tanstack/react-query"
import {getMe} from "@/lib/api"


// define user type
export type User = {
  id: number
  name: string
  email: string
  dietary_restrictions?: any
  allergens?: string[]
}

export function useMe() {
  // staleTime: 1000 * 60 * 5 -> 5 minutes
  return useQuery<User>({queryKey: ["me"], queryFn: () => getMe(), retry: false, staleTime: 300000})
}

