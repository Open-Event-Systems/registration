import {
  Registration,
  RegistrationCheckout,
  RegistrationSearchResult,
} from "#src/features/registration"
import { PaginatedResult } from "#src/types/api"
import { makeAutoObservable } from "mobx"
import { Wretch } from "wretch"
import queryString from "wretch/addons/queryString"

export class RegistrationStore {
  private registrations = new Map<string, Registration>()

  constructor(public wretch: Wretch) {
    makeAutoObservable(this)
  }

  private set(registration: Registration): Registration {
    this.registrations.set(registration.id, registration)
    return registration
  }

  get(id: string): Registration | undefined {
    return this.registrations.get(id)
  }

  getOrFetch(id: string): Registration | Promise<Registration> {
    const reg = this.get(id)
    if (!reg) {
      return this.read(id)
    } else {
      return reg
    }
  }

  async search(
    query: string,
    options = {},
  ): Promise<PaginatedResult<RegistrationSearchResult[]>> {
    let req = this.wretch.addon(queryString)

    if (query) {
      req = req.query({ q: query })
    }

    for (const [opt, val] of Object.entries(options)) {
      if (val) {
        req = req.query({ [opt]: val })
      }
    }

    return await getSearchResults(req as Wretch)
  }

  async create(registration: Registration): Promise<Registration> {
    const result = await this.wretch
      .json(registration)
      .post()
      .json<Registration>()
    return this.set(result)
  }

  async fromResponse(response: Response): Promise<Registration> {
    const registration = await response.json()
    return this.set(registration)
  }

  async read(id: string): Promise<Registration> {
    const result = await this.wretch.url(`/${id}`).get().json<Registration>()
    return this.set(result)
  }

  async readCheckouts(id: string): Promise<RegistrationCheckout[]> {
    return await this.wretch
      .url(`/${id}/checkouts`)
      .get()
      .json<RegistrationCheckout[]>()
  }

  async update(registration: Registration): Promise<Registration> {
    const headers = {
      "If-Match": `W/"${registration.version}"`,
    }

    const result = await this.wretch
      .url(`/${registration.id}`)
      .json(registration)
      .headers(headers)
      .put()
      .json<Registration>()

    return this.set(result)
  }

  async delete(id: string): Promise<void> {
    await this.wretch.url(`/${id}`).delete().res()
    this.registrations.delete(id)
  }

  async complete(id: string): Promise<Registration> {
    const res = await this.wretch
      .url(`/${id}/complete`)
      .put()
      .json<Registration>()
    return this.set(res)
  }

  async cancel(id: string): Promise<Registration> {
    const res = await this.wretch
      .url(`/${id}/cancel`)
      .put()
      .json<Registration>()
    return this.set(res)
  }
}

const getSearchResults = async (
  wretch: Wretch,
): Promise<PaginatedResult<RegistrationSearchResult[]>> => {
  const res = await wretch.get().res()
  const body = await res.json()

  const linkHeader = res.headers.get("Link")
  const nextMatch = linkHeader
    ? /<(.*?)>; rel="next"/.exec(linkHeader) ?? []
    : []
  const nextUrl = nextMatch[1]

  let next = null
  if (nextUrl) {
    next = () => getSearchResults(wretch.url(nextUrl, true))
  }

  return [body, next]
}
