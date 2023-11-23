import { Event, EventAPI } from "#src/features/event/types"
import { makeAutoObservable } from "mobx"

export class EventStore {
  private events = new Map<string, Event>()

  constructor(private api: EventAPI) {
    makeAutoObservable(this)
  }

  [Symbol.iterator](): Iterator<Event> {
    return this.events.values()
  }

  getEvent(id: string): Event | undefined {
    return this.events.get(id)
  }

  async load(): Promise<Map<string, Event>> {
    const res = await this.api.list()
    for (const event of res) {
      this.events.set(event.id, event)
    }
    return this.events
  }
}
