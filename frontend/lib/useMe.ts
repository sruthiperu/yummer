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
  return useQuery<User | null>({
    queryKey: ["me"],
    queryFn: async () => {
      try {
        return await getMe()
      } catch {
        return null
      }
    },
    retry: false,
    staleTime: 300000,
  })
}

