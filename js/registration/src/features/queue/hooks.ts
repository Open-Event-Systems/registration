import { defaultQueryClient, placeholderWretch } from "#src/config/api"
import { createQueueAPI } from "#src/features/queue/api"
import { QueueAPI } from "#src/features/queue/types"
import { createContext, useContext } from "react"

export const QueueAPIContext = createContext(
  createQueueAPI(placeholderWretch, defaultQueryClient),
)

export const useQueueAPI = (): QueueAPI => useContext(QueueAPIContext)
