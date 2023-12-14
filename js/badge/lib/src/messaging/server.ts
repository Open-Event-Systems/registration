import {
  FormatHandler,
  FormatRequest,
  FormatResponse,
  PrintHandler,
  PrintRequest,
  PrintResponse,
  Server,
} from "../types.js"

class ServerImpl {
  private handler: (e: MessageEvent) => void

  constructor(
    private allowedOrigins: string[] | "*",
    private formatHandler: FormatHandler,
    private printHandler: PrintHandler,
  ) {
    this.handler = (e) => {
      if (
        !e.source ||
        (this.allowedOrigins != "*" && !this.allowedOrigins.includes(e.origin))
      ) {
        return
      }

      if (e.data && typeof e.data == "object" && "type" in e.data) {
        if (e.data.type == "format") {
          this.format(e.source, e.data)
        } else if (e.data.type == "print") {
          this.print(e.source, e.data)
        }
      }
    }

    window.addEventListener("message", this.handler)
  }

  private async format(sender: MessageEventSource, request: FormatRequest) {
    await this.formatHandler(request.data)
    sender.postMessage({
      id: request.id,
    } as FormatResponse)
  }

  private async print(sender: MessageEventSource, request: PrintRequest) {
    await this.printHandler(request.data)
    sender.postMessage({
      id: request.id,
    } as PrintResponse)
  }

  dispose() {
    window.removeEventListener("message", this.handler)
  }
}

export type GetServerOptions = {
  format: FormatHandler
  print: PrintHandler
  allowedOrigins?: string[] | "*"
}

/**
 * Start a badge API server.
 */
export const createServer = (options: GetServerOptions): Server => {
  const { format, print, allowedOrigins = "*" } = options
  return new ServerImpl(allowedOrigins, format, print)
}
