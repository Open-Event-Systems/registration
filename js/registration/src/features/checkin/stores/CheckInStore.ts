import { placeholderWretch } from "#src/config/api"
import { makeAutoObservable } from "mobx"
import { createContext } from "react"
import { Wretch } from "wretch"

export class CheckInStore {
  stationId: string | null = null
  printIds = new Set<string>()

  constructor(private wretch: Wretch) {
    makeAutoObservable(this)
  }

  async print(printUrl: string, data: Record<string, unknown>) {
    const id = data.id
    if (typeof id == "string") {
      this.printIds.add(id)
    }

    await this.wretch
      .url(printUrl, true)
      .url(`/printers/default/print`)
      .json(data)
      .post()
      .res()
  }
}

export const CheckInStoreContext = createContext(
  new CheckInStore(placeholderWretch),
)
