import { BadgeData } from "@open-event-systems/badge-lib"
import express from "express"
import { Printer, getPrinters, printSystem } from "./print"
import { IpcMainEvent, WebContents, ipcMain } from "electron"

export const makeApp = (webContents: WebContents): express.Express => {
  const app = express()
  app.use(express.json())
  app.use((_req, res, next) => {
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    res.setHeader("Access-Control-Allow-Origin", "*")
    res.setHeader("Access-Control-Expose-Headers", "Content-Type")
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization")
    res.setHeader("Access-Control-Max-Age", "3600")
    next()
  })

  app.get("/printers", async (_req, res) => {
    const printers = await getPrinters(webContents)
    res.send(printers)
  })

  app.options("/printers/:printerId/print", (_req, res) => {
    res.status(204).send()
  })

  let curPrintPromise: Promise<void> = Promise.resolve()

  app.post("/printers/:printerId/print", async (req, res) => {
    const printerId = req.params.printerId
    const body = req.body as BadgeData

    let printer: Printer | undefined

    if (printerId != "default") {
      const printers = await getPrinters(webContents)
      printer = printers.find((p) => p.id == printerId)
      if (!printer) {
        res.status(404).send()
        return
      }
    }

    const id = String(new Date().getTime())

    curPrintPromise = curPrintPromise
      .catch()
      .then(
        () =>
          new Promise<void>((resolve, reject) => {
            const handler = (
              _e: IpcMainEvent,
              replyId: string,
              error?: Error,
            ) => {
              if (replyId !== id) {
                return
              }

              ipcMain.off("format", handler)

              if (error) {
                reject(error)
              } else {
                resolve()
              }
            }

            ipcMain.on("format", handler)
            webContents.send("format", id, body)
          }),
      )
      .then(() => {
        return printSystem(webContents, printer?.id)
      })

    return curPrintPromise
      .then(() => {
        res.status(204).send()
      })
      .catch((err: Error) => {
        res.status(500).send({ detail: err.message })
      })
  })

  return app
}
