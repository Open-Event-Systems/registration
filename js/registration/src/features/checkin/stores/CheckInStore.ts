import { placeholderWretch } from "#src/config/api"
import { makeAutoObservable } from "mobx"
import { createContext } from "react"
import { Wretch } from "wretch"

export class CheckInStore {
  stationId: string | null = null
  printer: string | null = null
  printIds = new Set<string>()

  constructor(private wretch: Wretch) {
    makeAutoObservable(this)
  }

  async getPrinters(printUrl: string): Promise<{ id: string; name: string }[]> {
    return await this.wretch
      .url(printUrl, true)
      .url("/printers")
      .get()
      .json<{ id: string; name: string }[]>()
  }

  async print(
    printUrl: string,
    printer: string,
    data: Record<string, unknown>,
  ) {
    const id = data.id
    if (typeof id == "string") {
      this.printIds.add(id)
    }

    await this.wretch
      .url(printUrl, true)
      .url(`/printers/${printer}/print`)
      .json(data)
      .post().res
  }
}

export const CheckInStoreContext = createContext(
  new CheckInStore(placeholderWretch),
)
