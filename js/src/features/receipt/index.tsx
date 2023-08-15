import { ReceiptPage } from "#src/features/receipt/routes.js"
import { createRoot } from "react-dom/client"

import "#src/features/receipt/styles.css"

const main = document.getElementById("main")
if (main) {
  const root = createRoot(main)
  root.render(<ReceiptPage />)
}
