import { BrowserWindow, app } from "electron"
import { makeApp } from "./api"

let mainWindow: BrowserWindow

app.whenReady().then(() => {
  const wnd = new BrowserWindow({
    title: "Print Daemon",
    webPreferences: {
      preload: RENDERER_PRELOAD_WEBPACK_ENTRY,
    },
  })
  mainWindow = wnd

  // wnd.loadURL(RENDERER_WEBPACK_ENTRY).then(() => {
  wnd.loadFile("index.html").then(() => {
    const app = makeApp(wnd.webContents)
    const server = app.listen(8090)
    wnd.on("close", () => {
      server.close()
    })
  })

  wnd.on("close", () => {
    app.quit()
  })
})
