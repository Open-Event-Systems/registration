import { WebContents } from "electron"
import child_process from "child_process"
import { temporaryFileTask } from "tempy"
import fs from "fs/promises"

export type Printer = {
  id: string
  name: string
}

/**
 * Get the available printers.
 * @param webContents - the webContents instance
 * @returns the available printers.
 */
export const getPrinters = async (
  webContents: WebContents,
): Promise<Printer[]> => {
  const printers = await webContents.getPrintersAsync()
  return printers.map((p) => ({ id: p.name, name: p.displayName }))
}

/**
 * Print the given WebContents via LP.
 * @param webContents - the WebContents
 * @param printerId - the printer ID
 */
export const print = async (webContents: WebContents, printerId?: string) => {
  return temporaryFileTask(async (tmpPath) => {
    const pdfData = await renderPDF(webContents)
    const f = await fs.open(tmpPath, "w")
    await f.write(pdfData)
    await f.close()
    await fs.copyFile(tmpPath, "output.pdf")
    await printLP(tmpPath, printerId)
  })
}

/**
 * Submit a print job via `lp`.
 * @param filePath - the file path
 * @param printerId - the printer ID
 */
export const printLP = async (
  filePath: string,
  printerId?: string,
): Promise<void> => {
  const args = printerId ? ["-d", printerId, filePath] : [filePath]
  const proc = child_process.spawn("lp", args)
  return new Promise<void>((resolve, reject) => {
    proc.once("error", (e) => {
      reject(e)
    })
    proc.once("exit", (code) => {
      if (code !== 0) {
        reject(new Error(`lp exited with ${code}`))
      } else {
        resolve()
      }
    })
  })
}

/**
 * Render web contents as PDF.
 * @param webContents - the WebContents to render
 * @returns a Promise of a Buffer of PDF data
 */
export const renderPDF = async (webContents: WebContents): Promise<Buffer> => {
  return await webContents.printToPDF({
    printBackground: true,
    preferCSSPageSize: true,
    margins: { marginType: "default" },
  })
}
