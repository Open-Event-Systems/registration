import {
  NextFunc,
  RegistrationAPI,
  RegistrationSearchResult,
} from "#src/features/registration"
import { makeAutoObservable, reaction, runInAction } from "mobx"
import { createContext } from "react"

export class Search {
  query = ""
  showAll = false
  results: RegistrationSearchResult[] = []
  private next: NextFunc | null = null

  get handleMore(): (() => Promise<void>) | undefined {
    return this.next ? () => this.more() : undefined
  }

  constructor(
    private api: RegistrationAPI,
    public eventId: string | null = null,
  ) {
    makeAutoObservable(this)

    reaction(
      () => [this.query, this.eventId, this.showAll],
      () => this.search(),
      {
        delay: 500,
      },
    )
  }

  private async search() {
    const query = this.query
    const eventId = this.eventId
    const showAll = this.showAll
    const [items, next] = await this.api.search(query, {
      event_id: eventId ?? undefined,
      all: showAll || undefined,
    })

    if (
      this.query != query ||
      this.eventId != eventId ||
      this.showAll != showAll
    ) {
      return
    }

    runInAction(() => {
      this.next = next
      this.results = items
    })
  }

  private async more() {
    const next = this.next
    if (!next) {
      return
    }

    const [items, newNext] = await next()

    if (this.next != next) {
      return
    }

    runInAction(() => {
      this.next = newNext
      this.results.push(...items)
    })
  }
}

export const SearchContext = createContext<Search | undefined>(undefined)
