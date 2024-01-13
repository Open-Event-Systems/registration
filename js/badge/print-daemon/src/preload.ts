import { BadgeData, createClient } from "@open-event-systems/badge-lib"
import { ipcRenderer } from "electron"

const client = createClient(window)

ipcRenderer.on("format", (_e, id: string, data: BadgeData) => {
  client
    .format(data)
    .then(() => new Promise<void>((r) => window.setTimeout(r, 200)))
    .then(() => {
      ipcRenderer.send("format", id)
    })
    .catch((err: Error) => {
      ipcRenderer.send("format", id, err)
    })
})
