import { RegistrationSearchResult } from "#src/features/registration"
import { makeAutoObservable } from "mobx"
import { createContext } from "react"

export class Search {
  query = ""
  eventId: string | null = null
  showAll = false
  results: RegistrationSearchResult[] = []

  constructor() {
    makeAutoObservable(this)
  }
}

export const SearchContext = createContext<Search | undefined>(undefined)
