import { Loader, createLoader } from "#src/features/loader"
import {
  RegistrationAPI,
  RegistrationSearchResult as IRegistrationSearchResult,
  NextFunc,
} from "#src/features/registration"
import { action, makeAutoObservable, observable } from "mobx"

export class ResultStore {
  next: Loader<ResultStore> | undefined = undefined

  constructor(
    public registrations: IRegistrationSearchResult[],
    next?: NextFunc,
    public prev?: ResultStore,
  ) {
    if (next) {
      this.next = createLoader(() =>
        next().then(([items, next]) => new ResultStore(items, next, this)),
      )
    }
  }
}

export class SearchStore {
  curResults: Loader<ResultStore> | undefined = undefined
  private query = ""

  constructor(
    private api: RegistrationAPI,
    private eventId?: string,
  ) {
    makeAutoObservable<this, "eventId">(this, {
      curResults: observable.ref,
      eventId: false,
    })
  }

  async search(query: string): Promise<ResultStore> {
    this.query = query
    const loader = createLoader(
      this.api
        .search(query, { event_id: this.eventId })
        .then(([items, next]) => new ResultStore(items, next)),
    )

    if (!this.curResults) {
      this.curResults = loader
      return loader
    } else {
      return loader.then(
        action((res) => {
          if (this.query == query) {
            this.curResults = loader
          }
          return res
        }),
      )
    }
  }
}
