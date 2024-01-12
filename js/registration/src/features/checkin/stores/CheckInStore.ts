import { defaultQueryClient, placeholderWretch } from "#src/config/api"
import { createQueueAPI } from "#src/features/queue/api"
import { QueueAPI, QueueItem, StationInfo } from "#src/features/queue/types"
import { QueryClient } from "@tanstack/react-query"
import { makeAutoObservable, reaction, runInAction } from "mobx"
import { createContext } from "react"

export class CheckInStore {
  stationId: string | null = null
  stationInfo: StationInfo | null = null
  queueItems: QueueItem[] = []

  constructor(
    private queryClient: QueryClient,
    private queueAPI: QueueAPI,
  ) {
    makeAutoObservable(this)

    let interval: number | null = null

    reaction(
      () => this.stationId,
      (cur) => {
        if (cur) {
          this.loadStation(cur)
        } else {
          this.stationInfo = null
          this.queueItems = []
        }
      },
    )

    reaction(
      () => this.stationInfo,
      (cur) => {
        if (interval) {
          window.clearInterval(interval)
          interval = null
        }

        if (cur) {
          this.update(cur.group_id, cur.id)
          interval = window.setInterval(() => {
            this.update(cur.group_id, cur.id)
          }, 5000)
        }
      },
    )
  }

  private async loadStation(stationId: string) {
    const res = await this.queryClient.fetchQuery(
      this.queueAPI.getStation(stationId),
    )
    runInAction(() => {
      if (this.stationId == stationId) {
        this.stationInfo = res
      }
    })
  }

  private async update(groupId: string, stationId: string) {
    const queueItems = await this.queryClient.fetchQuery(
      this.queueAPI.listQueueItems(groupId, stationId),
    )
    runInAction(() => {
      if (this.stationInfo?.id == stationId) {
        this.queueItems = queueItems
      }
    })
  }
}

export const CheckInStoreContext = createContext(
  new CheckInStore(
    defaultQueryClient,
    createQueueAPI(placeholderWretch, defaultQueryClient),
  ),
)
