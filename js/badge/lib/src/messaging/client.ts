import { BadgeData, Client, FormatRequest, PrintRequest } from "../types.js"

class ClientImpl {
  private id = 1

  constructor(
    private target: Window,
    private targetOrigin: string,
  ) {}

  async format(data: BadgeData): Promise<void> {
    const id = this.getId()
    const wait = this.wait(id)
    this.target.postMessage({
      type: "format",
      id: id,
      data: data,
    } as FormatRequest)
    return wait
  }

  async print(data: BadgeData): Promise<void> {
    const id = this.getId()
    const wait = this.wait(id)
    this.target.postMessage({
      type: "print",
      id: id,
      data: data,
    } as PrintRequest)
    return wait
  }

  private getId(): string {
    return `${this.id++}`
  }

  private wait(id: string): Promise<void> {
    const promise = new Promise<void>((resolve) => {
      const handler = (e: MessageEvent) => {
        if (e.origin != this.targetOrigin && this.targetOrigin != "*") {
          return
        }

        if (
          e.data &&
          typeof e.data == "object" &&
          "id" in e.data &&
          e.data.id == id
        ) {
          window.removeEventListener("message", handler)
          resolve()
        }
      }

      window.addEventListener("message", handler)
    })

    return promise
  }
}

/**
 * Create a badge message API client.
 */
export const createClient = (window: Window, targetOrigin = "*"): Client => {
  return new ClientImpl(window, targetOrigin)
}
