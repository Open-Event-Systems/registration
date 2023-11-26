import {
  RegistrationAPI,
  RegistrationSearchResult,
} from "#src/features/registration"
import {
  UndefinedInitialDataInfiniteOptions,
  UseInfiniteQueryOptions,
} from "@tanstack/react-query"
import { makeAutoObservable, reaction } from "mobx"
import { createContext } from "react"

export class Search {
  query = ""
  showAll = false
  eventId: string | null = null
  queryOptions: UndefinedInitialDataInfiniteOptions<RegistrationSearchResult[]>

  constructor(
    private api: RegistrationAPI,
    eventId: string | null = null,
  ) {
    this.eventId = eventId

    this.queryOptions = {
      ...this.api.list(this.query, { event_id: eventId, all: this.showAll }),
      queryFn: () => [],
      placeholderData: {
        pages: [],
        pageParams: [],
      },
    }

    makeAutoObservable(this)

    reaction(
      () => [this.query, this.eventId, this.showAll],
      () => this.search(),
      {
        delay: 500,
      },
    )
  }

  private search() {
    const query = this.query
    const eventId = this.eventId
    const showAll = this.showAll
    this.queryOptions = {
      ...this.api.list(query, { event_id: eventId, all: showAll }),
      placeholderData(prev) {
        return prev
      },
    }
  }
}

export const SearchContext = createContext<Search | undefined>(undefined)
