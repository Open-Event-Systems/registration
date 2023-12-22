import { BadgeData, createClient } from "@open-event-systems/badge-lib"
import { ipcRenderer } from "electron"

const client = createClient(window)

ipcRenderer.on("format", (_e, id: string, data: BadgeData) => {
  // window.setTimeout(() => {
  //   ipcRenderer.send("format", id)
  // }, 1000)
  client
    .format(data)
    .then(() => {
      console.log("Format")
      ipcRenderer.send("format", id)
    })
    .catch((err: Error) => {
      ipcRenderer.send("format", id, err)
    })
})
