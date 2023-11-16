import { Loader, createLoader } from "#src/features/loader"
import {
  RegistrationAPI,
  RegistrationSearchResult as IRegistrationSearchResult,
} from "#src/features/registration"
import { action, makeAutoObservable, observable } from "mobx"

export class RegistrationSearchResult {
  next: Loader<RegistrationSearchResult> | undefined = undefined

  get nextAfter(): string | undefined {
    return this.registrations[this.registrations.length - 1]?.id
  }

  constructor(
    api: RegistrationAPI,
    public query: string,
    public registrations: IRegistrationSearchResult[],
    public prev: RegistrationSearchResult | undefined = undefined,
  ) {
    this.prev = prev

    if (this.nextAfter) {
      this.next = createLoader(() => getResults(api, query, this))
    }
  }
}

export class RegistrationSearchStore {
  curResults: Loader<RegistrationSearchResult> | undefined = undefined
  private query = ""

  constructor(private api: RegistrationAPI) {
    makeAutoObservable(this, {
      curResults: observable.ref,
    })
  }

  async search(query: string): Promise<RegistrationSearchResult> {
    const loader = createLoader(getResults(this.api, query))
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

const getResults = async (
  api: RegistrationAPI,
  query: string,
  cur?: RegistrationSearchResult,
): Promise<RegistrationSearchResult> => {
  const results = await api.search(query, { after: cur?.nextAfter })
  return new RegistrationSearchResult(api, query, results, cur)
}
