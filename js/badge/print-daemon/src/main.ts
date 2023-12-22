import { BrowserWindow, app, dialog } from "electron"
import { makeApp } from "./api"

app.whenReady().then(() => {
  const wnd = new BrowserWindow({
    title: "Print Daemon",
    webPreferences: {
      preload: RENDERER_PRELOAD_WEBPACK_ENTRY,
    },
  })

  const badgeUrl = process.env.BADGE_URL || "badge.html"

  wnd
    .loadURL(badgeUrl)
    .catch((err: Error) => {
      dialog.showErrorBox(
        "Badge File Error",
        `Could not load the badge file "${badgeUrl}": ${err.message}`,
      )
      app.quit()
      throw err
    })
    .then(() => {
      const app = makeApp(wnd.webContents)
      const server = app.listen(8631)
      wnd.on("close", () => {
        server.close()
      })
    })

  wnd.on("close", () => {
    app.quit()
  })
})
